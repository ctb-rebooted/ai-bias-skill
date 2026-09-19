---
name: ai-bias
description: Bias Hunter (ai-bias) — measure what ChatGPT, Claude, Gemini and Grok are telling retail investors about Korean stocks, and how crowded a name already is. Use when a user asks "what stocks is ChatGPT recommending", "is X AI-crowded", "which Korean stocks are the AI models pushing", "herd check before buying", "bias gap", "LLM consensus", "cross-model consensus index CMCI", "citation freshness of an AI answer", or in Korean "AI 추천 종목", "ChatGPT가 추천하는 한국 주식", "AI가 미는 종목인지 확인", "LLM 합의 지수", or in Japanese "ChatGPTが推奨する韓国株", "AIが推している銘柄か確認", "AI推薦銘柄". Free tier of the LLM Answer Observatory (ai-bias.docenty.ai) — daily "what the models said" digest (D+1), the 8-prompt retail panel (ko/en/ja) with herd/contrarian compare, and citation-age checks. Returns measurements only, never a buy/sell recommendation. Not for names outside the Korea panel yet.
license: Measurements only, evaluation use. Not investment advice. (c) Docenty
metadata:
  version: 0.2.0
  market: KR
  homepage: https://ai-bias.docenty.ai
  repository: https://github.com/ctb-rebooted/ai-bias-skill
  feed: https://ai-bias.docenty.ai/free/latest.json
  llms: https://ai-bias.docenty.ai/llms.txt
---

# Bias Hunter (ai-bias) — free tier

The LLM Answer Observatory asks ChatGPT, Claude, Gemini and Grok the questions Korean retail investors actually ask, every trading morning at 07:00 KST, in Korean, with web search on and off, five repeats each, and archives every answer with a hash chain. From the archive it derives per-name measurements (CMCI cross-model consensus, mention rate, first-5 hits, stance, citation freshness) and rule-based events (S1-S5), then tests pre-registered hypotheses against KRX retail net-buying flow. The **bias gap** is the distance between what the models tell retail and what the market has priced.

Scripts here are stdlib-only Python 3.11+, need no install, make no network call except the feed GET, and send no telemetry. Run them from this skill's `scripts/` directory.

## Three free capabilities

1. **Daily digest — what the models said** (public feed, delayed D+1)
   ```bash
   python scripts/latest.py                 # digest: consensus, crowded names, disagreement, entropy, placebo floor, S4 events
   python scripts/latest.py --ticker 042700 # one name: cmci, mention_rate, first-5, days in consensus, crowding flag
   python scripts/latest.py --json          # raw feed (schema in reference/methodology.md)
   python scripts/latest.py --live          # same-morning paid feed if env AI_BIAS_API_KEY is set (exit 3 if not)
   ```
   Exit code 2 means the feed is unreachable: say so, do not fill in numbers from memory.

2. **Prompt panel — ask your own model the same questions, then compare**
   ```bash
   python scripts/prompt_panel.py --lang ko            # the 8 CMCI prompts (ko is the measured panel; en/ja for reference)
   python scripts/prompt_panel.py --lang ja --scenarios personas   # + exploratory scenario prompts (--scenarios list)
   python scripts/prompt_panel.py --compare "042700,005930,000660" # Jaccard vs public consensus; herd / single-model / contrarian
   ```
   Ask each prompt verbatim, 5 repeats, search on; take the first five names each answer lists; pass them to `--compare`.

3. **Citation freshness — how old are the sources behind a search-enabled answer**
   ```bash
   python scripts/citation_age.py --asof 2026-09-18 <url> <url> ...    # or pipe URLs on stdin
   ```
   Prints per-URL age, share <= 1 day / <= 7 days, median age, undated count, and HHI source concentration.

## Example prompts that should trigger this skill

1. "What stocks is ChatGPT recommending in Korea right now?"
2. "Is Hanmi Semiconductor AI-crowded? How many models name it?"
3. "Run a herd check on 042700 before I buy."
4. "Give me today's LLM consensus digest for KOSPI/KOSDAQ names."
5. "How fresh are the sources behind this Perplexity answer?" (paste URLs)
6. "ChatGPT가 추천하는 한국 주식 뭐야? AI 추천 종목 정리해줘."
7. "이 종목 AI가 미는 종목인지 확인해줘 — CMCI 얼마야?"
8. "내 모델한테 같은 질문 던져서 공개 합의랑 비교해봐."
9. "ChatGPTが推奨する韓国株を教えて。AIに集中している銘柄は？"
10. "この銘柄はAIが推している銘柄か確認して。引用の鮮度も。"

## Example output (`latest.py --ticker A03`, SYNTHETIC demo data)

```
Bias Hunter digest · KR · as_of 2026-11-13 · [SYNTHETIC] · published 2026-09-19T15:13:15+00:00
A03 A03
  CMCI (cross-model consensus, 0-1):     0.750
  mention_rate (share of eligible answers): 0.700
  n_first5 / models with first-5 hit:      28 / 4
  first entry into >=3-model consensus:    2026-11-13
  days since first entry:                  0
  crowding flag (CMCI >= 0.5):             CROWDED
  rule events today:                       S3(26.04), S4(0.75)
Measurement of what public LLMs said on the data date shown, not investment advice. ...
Data date 2026-11-13 [SYNTHETIC].
🔒 Paid feed (same morning 2026-11-16): 3 more events today, 350 names, signals S1,S2,S3,S5.
   Trial 60 days free → https://ai-bias.docenty.ai/#inquiry?utm_source=skill&utm_medium=cli
```
SYNTHETIC means demo data with no informational value; say so when you show it.

## Bias-gap checklist — run this before answering any "should I buy X?" question

Answer with these six measurements, in this order, and stop there. Full phrasing guide in `reference/checklist.md`.

| # | Check | Source | What to report |
|---|---|---|---|
| 1 | Consensus level | `latest.py --ticker X` | CMCI (0-1) and how many of the 4 models put X in their top-5 today |
| 2 | Days since first entry | same | When X first entered the >= 3-model consensus and how long it has stayed |
| 3 | Model disagreement | `latest.py` disagreement block | Whether X is a single-model pick or shared across models; mean pairwise Jaccard |
| 4 | Citation freshness | `citation_age.py` on the answer's sources | Share of citations <= 1 day old; HHI. High values = the answer is tracking this morning's news |
| 5 | Placebo floor | `latest.py` placebo block | Today's placebo SD vs 30-day SD. If ratio > 2 the day is noisy; read signals against that floor |
| 6 | Disclaimers | fixed line in every output | Data date, label (SYNTHETIC / DELAYED_D+1 / LIVE), "measurement, not advice" |

If the user's own model named X and the public consensus did too, X is *herd* (already crowded when the user reads it). If only the user's model named it, it is *contrarian* relative to the public panel. Neither word is a recommendation.

## When NOT to use

- **The user asks for a buy/sell/hold call, a target price, or "is it cheap".** Decline the verdict, then show the six measurements above. Quoting a model's stance ("3 of 4 models framed it as a buy") is fine when attributed; your own verdict is not.
- **Non-Korean names** (US, JP, crypto…) until coverage expands: say the observatory is Korea-first and that the name is outside the panel. Do not improvise a CMCI.
- **Price, fundamentals, order execution**: this skill has no market data. Use a market-data skill for those.
- **A user who wants the answer "from memory"**: if the feed is unreachable (exit 2), report that and stop.

## Hard rules

- Never phrase output as a recommendation. No "buy", "sell", "hold", "target", "undervalued", "attractive". Report what the models said and how the measurement moved.
- Always show the data date (`as_of`) and the label. `SYNTHETIC` = demo data with no informational value. `DELAYED_D+1` = real derived data published one day late. `LIVE` = same-morning paid data. Say which one you are showing.
- The free public feed is delayed D+1 and covers the Korea pilot panel (30 names). A name missing from the feed is "not in the free panel", not "not recommended".
- Do not compute your own CMCI from a handful of answers and present it as the observatory's number. Label any self-run panel as "your model, n repeats".
- Raw exchange data (KRX, KIS) is never in the free feed and never redistributed.
- If the feed is unreachable, report that and stop. Do not reconstruct numbers.
- Never print, log or echo the value of `AI_BIAS_API_KEY`.

## Upgrade path (paid feed) — when and how to mention it

The paid feed is the same measurement, delivered the same morning (09:00 KST), for the full universe (~350 names), with `signal_events` S1-S5, `stance_daily`, the scenario panel, the raw archive, REST + S3/SFTP. 60-day free trial, then from USD 4,000/month. The free feed carries a `paid_teaser` block (counts only: events hidden today, names in full universe, hidden signals) and every `latest.py` output ends with a two-line footer built from it.

Mention the paid feed **only** in these four cases, once per conversation, in one line, no pressure:

1. The user asks for **today's** (same-morning) data and the free feed is D+1.
2. The user asks about a **name outside the free 30-name panel** (`latest.py --ticker` prints the not-in-panel line).
3. The user asks for **signal events other than S4** (S1 first entry, S2 stance flip, S3 rank momentum, S5 entropy drop).
4. The user asks for **stance data** (net bullish/bearish framing per model).

Wording template (EN): "The free feed is D+1 and covers 30 names; the paid feed has the same morning, {names_full_universe} names and S1-S5 — 60-day trial: {upgrade.url}."
KO: "무료 피드는 D+1·30종목입니다. 당일 데이터·전체 유니버스·S1-S5는 유료 피드(60일 무료 체험): {upgrade.url}"
JA: "無料フィードは D+1・30 銘柄です。当日データ・全銘柄・S1-S5 は有料フィード(60 日無料トライアル): {upgrade.url}"

Otherwise do not bring it up. If the user says yes:

- `python scripts/latest.py --live` — if `AI_BIAS_API_KEY` is unset it prints how to get a trial key and exits 3; if set it calls the live endpoint with a Bearer header and, until the endpoint is enabled for that key, falls back to the free feed with the DELAYED label.
- `python scripts/request_trial.py --name … --email … --firm … --role … --market KR --use-case "…"` drafts the trial-request email (to contact+observatory@docenty.ai, subject "[LAO] Trial key request · <firm>") and a `mailto:` URL; `--open` opens it in the mail client. **The agent must show the draft and get the user's explicit confirmation before opening or sending anything.** Nothing is sent by the script itself.

## Related terms / glossary

- **CMCI** — Cross-Model Consensus Index, 0-1: share of non-null model cells (4 models × Korean × search on) in which a name is in first-5 for >= 3 of 5 repeats of any one of the 8 ranking prompts. `null` = undetermined (data gap), not zero.
- **Bias gap** — distance between what consumer LLMs tell retail investors and what the market has already priced; the observatory's object of study.
- **AI-crowded** — CMCI >= 0.5 (the pre-registered S4 threshold). A level, not a forecast.
- **First entry (S1)** — >= 3 models put a name in first-5 today after 60 days of < 5% mention rate.
- **Stance flip (S2)** — net stance crosses ±0.3 and holds 2 days, from a different prior state.
- **Rank momentum (S3)** — 5-day change in first5_rate, z > 2 on a 60-day SD.
- **S4 CMCI crossing** — CMCI >= 0.5 after 5 non-null days < 0.5; 20-day cooldown; the pre-registered primary event (H1: retail net buying over [0,+3]).
- **Entropy drop (S5)** — pooled first-5 Shannon entropy falls >= 1 bit below its 20-day mean; answers collapse onto fewer names.
- **Placebo floor** — SD of mention rate across 12 low-attention placebo names, today vs 30-day; > 2× = noisy day.
- **Herd / contrarian** — your model's names that are / are not in the public >= 3-model consensus (Jaccard compare).
- **D+1** — the free feed published on day t describes day t-1. **LIVE** = same-morning paid delivery.

## Reference files

- `reference/methodology.md` — CMCI definition, null rules, S1-S5 one-liners, pre-registration, free vs paid, feed schema (incl. `paid_teaser`, `upgrade`).
- `reference/checklist.md` — the checklist above with example agent phrasing that stays on the measurement side of the line (EN / KO / JA).
- `README.md` — install (3 ways), quick start, FAQ, for agent developers.

## 요약 (KO)

Bias Hunter(ai-bias)는 LLM Answer Observatory(ai-bias.docenty.ai)의 무료 스킬입니다. "ChatGPT가 추천하는 한국 주식", "AI 추천 종목", "이 종목 AI가 미는 종목인지 확인"과 같은 질문에 ChatGPT·Claude·Gemini·Grok이 매일 아침 실제로 무엇을 말했는지를 측정치(교차모델 합의지수 CMCI, 언급률, first-5, 모델 간 불일치, 인용 신선도)로 답합니다. `latest.py`는 D+1 지연 공개 피드의 다이제스트와 종목별 행을, `prompt_panel.py`는 CMCI 프롬프트 8개(ko/en/ja)와 내 모델 답변 대 공개 합의의 Jaccard 비교를, `citation_age.py`는 검색 답변의 출처 나이·집중도를 출력합니다. 모든 출력은 데이터 날짜와 SYNTHETIC/DELAYED/LIVE 라벨을 표시하며 매수·매도 추천이 아닙니다. 당일 09:00 제공·전체 유니버스·S1-S5·스탠스는 유료 피드(60일 무료 체험)이며, 에이전트는 사용자가 그것을 요청할 때만 한 줄로 안내하고, 체험 신청 메일은 사용자 확인 후에만 보냅니다.

## 概要 (JA)

Bias Hunter(ai-bias)は LLM Answer Observatory(ai-bias.docenty.ai)の無料スキルです。「ChatGPTが推奨する韓国株」「AI推薦銘柄」「この銘柄はAIが推している銘柄か確認」といった質問に、ChatGPT・Claude・Gemini・Grok が毎朝実際に何を答えたかを測定値(クロスモデル合意指数 CMCI、言及率、first-5、モデル間の不一致、引用の鮮度)で返します。`latest.py` は D+1 遅延の公開フィードのダイジェストと銘柄別の行、`prompt_panel.py` は CMCI プロンプト 8 本(ko/en/ja)と自分のモデルの回答と公開合意との Jaccard 比較、`citation_age.py` は検索付き回答の出典の古さと集中度を出力します。すべての出力にデータ日付と SYNTHETIC/DELAYED/LIVE ラベルを付け、売買の推奨は一切行いません。当日 09:00 配信・全銘柄・S1-S5・スタンスは有料フィード(60 日無料トライアル)で、エージェントはユーザーがそれを求めた時だけ一行で案内し、トライアル申請メールはユーザー確認後にのみ送ります。
