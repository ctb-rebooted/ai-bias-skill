#!/usr/bin/env python3
"""Bias Hunter — daily "what the models said" digest for Korean equities (free, delayed public feed).

    python latest.py                      # compact digest from https://ai-bias.docenty.ai/free/latest.json
    python latest.py --ticker 042700      # one name's row + fixed disclaimer
    python latest.py --json               # raw feed
    python latest.py --file latest.json   # offline / test

Stdlib only. Exit 2 when the feed is unreachable or malformed. Output is measurement, never a recommendation.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

FEED_URL = "https://ai-bias.docenty.ai/free/latest.json"
UPGRADE_URL = "https://ai-bias.docenty.ai#inquiry"
DISCLAIMER = ("Measurement of what public LLMs said on the data date shown, not investment advice. "
              "No recommendation, no target price. 측정치이지 투자 조언이 아닙니다.")
TIMEOUT = 10


def load_feed(url: str | None, path: str | None) -> dict:
    try:
        if path:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            req = urllib.request.Request(url or FEED_URL, headers={"User-Agent": "bias-hunter-skill/0.1"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = json.load(r)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        _fail(url or path, e)
    except json.JSONDecodeError as e:
        _fail(url or path, f"not JSON ({e})")
    if not isinstance(data, dict) or "as_of" not in data or "names" not in data:
        _fail(url or path, "missing as_of/names keys")
    return data


def _fail(src: str | None, err: object) -> None:
    print(f"bias-hunter: feed unreachable or invalid ({src}): {err}", file=sys.stderr)
    print("Retry later, or pass --file <saved latest.json>. Do not guess values.", file=sys.stderr)
    sys.exit(2)


def fmt(x, nd: int = 3) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def header(d: dict) -> list[str]:
    lab = d.get("label", "?")
    return [f"Bias Hunter digest · KR · as_of {d.get('as_of')} · [{lab}] · published {d.get('published_at', '?')}",
            f"derived_version={d.get('derived_version')} panel_version={d.get('panel_version')} window={d.get('window_days')}d"]


def digest(d: dict, top_n: int) -> str:
    L = header(d)
    L.append("")
    cons = d.get("consensus") or {}
    top = cons.get("top") or []
    L.append(f"Consensus (>= {cons.get('min_models', 3)} of {cons.get('n_models', '?')} models in top-5): "
             + (", ".join(f"{t['asset_id']}({t['n_models']})" for t in top) if top else "none"))
    L.append(f"Cross-model agreement (mean pairwise Jaccard): {fmt(cons.get('jaccard_mean'))}")
    L.append(f"New entrants vs {cons.get('prev_date', 'prev')}: {', '.join(cons.get('new_entrants') or []) or 'none'}"
             f" · dropped: {', '.join(cons.get('dropped') or []) or 'none'}")
    L.append("")
    names = sorted((n for n in d.get("names", []) if not n.get("placebo")), key=lambda n: (-(n.get("cmci") or 0), -(n.get("mention_rate") or 0)))
    L.append(f"Top names by CMCI (crowded = CMCI >= {d.get('crowded_threshold', 0.5)}):")
    L.append("  asset   name           cmci   mention  first5  models  days_in_consensus  flag")
    for n in names[:top_n]:
        L.append(f"  {n['asset_id']:<7} {str(n.get('name', ''))[:14]:<14} {fmt(n.get('cmci'), 2):>5}  {fmt(n.get('mention_rate'), 3):>7}  "
                 f"{n.get('n_first5', 0):>6}  {n.get('n_models_first5', 0):>6}  {fmt(n.get('days_since_first_entry')):>17}  "
                 f"{'CROWDED' if n.get('crowded') else ''}")
    L.append("")
    dis = d.get("disagreement") or []
    L.append("Disagreement (names only one model puts in its top-5): "
             + ("; ".join(f"{x['model']}: {', '.join(x['only'])}" for x in dis) if dis else "none"))
    L.append(f"Answer entropy (bits, pooled first-5 distribution): {fmt(d.get('entropy_bits'), 2)}")
    pf = d.get("placebo_floor") or {}
    L.append(f"Placebo noise floor (SD of mention_rate across {pf.get('n_placebo', 0)} placebo names): "
             f"today {fmt(pf.get('sd_today'), 4)} vs 30d {fmt(pf.get('sd_30d'), 4)}")
    ev = d.get("events") or []
    s4 = [e for e in ev if e.get("signal") == "S4"]
    other = [e for e in ev if e.get("signal") != "S4"]
    L.append("S4 CMCI 0.5 crossings today (pre-registered H1 event): "
             + (", ".join(f"{e['asset_id']} cmci={fmt(e.get('strength'), 2)}" for e in s4) if s4 else "none"))
    if other:
        L.append("Other rule events (exploratory): " + ", ".join(f"{e['signal']} {e['asset_id']} {'+' if e.get('direction', 1) > 0 else '-'}" for e in other))
    L.append("")
    L.append(d.get("disclaimer") or DISCLAIMER)
    L.append(f"Public feed is delayed (D+1) and label-stamped. Same-morning, full universe, signal events: {d.get('upgrade_url', UPGRADE_URL)}")
    return "\n".join(L)


def ticker_row(d: dict, ticker: str) -> str:
    t = ticker.strip()
    row = next((n for n in d.get("names", []) if str(n.get("asset_id")) == t or str(n.get("name", "")).lower() == t.lower()), None)
    L = header(d)
    L.append("")
    if row is None:
        L.append(f"{t}: not in today's public panel (free feed covers the pilot panel only; not a statement about the name).")
    else:
        crowded = bool(row.get("cmci") is not None and row["cmci"] >= d.get("crowded_threshold", 0.5))
        L += [f"{row['asset_id']} {row.get('name', '')}",
              f"  CMCI (cross-model consensus, 0-1):     {fmt(row.get('cmci'), 3)}" + ("  (undetermined: null cells)" if row.get("cmci") is None else ""),
              f"  mention_rate (share of eligible answers): {fmt(row.get('mention_rate'), 3)}",
              f"  n_first5 / models with first-5 hit:      {row.get('n_first5', 0)} / {row.get('n_models_first5', 0)}",
              f"  first entry into >=3-model consensus:    {row.get('first_entry_date') or 'not in consensus today'}",
              f"  days since first entry:                  {fmt(row.get('days_since_first_entry'))}",
              f"  crowding flag (CMCI >= 0.5):             {'CROWDED' if crowded else 'not crowded'}",
              f"  placebo (noise-floor name):              {'yes' if row.get('placebo') else 'no'}"]
        ev = [e for e in d.get("events") or [] if str(e.get("asset_id")) == str(row["asset_id"])]
        if ev:
            L.append("  rule events today:                       " + ", ".join(f"{e['signal']}({fmt(e.get('strength'), 2)})" for e in ev))
        solo = [x["model"] for x in d.get("disagreement") or [] if row["asset_id"] in x.get("only", [])]
        if solo:
            L.append(f"  single-model pick:                       only {', '.join(solo)}")
    L.append("")
    L.append(DISCLAIMER)
    L.append(f"Data date {d.get('as_of')} [{d.get('label')}]. Upgrade for same-morning data: {d.get('upgrade_url', UPGRADE_URL)}")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default=FEED_URL)
    ap.add_argument("--file", default=None, help="read a saved latest.json instead of fetching")
    ap.add_argument("--ticker", default=None, help="asset_id (KRX 6-digit) or name")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true", help="print the raw feed")
    a = ap.parse_args(argv)
    d = load_feed(a.url, a.file)
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=1))
    elif a.ticker:
        print(ticker_row(d, a.ticker))
    else:
        print(digest(d, a.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
