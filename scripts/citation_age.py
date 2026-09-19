#!/usr/bin/env python3
"""Bias Hunter — citation freshness: how old are the sources behind a search-enabled LLM answer?

    python citation_age.py --asof 2026-09-18 https://news.example.com/2026/09/17/article https://x.com/...
    cat urls.txt | python citation_age.py --asof 2026-09-18
    python citation_age.py --asof 2026-09-18 --json < urls.txt

Standalone copy of the URL-date heuristics used by the observatory (derived/citations.py); no network, deterministic.
Publication date is inferred from the URL path/query only. Hosts whose URLs carry no date (Naver news, YouTube, X)
are counted as undated and excluded from the age shares — the share_dated figure keeps that denominator honest.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

_PATTERNS = [
    re.compile(r"/(20\d{2})/(\d{1,2})/(\d{1,2})(?:/|$)"),             # /2026/09/18/
    re.compile(r"/(20\d{2})-(\d{2})-(\d{2})(?:/|-|_|$)"),             # /2026-09-18-slug
    re.compile(r"[?&](?:date|dt|d)=(20\d{2})(\d{2})(\d{2})"),          # ?date=20260918
    re.compile(r"/(20\d{2})(\d{2})(\d{2})(?:/|_|-|\d{4,}|$)"),         # /20260918/ or /202609181234567
    re.compile(r"[?&]date=(20\d{2})-(\d{2})-(\d{2})"),
]
_NO_DATE_HOSTS = ("n.news.naver.com", "news.naver.com", "finance.naver.com", "youtube.com", "youtu.be", "x.com", "twitter.com")


def published_date_from_url(url: str) -> dt.date | None:
    try:
        u = urlparse(url)
    except ValueError:
        return None
    host = (u.hostname or "").lower()
    if any(host == h or host.endswith("." + h) for h in _NO_DATE_HOSTS):
        return None
    target = (u.path or "") + ("?" + u.query if u.query else "")
    for rx in _PATTERNS:
        m = rx.search(target)
        if m:
            y, mo, d = (int(g) for g in m.groups())
            try:
                cand = dt.date(y, mo, d)
            except ValueError:
                continue
            if dt.date(2015, 1, 1) <= cand <= dt.date(2100, 1, 1):
                return cand
    return None


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def analyse(asof: dt.date, urls: list[str], top_k: int = 5) -> dict:
    per_url, ages = [], []
    hosts: Counter[str] = Counter()
    for u in urls:
        h = host_of(u)
        if h:
            hosts[h] += 1
        p = published_date_from_url(u)
        age = max(0, (asof - p).days) if p else None
        if age is not None:
            ages.append(age)
        per_url.append({"url": u, "host": h, "published": p.isoformat() if p else None, "age_days": age})
    n, nd = len(urls), len(ages)
    s = sorted(ages)
    median = (s[nd // 2] if nd % 2 else (s[nd // 2 - 1] + s[nd // 2]) / 2) if nd else None
    total = sum(hosts.values())
    hhi = sum((c / total) ** 2 for c in hosts.values()) if total else None
    return {
        "as_of": asof.isoformat(), "n_urls": n, "n_dated": nd, "n_undated": n - nd,
        "share_dated": (nd / n) if n else None,
        "share_le_1d": (sum(a <= 1 for a in ages) / nd) if nd else None,
        "share_le_7d": (sum(a <= 7 for a in ages) / nd) if nd else None,
        "median_age_days": median,
        "hhi_source_concentration": hhi, "n_hosts": len(hosts), "top_hosts": hosts.most_common(top_k),
        "urls": per_url,
    }


def _f(x, nd=2) -> str:
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def render(r: dict) -> str:
    L = [f"Citation freshness · as_of {r['as_of']} · {r['n_urls']} URLs ({r['n_dated']} dated, {r['n_undated']} undated)"]
    for u in r["urls"]:
        age = f"{u['age_days']}d" if u["age_days"] is not None else "—"
        L.append(f"  {age:>5}  {u['published'] or '   undated'}  {u['host']:<28} {u['url'][:80]}")
    L += ["",
          f"  share dated (denominator transparency): {_f(r['share_dated'])}",
          f"  share <= 1 day old:  {_f(r['share_le_1d'])}   (same-morning news following)",
          f"  share <= 7 days old: {_f(r['share_le_7d'])}",
          f"  median age (days):   {_f(r['median_age_days'])}",
          f"  source concentration HHI: {_f(r['hhi_source_concentration'])} over {r['n_hosts']} hosts"
          + ("  (>= 0.5: single-source / echo-chamber flag)" if (r["hhi_source_concentration"] or 0) >= 0.5 else ""),
          "  top hosts: " + (", ".join(f"{h} x{c}" for h, c in r["top_hosts"]) or "—"),
          "",
          ("Reading: a high <=1d share means the answer tracks that morning's news, not a durable view. "
           "Undated hosts are not 'old' — they are unknown. Measurement only, not advice.")]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("urls", nargs="*", help="URLs; if none, read one per line (or comma/space separated) from stdin")
    ap.add_argument("--asof", default=None, help="answer date YYYY-MM-DD (default: today UTC)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    urls = list(a.urls)
    if not urls and not sys.stdin.isatty():
        urls = [t for t in re.split(r"[\s,]+", sys.stdin.read()) if t]
    urls = [u for u in urls if u.startswith(("http://", "https://"))]
    if not urls:
        print("ai-bias: no http(s) URLs given", file=sys.stderr)
        return 1
    try:
        asof = dt.date.fromisoformat(a.asof) if a.asof else dt.datetime.now(dt.UTC).date()
    except ValueError:
        print("ai-bias: --asof must be YYYY-MM-DD", file=sys.stderr)
        return 1
    r = analyse(asof, urls)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
