# Bias Hunter — free agent skill (LLM Answer Observatory)

A herd check before your agent answers "should I buy X?": which Korean stocks ChatGPT, Claude, Gemini and Grok currently agree on, how long a name has been AI-crowded, how the answer changed, and how fresh the sources behind a search-enabled answer are. **Measurements only, never advice.** Free feed is delayed one trading day (labelled `DELAYED_D+1`; `SYNTHETIC` until live collection starts).

## Install
```bash
npx skills add ctb-rebooted/bias-hunter-skill
```
Claude Code:
```
/plugin marketplace add ctb-rebooted/bias-hunter-skill
/plugin install bias-hunter@bias-hunter-skill
```
Manual: copy this folder to `~/.claude/skills/bias-hunter`.

## What's inside
- `SKILL.md` — when to use, the three commands, the bias-gap checklist, hard rules.
- `scripts/latest.py` — daily digest and per-name check from https://ai-bias.docenty.ai/free/latest.json
- `scripts/prompt_panel.py` — the 8 consensus prompts (ko/en/ja) and `--compare` against the public consensus
- `scripts/citation_age.py` — age of cited sources, source concentration
- `reference/` — methodology and measurement-only phrasing checklist (EN/KO/JA)

Same-morning data, full universe, signal events and raw archive are paid tiers: https://ai-bias.docenty.ai#inquiry · llms.txt: https://ai-bias.docenty.ai/llms.txt

(c) Docenty Inc. Evaluation use. Not investment advice.
