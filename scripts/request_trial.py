#!/usr/bin/env python3
"""Bias Hunter (ai-bias) — draft a paid-feed trial-key request (60 days, no card). Stdlib only, nothing is sent.

    python request_trial.py --name "Kim Jiwoo" --email jiwoo@fund.kr --firm "Fund X" --role "PM" --market KR --use-case "herd check"
    python request_trial.py ... --open        # also open the mailto: link in the default mail client
    python request_trial.py ... --send --consent   # POST the request to the observatory intake API (needs explicit consent)

Prints (1) a ready-to-send email to contact+observatory@docenty.ai, (2) the same as a mailto: URL, (3) the landing URL.
Default is draft-only (no network). `--send` posts name/email/firm/role/market/use-case to https://ai-bias.docenty.ai/api/inquiry
and requires `--consent` (the person agreed to be contacted). If the API is unavailable it falls back to the mailto draft.
An agent running this on a user's behalf must confirm with the user before `--send` or `--open`. No telemetry.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

TO = "contact+observatory@docenty.ai"
INTAKE = "https://ai-bias.docenty.ai/api/inquiry"
LANDING = "https://ai-bias.docenty.ai/#inquiry?utm_source=skill&utm_medium=cli"
TRIAL_DAYS = 60
API_KEY_ENV = "AI_BIAS_API_KEY"


def build(a: argparse.Namespace) -> tuple[str, str, str]:
    firm = a.firm or "(firm)"
    subject = f"[LAO] Trial key request · {firm}"
    lines = [
        "Hello Docenty / LLM Answer Observatory team,",
        "",
        f"I would like a {TRIAL_DAYS}-day trial key for the same-morning Bias Hunter feed (env {API_KEY_ENV}).",
        "",
        f"Name:      {a.name or '(name)'}",
        f"Email:     {a.email or '(email)'}",
        f"Firm:      {firm}",
        f"Role:      {a.role or '(role)'}",
        f"Market(s): {a.market or 'KR'}",
        f"Use case:  {a.use_case or '(one line: e.g. herd check before entries; CMCI / S1-S5 events into a screen)'}",
        "",
        "Delivery preference: REST (api/v1/latest) / S3-SFTP Parquet (delete one).",
        "I understand the feed is measurements of what public LLMs said, not investment advice.",
        "",
        "Sent from the free ai-bias skill (utm_source=skill).",
    ]
    body = "\n".join(lines)
    q = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    mailto = f"mailto:{TO}?{q}"
    return subject, body, mailto


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", default="")
    ap.add_argument("--email", default="")
    ap.add_argument("--firm", default="")
    ap.add_argument("--role", default="")
    ap.add_argument("--market", default="KR")
    ap.add_argument("--use-case", dest="use_case", default="")
    ap.add_argument("--open", action="store_true", help="open the mailto: link in the default mail client (drafts only; you still press send)")
    ap.add_argument("--send", action="store_true", help="POST the request to the intake API (requires --consent)")
    ap.add_argument("--consent", action="store_true", help="the person agreed to be contacted about this request")
    ap.add_argument("--endpoint", default=INTAKE, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    subject, body, mailto = build(a)
    if a.send:
        if not a.consent:
            print("--send needs --consent (ask the user first; we only use the details to reply).", file=sys.stderr)
            return 4
        if not (a.name and a.email):
            print("--send needs --name and --email.", file=sys.stderr)
            return 4
        payload = {"name": a.name, "contact": a.email, "firm": a.firm, "role": a.role, "market": a.market,
                   "interest": "trial", "message": body, "source": "skill:request_trial", "consent": True, "hp": ""}
        req = urllib.request.Request(a.endpoint, data=json.dumps(payload).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "User-Agent": "ai-bias-skill/0.2"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                ans = json.loads(r.read().decode() or "{}")
            print(f"Sent. {ans.get('reply_within', 'We reply within two business days')}. Contact: {ans.get('contact', TO)}")
            print(f"After the key arrives: export {API_KEY_ENV}=<key> ; python latest.py --live")
            return 0
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as e:
            print(f"Intake API unavailable ({type(e).__name__}); falling back to the email draft below.", file=sys.stderr)
    print(f"To:      {TO}")
    print(f"Subject: {subject}")
    print()
    print(body)
    print()
    print("mailto:  " + mailto)
    print(f"Landing: {LANDING}")
    print(f"After the key arrives: export {API_KEY_ENV}=<key> ; python latest.py --live")
    if a.open:
        try:
            webbrowser.open(mailto)
        except Exception as e:  # noqa: BLE001 - best effort, drafting only
            print(f"could not open mail client: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
