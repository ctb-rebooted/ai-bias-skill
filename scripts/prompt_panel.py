#!/usr/bin/env python3
"""Bias Hunter — the standard retail-investor prompt panel (8 CMCI prompts, ko/en/ja) and a compare tool.

    python prompt_panel.py --lang ko                     # print the 8 CMCI prompts in Korean (the measured panel)
    python prompt_panel.py --lang ja --scenarios personas
    python prompt_panel.py --scenarios list              # list scenario dimensions
    python prompt_panel.py --compare "042700,005930,000660"   # Jaccard vs today's public consensus, herd vs contrarian
    python prompt_panel.py --file prompts.json --feed-file latest.json --compare names.txt

Stdlib only. Run the prompts against your own model (5 repeats, search on), take the first five names it lists,
then --compare. The compare output is a similarity measurement, not a judgement of which list is "right".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

PROMPTS_URL = "https://ai-bias.docenty.ai/free/prompts.json"
FEED_URL = "https://ai-bias.docenty.ai/free/latest.json"
UPGRADE_URL = "https://ai-bias.docenty.ai/#inquiry?utm_source=skill&utm_medium=cli"
LANGS = ("ko", "en", "ja")
TIMEOUT = 10
DISCLAIMER = "Measurement of answer overlap, not investment advice. 측정치이지 투자 조언이 아닙니다."


def _fetch(url: str | None, path: str | None, what: str) -> dict:
    try:
        if path:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        req = urllib.request.Request(url, headers={"User-Agent": "ai-bias-skill/0.2"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.load(r)
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as e:
        print(f"ai-bias: {what} unreachable or invalid ({path or url}): {e}", file=sys.stderr)
        print("Retry later, or pass --file / --feed-file with a saved copy.", file=sys.stderr)
        sys.exit(2)


def print_prompts(p: dict, lang: str, dimension: str | None) -> None:
    ver = p.get("version") or {}
    print(f"Bias Hunter prompt panel · catalog_version={ver.get('catalog_version')} · lang={lang}"
          + ("  (ja = machine translated, not part of the measured panel)" if lang == "ja" else ""))
    print(f"CMCI cells: {p.get('cmci_cells', '')} · rule: {p.get('cmci_rule', '')}")
    print()
    print("CMCI prompts (these 8 define the consensus index):")
    for q in p.get("prompts", []):
        text = q.get(lang) or q.get("en") or q.get("ko")
        miss = "" if q.get(lang) else f"  [no {lang}; showing fallback]"
        print(f"  {q['id']}  {text}{miss}")
    if dimension:
        sc = p.get("scenarios") or {}
        if dimension == "list":
            print("\nScenario dimensions (exploratory, never in CMCI): " + ", ".join(f"{k} ({len(v)})" for k, v in sc.items()))
            return
        items = sc.get(dimension)
        if not items:
            print(f"\nUnknown scenario dimension '{dimension}'. Use --scenarios list.", file=sys.stderr)
            sys.exit(1)
        print(f"\nScenario prompts · {dimension} (scenario_version={ver.get('scenario_version')}, exploratory):")
        for q in items:
            text = q.get(lang) or q.get("en") or q.get("ko")
            miss = "" if q.get(lang) else f"  [no {lang}; showing {'en' if q.get('en') else 'ko'}]"
            print(f"  {q['id']}  {text}{miss}")
    print()
    print("How to use: ask your model each string verbatim, 5 repeats, web search on. Record the first five names per answer.")
    print("Then: python prompt_panel.py --compare \"name1,name2,...\"  (or a file / '-' for stdin)")


def parse_names(spec: str) -> list[str]:
    if spec == "-":
        raw = sys.stdin.read()
    elif os.path.exists(spec):
        with open(spec, encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = spec
    out: list[str] = []
    for tok in raw.replace("\n", ",").replace(";", ",").split(","):
        t = tok.strip().strip("-•*").strip()
        if t and t not in out:
            out.append(t)
    return out


def jaccard(a: set[str], b: set[str]) -> float | None:
    if not a and not b:
        return None
    return len(a & b) / len(a | b)


def compare(names: list[str], feed: dict) -> dict:
    """Map pasted names to asset_id via feed names (exact id or case-insensitive name), then classify vs consensus."""
    rows = feed.get("names") or []
    by_id = {str(r["asset_id"]): r for r in rows}
    by_name = {str(r.get("name", "")).lower(): r for r in rows}
    resolved, unknown = {}, []
    for n in names:
        r = by_id.get(n) or by_name.get(n.lower())
        if r is None:
            unknown.append(n)
        else:
            resolved[n] = str(r["asset_id"])
    cons = feed.get("consensus") or {}
    top = {str(t["asset_id"]) for t in cons.get("top") or []}
    union = set(cons.get("union") or [])
    mine = set(resolved.values())
    herd = sorted(mine & top)
    single = sorted((mine & union) - top)
    contrarian = sorted(mine - union)
    crowded = sorted(a for a in mine if by_id.get(a, {}).get("crowded"))
    return {"as_of": feed.get("as_of"), "label": feed.get("label"), "input": names, "unknown": unknown,
            "jaccard_vs_consensus_top": jaccard(mine, top), "jaccard_vs_any_model_top5": jaccard(mine, union),
            "herd": herd, "single_model_overlap": single, "contrarian": contrarian, "crowded_in_input": crowded,
            "consensus_top": sorted(top)}


def print_compare(c: dict) -> None:
    f = lambda x: "—" if x is None else f"{x:.3f}"
    print(f"Compare vs public consensus · as_of {c['as_of']} [{c['label']}]")
    print(f"  your list ({len(c['input'])}): {', '.join(c['input'])}")
    if c["unknown"]:
        print(f"  not in public panel (unmapped, excluded from Jaccard): {', '.join(c['unknown'])}")
    print(f"  consensus top (>=3 models): {', '.join(c['consensus_top']) or 'none'}")
    print(f"  Jaccard vs consensus top:   {f(c['jaccard_vs_consensus_top'])}")
    print(f"  Jaccard vs any-model top-5: {f(c['jaccard_vs_any_model_top5'])}")
    print(f"  herd (in >=3-model consensus):        {', '.join(c['herd']) or 'none'}")
    print(f"  single-model overlap (1-2 models):     {', '.join(c['single_model_overlap']) or 'none'}")
    print(f"  contrarian (no public model top-5):    {', '.join(c['contrarian']) or 'none'}")
    print(f"  crowded (CMCI >= 0.5) among your names: {', '.join(c['crowded_in_input']) or 'none'}")
    print()
    print(DISCLAIMER + f" Public feed is delayed (D+1); same-morning consensus: {UPGRADE_URL}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default=PROMPTS_URL)
    ap.add_argument("--file", default=None, help="saved prompts.json")
    ap.add_argument("--lang", default="ko", choices=LANGS)
    ap.add_argument("--scenarios", default=None, metavar="DIMENSION", help="also print scenario prompts of a dimension, or 'list'")
    ap.add_argument("--compare", default=None, metavar="NAMES", help="comma list, file path, or '-' (stdin) of names/asset_ids")
    ap.add_argument("--feed-url", default=FEED_URL)
    ap.add_argument("--feed-file", default=None, help="saved latest.json for --compare")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.compare is not None:
        feed = _fetch(a.feed_url, a.feed_file, "feed")
        c = compare(parse_names(a.compare), feed)
        print(json.dumps(c, ensure_ascii=False, indent=1)) if a.json else print_compare(c)
        return 0
    p = _fetch(a.url, a.file, "prompt panel")
    if a.json:
        print(json.dumps(p, ensure_ascii=False, indent=1))
    else:
        print_prompts(p, a.lang, a.scenarios)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
