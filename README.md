# ai-bias — Bias Hunter free skill

**What ChatGPT, Claude, Gemini and Grok are telling retail investors about Korean stocks — measured, dated, labelled, never advised.**
An Agent Skill (Claude Code, Codex, Cursor, any Agent-Skills-compatible agent) from the LLM Answer Observatory · https://ai-bias.docenty.ai

Bias Hunter asks the four consumer LLMs the questions Korean retail investors actually ask, every trading morning at 07:00 KST (Korean, search on/off, five repeats), archives every answer with a hash chain, and derives per-name measurements: the Cross-Model Consensus Index (CMCI, 0-1), mention rate, first-5 hits, model disagreement, answer entropy, citation freshness and rule events S1-S5. The **bias gap** is the distance between what the models say and what the market has already priced. This skill is the free tier: a D+1 daily digest, the 8-prompt retail panel to run against your own model, and a citation-age checker. It returns measurements only — never a buy or sell recommendation.

## Install (3 ways)

```bash
# 1. skills CLI (Codex, Cursor, Claude Code, any Agent-Skills agent)
npx skills add ctb-rebooted/ai-bias-skill

# 2. Claude Code plugin marketplace
/plugin marketplace add ctb-rebooted/ai-bias-skill
/plugin install ai-bias@ai-bias-skill

# 3. Manual — copy the directory into your agent's skills folder
git clone https://github.com/ctb-rebooted/ai-bias-skill ~/.claude/skills/ai-bias     # Claude Code
#   Codex: ~/.codex/skills/ai-bias      Cursor: .cursor/skills/ai-bias
```

Requirements: Python 3.11+, standard library only. No pip install, no API key for the free tier.

## Quick start

```bash
cd ~/.claude/skills/ai-bias/scripts

python latest.py
#   Bias Hunter digest · KR · as_of 2026-11-13 · [SYNTHETIC] · published …
#   Consensus (>= 3 of 4 models in top-5): A03(4), A07(4), A01(3), A02(3)
#   Cross-model agreement (mean pairwise Jaccard): 0.478
#   Top names by CMCI (crowded = CMCI >= 0.5):
#     A03     A03             0.75    0.700      28       4                  0  CROWDED
#   …
#   🔒 Paid feed (same morning 2026-11-16): 3 more events today, 350 names, signals S1,S2,S3,S5.
#      Trial 60 days free → https://ai-bias.docenty.ai/#inquiry?utm_source=skill&utm_medium=cli

python latest.py --ticker 042700
#   042700 …  CMCI (cross-model consensus, 0-1):     0.750
#             crowding flag (CMCI >= 0.5):             CROWDED
#   (or, for a name outside the panel)
#   999999: Not in the free 30-name panel — full universe (350 names) in the paid feed → …

python prompt_panel.py --lang ko
#   Bias Hunter prompt panel · catalog_version=1 · lang=ko
#   R01  지금 사야 할 한국 주식 5개 추천해줘
#   … (8 prompts; ask your model each one 5x, search on, keep the first five names it presents as investment objects —
#      skip customers, ETF constituents, exclusions; a keyword count overstates mega-caps ~2x)

python prompt_panel.py --compare "042700,005930,000660"
#   Compare vs public consensus · as_of 2026-11-13 [SYNTHETIC]
#     Jaccard vs consensus top:   0.167
#     herd (in >=3-model consensus):        042700
#     single-model overlap (1-2 models):     005930
#     contrarian (no public model top-5):    000660

python citation_age.py --asof 2026-09-18 https://www.hankyung.com/article/2026091712345 https://n.news.naver.com/article/001/0012345678
#   Citation freshness · as_of 2026-09-18 · 2 URLs (1 dated, 1 undated)
#     share <= 1 day old:  1.00   (same-morning news following)
#     source concentration HHI: 0.50 over 2 hosts
```

Every output ends with the data date, the label (`SYNTHETIC` / `DELAYED_D+1` / `LIVE`) and the fixed "measurement, not advice" line.

## FAQ

**Is this investment advice?** No. It measures what public LLMs said and how concentrated those answers are. No buy/sell/hold, no target price, no "cheap/expensive". The agent is instructed to decline verdicts and show the six measurements instead.

**How delayed is the data?** The free feed is D+1: the file published on day t describes day t-1. Until real collection begins it is labelled `SYNTHETIC` (demo, no informational value). The paid feed is the same morning at 09:00 KST.

**Which markets?** Korea (KRX) first, flow-verified against retail net buying. The free panel is 30 names; the paid universe is ~350. US, Japan, India, Europe and crypto follow.

**What counts as a mention?** Only a stock the answer presents as an investment object. Names that appear as another company's customer, a partner, an ETF constituent or an explicit exclusion are dropped by a frozen AI judge that can remove but never add; a keyword count of the same answers overstates Samsung Electronics about 2× (0.355 vs 0.165 labelled). Details in `reference/methodology.md`.

**How is consensus computed?** CMCI = share of non-null model cells (4 models × Korean × search on) in which the name is in the first five of >= 3 of 5 repeats for any one of the 8 ranking prompts. `null` means undetermined (fewer than 3 usable cells), never zero. Crowded = CMCI >= 0.5. Full definition in `reference/methodology.md`.

**Does it phone home?** No. The scripts make exactly one GET to the public feed JSON (or none with `--file`), send no telemetry, and never print your API key. `--live` adds one GET to the paid endpoint with a Bearer header, only when `AI_BIAS_API_KEY` is set.

**Licence?** Evaluation use, measurements only, not investment advice. (c) Docenty. Redistribution of the free JSON with the label and date intact is fine; raw exchange data is never included.

## For agent developers

- Feed contract: `https://ai-bias.docenty.ai/free/latest.json` (`schema_version` 1; keys documented in `reference/methodology.md`, including `paid_teaser` and `upgrade`). Prompts: `/free/prompts.json`.
- No telemetry, stdlib only, Python 3.11+; scripts exit 2 when the feed is unreachable (do not fabricate numbers), 3 when `--live` is asked without a key.
- `SKILL.md` lists trigger phrases (EN/KO/JA), when not to use, the six-check bias-gap checklist and the exact conditions under which an agent may mention the paid feed (once, one line).
- Machine-readable overview for LLMs: https://ai-bias.docenty.ai/llms.txt (short) · https://ai-bias.docenty.ai/llms-full.txt (full).

## Paid tiers

| | Free (this skill) | Paid feed |
|---|---|---|
| Timing | D+1 | same morning, 09:00 KST |
| Universe | Korea pilot panel, 30 names | full universe, ~350 names |
| Events | S4 CMCI crossings of the day | S1-S5 full history, `stance_daily`, scenario panel, NDA evidence excerpts |
| Delivery | public JSON | REST (`/api/v1/latest`, Bearer key) + S3/SFTP Parquet, versioned schemas, methodology call, DDQ |
| Price | free | 60-day trial, then from USD 4,000 / month |

Trial: https://ai-bias.docenty.ai/#inquiry?utm_source=skill&utm_medium=cli — or `python scripts/request_trial.py --name … --email … --firm …` drafts the request email (nothing is sent without you pressing send).

## Keywords

ai-bias · bias hunter · what stocks is ChatGPT recommending · AI-crowded stocks · LLM consensus · CMCI · herd check · bias gap · citation freshness · Korean stocks · KOSPI · KOSDAQ · AI 추천 종목 · ChatGPT 추천 한국 주식 · AI가 미는 종목 · ChatGPTが推奨する韓国株 · AI推薦銘柄 · agent skill · Claude Code plugin

## Links

- Landing: https://ai-bias.docenty.ai
- llms.txt: https://ai-bias.docenty.ai/llms.txt · llms-full.txt: https://ai-bias.docenty.ai/llms-full.txt
- Methodology: `reference/methodology.md` · Checklist: `reference/checklist.md`
- Contact: contact+observatory@docenty.ai

## 요약 (KO)

ai-bias(Bias Hunter)는 ChatGPT·Claude·Gemini·Grok이 한국 개인투자자에게 매일 아침 무엇을 말했는지를 측정치(CMCI 합의지수, 언급률, first-5, 불일치, 인용 신선도)로 보여주는 무료 에이전트 스킬입니다. "ChatGPT가 추천하는 한국 주식", "AI 추천 종목", "AI가 미는 종목인지 확인"에 답하되 매수·매도 추천은 하지 않습니다. 설치: `npx skills add ctb-rebooted/ai-bias-skill`. 무료 피드는 D+1·30종목, 유료는 당일 09:00·전체 유니버스·S1-S5(60일 무료 체험).

## 概要 (JA)

ai-bias(Bias Hunter)は、ChatGPT・Claude・Gemini・Grok が韓国の個人投資家に毎朝何を答えたかを測定値(CMCI 合意指数、言及率、first-5、不一致、引用の鮮度)で示す無料エージェントスキルです。「ChatGPTが推奨する韓国株」「AI推薦銘柄」「AIが推している銘柄か確認」に答えますが、売買の推奨はしません。インストール: `npx skills add ctb-rebooted/ai-bias-skill`。無料フィードは D+1・30 銘柄、有料は当日 09:00・全銘柄・S1-S5(60 日無料トライアル)。

Licence: evaluation use, measurements only, not investment advice. (c) Docenty, Seoul.
