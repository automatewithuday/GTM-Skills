#!/usr/bin/env python3
"""Stage 1 of the gateway waterfall: free DNS classification per domain.

Usage:
  python mx_lookup.py --in leads.csv --out tagged.csv [--cache .seg_cache.json] [--ttl-days 45]
                      [--resolver auto|system|doh] [--max-tier 1-4]

Input CSV needs an `email` or `domain` column. Output keeps every input column
and appends the schema fields documented in SKILL.md. One DNS lookup per unique
domain; results are cached so reruns and big lists stay cheap. The TXT record is read once per
domain: SPF for the mailbox provider, verification tokens and SPF includes for `dns_tools`.

Resolvers:
  system  dnspython against the machine's resolver (pip install dnspython).
  doh     DNS-over-HTTPS JSON, stdlib only: Google first, Cloudflare on failure. Use it where raw
          DNS is blocked or dnspython cannot be installed (serverless tasks, HTTP-only sandboxes).
  auto    system when dnspython imports, otherwise doh. The default.

Ramp gate: every row gets `inbox_tier` (1 google direct, 2 microsoft direct, 3 other, 4 behind a
gateway). `--max-tier N` writes rows above N to `<out>.held.csv` instead of `<out>`, so a fresh
sending domain can start on tier 1 only and unlock the rest as reply data comes in (SKILL.md).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAP_PATH = Path(__file__).resolve().parent.parent / "references" / "gateway-map.json"
FIELDS = [
    "domain", "seg_vendor", "mailbox_provider", "seg_source", "mailbox_source",
    "seg_status", "mx_hosts", "seg_checked_at", "seg_conflict", "dns_tools", "inbox_tier",
]
RESOLVERS = ("auto", "system", "doh")

# DNS-over-HTTPS JSON endpoints, tried in order. Both return the same shape:
# {"Status": rcode, "Answer": [{"name","type","TTL","data"}, ...]}. RFC 8427-style JSON, type is numeric.
DOH_ENDPOINTS = (
    ("google", "https://dns.google/resolve?name={name}&type={rtype}"),
    ("cloudflare", "https://cloudflare-dns.com/dns-query?name={name}&type={rtype}"),
)
RRTYPE = {"MX": 15, "TXT": 16}
RCODE_STATUS = {2: "servfail", 3: "nxdomain"}  # other non-zero rcodes are treated as servfail
_TXT_SEGMENT = re.compile(r'"((?:[^"\\]|\\.)*)"')


class DnsError(Exception):
    """A lookup that produced no usable answer. `status` is one of the seg_status values in errors.md."""

    def __init__(self, status: str):
        super().__init__(status)
        self.status = status


def load_map(path: Path = MAP_PATH) -> dict:
    return json.loads(path.read_text())


def _match_suffix(host: str, table: dict, key: str) -> str | None:
    """Return the table entry whose suffix matches host, longest suffix wins."""
    best, best_len = None, 0
    for name, entry in table.items():
        for suffix in entry[key]:
            if (host == suffix or host.endswith("." + suffix)) and len(suffix) > best_len:
                best, best_len = name, len(suffix)
    return best


def tools_of(txt: list[str], tools: dict) -> str:
    """Pipe-joined vendor slugs from TXT verification tokens and SPF includes (SKILL.md, dns_tools)."""
    found = {slug for t in txt for prefix, slug in tools["txt_prefixes"].items() if t.startswith(prefix)}
    spf = next((t for t in txt if t.startswith("v=spf1")), "")
    found |= {slug for needle, slug in tools["spf_includes"].items() if needle in spf}
    return "|".join(sorted(found))


class DnsClient:
    """System resolver through dnspython. Tests inject fakes with the same mx()/txt() shape."""

    def __init__(self, timeout: float = 4.0):
        import dns.exception  # imported here so `--resolver doh` runs without dnspython installed
        import dns.resolver
        self._dns, self._exc = dns.resolver, dns.exception
        self.r = dns.resolver.Resolver()
        self.r.lifetime = timeout

    def mx(self, domain: str) -> list[tuple[int, str]]:
        try:
            ans = self.r.resolve(domain, "MX")
        except self._dns.NXDOMAIN:
            raise DnsError("nxdomain")
        except self._dns.NoAnswer:
            raise DnsError("no_mx")  # RFC 5321 A-record fallback exists, but treat as unsendable
        except self._exc.Timeout:
            raise DnsError("timeout")  # retry later, do NOT cache
        except self._dns.NoNameservers:
            raise DnsError("servfail")
        return sorted((a.preference, str(a.exchange).rstrip(".").lower()) for a in ans)

    def txt(self, domain: str) -> list[str]:
        try:
            ans = self.r.resolve(domain, "TXT")
        except (self._dns.NoAnswer, self._dns.NXDOMAIN, self._exc.Timeout, self._dns.NoNameservers):
            return []
        return [b"".join(a.strings).decode(errors="ignore").lower() for a in ans]


def parse_txt_data(data: str) -> str:
    """DoH returns TXT rdata as quoted segments: '"v=spf1 a" "b"' or '"a""b"'. Join them, lowercase."""
    segments = _TXT_SEGMENT.findall(data)
    joined = "".join(segments) if segments else data
    return joined.replace('\\"', '"').lower()


class DohClient:
    """DNS-over-HTTPS JSON resolver, stdlib only. Same mx()/txt() contract as DnsClient.

    Google answers first; on a transport error, HTTP error or SERVFAIL the query is retried on
    Cloudflare. NXDOMAIN is final on the first answer. `fetch(url) -> dict` is injectable for tests.
    """

    def __init__(self, timeout: float = 4.0, fetch=None, endpoints=DOH_ENDPOINTS):
        self.timeout = timeout
        self.endpoints = endpoints
        self.fetch = fetch or self._fetch

    def _fetch(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"accept": "application/dns-json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read())

    def _query(self, domain: str, rtype: str) -> list[str]:
        """rdata strings of the requested type, in answer order. Raises DnsError on nxdomain/servfail/timeout."""
        timed_out = False
        for _, tmpl in self.endpoints:
            url = tmpl.format(name=urllib.parse.quote(domain), rtype=rtype)
            try:
                body = self.fetch(url)
            except TimeoutError:
                timed_out = True
                continue
            except urllib.error.URLError as e:  # HTTPError is a URLError: 429/5xx fall through to the next endpoint
                timed_out = timed_out or "timed out" in str(e.reason).lower()
                continue
            except (OSError, ValueError):  # connection reset, non-JSON body
                continue
            status = body.get("Status")
            if status == 0:
                return [a["data"] for a in body.get("Answer") or [] if a.get("type") == RRTYPE[rtype]]
            if status == 3:
                raise DnsError("nxdomain")
            # SERVFAIL or another rcode: a second resolver may still answer
        raise DnsError("timeout" if timed_out else "servfail")

    def mx(self, domain: str) -> list[tuple[int, str]]:
        records = self._query(domain, "MX")
        if not records:
            raise DnsError("no_mx")
        out = []
        for data in records:
            pref, _, host = data.strip().partition(" ")
            out.append((int(pref), host.strip().rstrip(".").lower()))
        return sorted(out)

    def txt(self, domain: str) -> list[str]:
        try:
            return [parse_txt_data(d) for d in self._query(domain, "TXT")]
        except DnsError:
            return []


def make_client(resolver: str = "auto", timeout: float = 4.0):
    """Pick the Stage 1 resolver. `auto` is the system resolver when dnspython imports, else DoH."""
    if resolver not in RESOLVERS:
        raise ValueError(f"resolver must be one of {RESOLVERS}")
    if resolver == "doh":
        return DohClient(timeout)
    try:
        return DnsClient(timeout)
    except ImportError:
        if resolver == "system":
            raise SystemExit("resolver=system needs dnspython: pip install dnspython, or use --resolver doh")
        return DohClient(timeout)


CANARY = "gmail.com"  # has had MX records for two decades; if this fails the resolver is broken, not the domain


def preflight(client, canary: str = CANARY) -> None:
    """Abort before tagging anything when the resolver cannot see DNS at all.

    A walled or misconfigured resolver answers NXDOMAIN/SERVFAIL for every name. Without this check
    those answers would be cached as 'drop this lead' for thousands of good domains.
    """
    try:
        client.mx(canary)
    except DnsError as e:
        raise SystemExit(f"resolver preflight failed: {canary} -> {e.status}. DNS is not reachable from here; "
                         "nothing was written. Try --resolver doh, or run from a machine with DNS access.")


def tier_of(row: dict) -> str:
    """Inbox difficulty tier, derived from seg_vendor and mailbox_provider. Empty when seg_status is not ok.

    1 google direct, 2 microsoft direct, 3 other/zoho/self-hosted/unknown, 4 behind a named gateway.
    Microsoft is bimodal (default tenant vs aggressive Defender policies) so it is its own tier, not 1.
    """
    if row.get("seg_status") != "ok":
        return ""
    vendor, prov = row.get("seg_vendor", ""), row.get("mailbox_provider", "")
    if vendor == "none":
        return {"google": "1", "microsoft": "2"}.get(prov, "3")
    if vendor in ("", "unknown"):
        return "3"
    return "4"


def split_by_tier(rows: list[dict], max_tier: int) -> tuple[list[dict], list[dict]]:
    """(send, held). Rows with inbox_tier above max_tier are held; rows with no tier (bad DNS) stay in send
    so the existing drop rules in errors.md still apply to them downstream."""
    send, held = [], []
    for r in rows:
        t = r.get("inbox_tier", "")
        (held if t and int(t) > max_tier else send).append(r)
    return send, held


def classify(domain: str, client, gmap: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row = {"domain": domain, "seg_vendor": "", "mailbox_provider": "", "seg_source": "dns",
           "mailbox_source": "", "seg_status": "ok", "mx_hosts": "",
           "seg_checked_at": now, "seg_conflict": "false", "dns_tools": "", "inbox_tier": ""}
    try:
        mx = client.mx(domain)
    except DnsError as e:
        row["seg_status"] = e.status
        return row

    hosts = [h for _, h in mx]
    row["mx_hosts"] = "|".join(hosts)
    if hosts == [""] or hosts == ["."]:
        row["seg_status"] = "null_mx"  # RFC 7505: domain explicitly accepts no mail
        return row

    # Gateway: first host in preference order that matches wins.
    for h in hosts:
        vendor = _match_suffix(h, gmap["gateways"], "suffixes")
        if vendor:
            row["seg_vendor"] = vendor
            break

    # Mailbox provider: direct from MX when no gateway, else infer from SPF.
    if not row["seg_vendor"]:
        for h in hosts:
            prov = _match_suffix(h, gmap["mailbox_providers"], "mx_suffixes")
            if prov:
                row["mailbox_provider"], row["mailbox_source"] = prov, "dns_mx"
                row["seg_vendor"] = "none"
                break
    txt = client.txt(domain)  # one TXT query: SPF for the provider, tokens and includes for dns_tools
    if not row["mailbox_provider"]:
        spf = next((t for t in txt if t.startswith("v=spf1")), "")
        for prov, entry in gmap["mailbox_providers"].items():
            if any(f"include:{inc}" in spf for inc in entry["spf_includes"]):
                row["mailbox_provider"], row["mailbox_source"] = prov, "dns_spf"
                break
    if not row["mailbox_provider"]:
        row["mailbox_provider"] = "other"
    if not row["seg_vendor"]:
        row["seg_vendor"] = "unknown"  # self-hosted or unmapped host: send to Stage 2
    row["dns_tools"] = tools_of(txt, gmap["tools"])
    row["inbox_tier"] = tier_of(row)
    return row


def domain_of(rec: dict) -> str:
    raw = (rec.get("domain") or rec.get("email") or "").strip().lower()
    return raw.split("@")[-1].removeprefix("www.")


def tag_rows(rows: list[dict], cache: dict, ttl_days: int = 45, client=None, gmap: dict | None = None,
             resolver: str = "auto") -> int:
    """Stage 1 over a list of dict rows, in place. Fills `cache`. Returns number of DNS lookups made."""
    gmap = gmap or load_map()
    client = client or make_client(resolver)
    cutoff = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    looked_up = 0
    for rec in rows:
        d = domain_of(rec)
        hit = cache.get(d)
        # entries from before dns_tools existed are looked up once more so the column fills
        if not hit or "dns_tools" not in hit or datetime.fromisoformat(hit["seg_checked_at"]) < cutoff:
            hit = classify(d, client, gmap)
            looked_up += 1
            if hit["seg_status"] not in ("timeout", "servfail"):
                cache[d] = hit
        hit["inbox_tier"] = tier_of(hit)  # derived, so cache entries from before the field get it for free
        rec.update({k: v for k, v in hit.items() if k != "domain"})
        rec["domain"] = d
    return looked_up


def write_outputs(rows: list[dict], out: str, fields: list[str], max_tier: int) -> tuple[int, int]:
    """Write `out` and, when the gate holds anything, `<out>.held.csv` with the same columns. Returns counts."""
    send, held = split_by_tier(rows, max_tier)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(send)
    if held:
        held_path = Path(out).with_suffix(".held.csv")
        with open(held_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(held)
    return len(send), len(held)


def tier_summary(rows: list[dict], max_tier: int, held: int) -> str:
    counts = {t: sum(1 for r in rows if r.get("inbox_tier") == t) for t in "1234"}
    gate = f" max_tier={max_tier} held={held}" if max_tier < 4 else ""
    return "inbox_tier: " + " ".join(f"{t}={n}" for t, n in counts.items()) + gate


def add_common_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--resolver", default="auto", choices=RESOLVERS,
                    help="system (dnspython), doh (Google then Cloudflare over HTTPS, stdlib only) or auto")
    ap.add_argument("--max-tier", type=int, default=4, choices=[1, 2, 3, 4],
                    help="ramp gate: rows with inbox_tier above this go to <out>.held.csv (default 4 = no gate)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default=".seg_cache.json")
    ap.add_argument("--ttl-days", type=int, default=45)
    add_common_args(ap)
    a = ap.parse_args(argv)

    cache_path = Path(a.cache)
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    with open(a.inp, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("empty input", file=sys.stderr)
        return 1

    client = make_client(a.resolver)
    preflight(client)
    looked_up = tag_rows(rows, cache, a.ttl_days, client=client)

    cache_path.write_text(json.dumps(cache, indent=1))
    out_fields = list(dict.fromkeys(list(rows[0].keys()) + FIELDS))
    _, held = write_outputs(rows, a.out, out_fields, a.max_tier)

    unknown = sum(1 for r in rows if r["seg_vendor"] == "unknown")
    print(f"rows={len(rows)} dns_lookups={looked_up} unknown_for_stage2={unknown}", file=sys.stderr)
    print(tier_summary(rows, a.max_tier, held), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
