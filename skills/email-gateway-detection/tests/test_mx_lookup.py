"""Offline tests: no network needed. Run with `python -m pytest tests/`."""
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import mx_lookup as m  # noqa: E402

GMAP = m.load_map()


class Fake:
    def __init__(self, mx=None, txt=None, exc=None):
        self._mx, self._txt, self._exc = mx or [], txt or [], exc

    def mx(self, d):
        if self._exc:
            raise self._exc
        return self._mx

    def txt(self, d):
        return self._txt


def run(**kw):
    return m.classify("acme.com", Fake(**kw), GMAP)


def test_proofpoint_behind_m365_via_spf():
    r = run(mx=[(10, "mx0a-001.pphosted.com")], txt=["v=spf1 include:spf.protection.outlook.com -all"])
    assert (r["seg_vendor"], r["mailbox_provider"], r["mailbox_source"]) == ("proofpoint", "microsoft", "dns_spf")


def test_mimecast():
    assert run(mx=[(10, "eu-smtp-inbound-1.mimecast.com")])["seg_vendor"] == "mimecast"


def test_direct_google_no_gateway():
    r = run(mx=[(1, "aspmx.l.google.com")])
    assert (r["seg_vendor"], r["mailbox_provider"], r["mailbox_source"]) == ("none", "google", "dns_mx")


def test_cisco_ironport():
    assert run(mx=[(10, "mx1.hc1234-56.iphmx.com")])["seg_vendor"] == "cisco"


def test_unknown_self_hosted_goes_to_stage2():
    r = run(mx=[(10, "mail.acme.com")])
    assert (r["seg_vendor"], r["mailbox_provider"]) == ("unknown", "other")


def test_suffix_does_not_overmatch():
    # notmimecast.com must not be read as mimecast
    assert run(mx=[(10, "mx.notmimecast.com")])["seg_vendor"] == "unknown"


def test_null_mx():
    assert run(mx=[(0, "")])["seg_status"] == "null_mx"


def test_nxdomain():
    r = run(exc=m.DnsError("nxdomain"))
    assert (r["seg_status"], r["inbox_tier"]) == ("nxdomain", "")


def test_domain_parsing():
    assert m.domain_of({"email": "Jane@WWW.Acme.com"}) == "acme.com"


def test_dns_tools_from_txt_tokens_and_spf():
    r = run(mx=[(1, "aspmx.l.google.com")], txt=[
        "google-site-verification=abc", "ms=ms123", "docusign=1", "atlassian-domain-verification=a",
        "atlassian-domain-verification=b", "00d36000000kfwn=1tbpm0000000sqj",
        "v=spf1 include:_spf.google.com include:mail.zendesk.com include:sendgrid.net ~all"])
    assert r["dns_tools"] == "atlassian|docusign|google_search_console|microsoft_365|salesforce|sendgrid|zendesk"
    assert run(mx=[(1, "aspmx.l.google.com")])["dns_tools"] == ""


def test_cache_entry_without_dns_tools_is_refreshed():
    rows = [{"domain": "acme.com"}]
    old = {"seg_vendor": "none", "mailbox_provider": "google", "seg_source": "dns", "mailbox_source": "dns_mx",
           "seg_status": "ok", "mx_hosts": "aspmx.l.google.com", "seg_checked_at": "2099-01-01T00:00:00+00:00",
           "seg_conflict": "false"}
    cache = {"acme.com": dict(old)}
    client = Fake(mx=[(1, "aspmx.l.google.com")], txt=["docusign=1"])
    assert m.tag_rows(rows, cache, client=client, gmap=GMAP) == 1
    assert rows[0]["dns_tools"] == cache["acme.com"]["dns_tools"] == "docusign"


# --- inbox_tier and the ramp gate ---

def test_inbox_tier_per_class():
    assert run(mx=[(1, "aspmx.l.google.com")])["inbox_tier"] == "1"
    assert run(mx=[(0, "acme-com.mail.protection.outlook.com")])["inbox_tier"] == "2"
    assert run(mx=[(10, "mx.zoho.com")])["inbox_tier"] == "3"
    assert run(mx=[(10, "mail.acme.com")])["inbox_tier"] == "3"  # unknown / self-hosted
    # M365 behind Proofpoint is tier 4: the wall decides, not what is behind it
    r = run(mx=[(10, "mx0a-001.pphosted.com")], txt=["v=spf1 include:spf.protection.outlook.com -all"])
    assert (r["inbox_tier"], r["mailbox_provider"]) == ("4", "microsoft")


def test_split_by_tier_holds_above_max_and_keeps_bad_status_rows():
    rows = [{"inbox_tier": "1"}, {"inbox_tier": "2"}, {"inbox_tier": "4"}, {"inbox_tier": ""}]
    send, held = m.split_by_tier(rows, 1)
    assert [r["inbox_tier"] for r in send] == ["1", ""] and [r["inbox_tier"] for r in held] == ["2", "4"]
    send, held = m.split_by_tier(rows, 4)
    assert len(send) == 4 and held == []


def test_cached_entry_without_inbox_tier_gets_it_without_a_lookup():
    rows = [{"domain": "acme.com"}]
    cache = {"acme.com": {"seg_vendor": "none", "mailbox_provider": "google", "seg_source": "dns",
                          "mailbox_source": "dns_mx", "seg_status": "ok", "mx_hosts": "aspmx.l.google.com",
                          "seg_checked_at": "2099-01-01T00:00:00+00:00", "seg_conflict": "false", "dns_tools": ""}}
    assert m.tag_rows(rows, cache, client=Fake(), gmap=GMAP) == 0
    assert rows[0]["inbox_tier"] == cache["acme.com"]["inbox_tier"] == "1"


def test_main_writes_held_file(tmp_path, monkeypatch):
    class FakeDns:
        def mx(self, d):
            return [(1, "aspmx.l.google.com")] if d == "g.com" else [(10, "eu-smtp-inbound-1.mimecast.com")]

        def txt(self, d):
            return []
    monkeypatch.setattr(m, "make_client", lambda *a, **k: FakeDns())
    src = tmp_path / "in.csv"
    src.write_text("domain\ng.com\nmc.com\n")
    out = tmp_path / "out.csv"
    assert m.main(["--in", str(src), "--out", str(out), "--cache", str(tmp_path / "c.json"), "--max-tier", "1"]) == 0
    import csv
    assert [r["domain"] for r in csv.DictReader(open(out))] == ["g.com"]
    held = list(csv.DictReader(open(tmp_path / "out.held.csv")))
    assert [(r["domain"], r["inbox_tier"]) for r in held] == [("mc.com", "4")]


# --- DNS-over-HTTPS client, offline ---

GOOGLE = "https://dns.google/"
CF = "https://cloudflare-dns.com/"


def doh(responses):
    """responses: list of dicts or exceptions, consumed in call order; also records the urls hit."""
    calls = []

    def fetch(url):
        calls.append(url)
        r = responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r
    return m.DohClient(fetch=fetch), calls


def test_doh_mx_parses_google_json_shape():
    body = {"Status": 0, "Answer": [
        {"name": "acme.com.", "type": 5, "TTL": 300, "data": "alias.acme.com."},  # CNAME noise is ignored
        {"name": "acme.com.", "type": 15, "TTL": 300, "data": "20 mx0b-001.pphosted.com."},
        {"name": "acme.com.", "type": 15, "TTL": 300, "data": "10 MX0A-001.pphosted.com."}]}
    c, calls = doh([body])
    assert c.mx("acme.com") == [(10, "mx0a-001.pphosted.com"), (20, "mx0b-001.pphosted.com")]
    assert calls == ["https://dns.google/resolve?name=acme.com&type=MX"]


def test_doh_txt_joins_quoted_segments_and_lowercases():
    body = {"Status": 0, "Answer": [
        {"type": 16, "data": "\"v=spf1 include:_spf.google.com\" \"include:sendgrid.net ~all\""},
        {"type": 16, "data": "\"DocuSign=abc\""},
        {"type": 16, "data": "\"MS=ms123\"\"456\""}]}
    c, _ = doh([body])
    assert c.txt("acme.com") == ["v=spf1 include:_spf.google.cominclude:sendgrid.net ~all", "docusign=abc", "ms=ms123456"]


def test_doh_nxdomain_is_final_no_fallback():
    c, calls = doh([{"Status": 3}])
    try:
        c.mx("nope.invalid")
        assert False
    except m.DnsError as e:
        assert e.status == "nxdomain"
    assert len(calls) == 1


def test_doh_no_answer_is_no_mx_and_null_mx_passes_through():
    c, _ = doh([{"Status": 0, "Answer": []}])
    try:
        c.mx("acme.com")
        assert False
    except m.DnsError as e:
        assert e.status == "no_mx"
    c, _ = doh([{"Status": 0, "Answer": [{"type": 15, "data": "0 ."}]}])
    assert c.mx("acme.com") == [(0, "")]  # classify() turns this into null_mx


def test_doh_falls_back_to_cloudflare_on_http_error_and_servfail():
    http429 = urllib.error.HTTPError("u", 429, "rate limited", {}, None)
    c, calls = doh([http429, {"Status": 0, "Answer": [{"type": 15, "data": "1 aspmx.l.google.com."}]}])
    assert c.mx("acme.com") == [(1, "aspmx.l.google.com")]
    assert calls[0].startswith(GOOGLE) and calls[1].startswith(CF)
    c, calls = doh([{"Status": 2}, {"Status": 2}])
    try:
        c.mx("acme.com")
        assert False
    except m.DnsError as e:
        assert e.status == "servfail"
    assert len(calls) == 2


def test_doh_timeout_on_both_is_timeout_not_cached():
    c, _ = doh([TimeoutError(), urllib.error.URLError("timed out")])
    try:
        c.mx("acme.com")
        assert False
    except m.DnsError as e:
        assert e.status == "timeout"


def test_doh_client_classifies_end_to_end():
    mx = {"Status": 0, "Answer": [{"type": 15, "data": "10 eu-smtp-inbound-1.mimecast.com."}]}
    txt = {"Status": 0, "Answer": [{"type": 16, "data": "\"v=spf1 include:spf.protection.outlook.com -all\""}]}
    c, _ = doh([mx, txt])
    r = m.classify("acme.com", c, GMAP)
    assert (r["seg_vendor"], r["mailbox_provider"], r["mailbox_source"], r["inbox_tier"]) == \
        ("mimecast", "microsoft", "dns_spf", "4")


def test_make_client_doh_needs_no_dnspython(monkeypatch):
    import builtins
    real = builtins.__import__

    def no_dns(name, *a, **k):
        if name.startswith("dns"):
            raise ImportError(name)
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_dns)
    assert isinstance(m.make_client("doh"), m.DohClient)
    assert isinstance(m.make_client("auto"), m.DohClient)  # auto degrades to doh when dnspython is missing


def test_preflight_aborts_when_resolver_is_walled():
    import pytest
    with pytest.raises(SystemExit, match="preflight failed: gmail.com -> nxdomain"):
        m.preflight(Fake(exc=m.DnsError("nxdomain")))
    m.preflight(Fake(mx=[(5, "gmail-smtp-in.l.google.com")]))  # healthy resolver: no exception
