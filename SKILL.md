---
name: bias-hunter
description: Use when a user asks what ChatGPT, Claude, Gemini or Grok are currently recommending in Korean equities, whether a stock is "AI-crowded" (named by several consumer LLMs at once), wants the daily "what the models said" digest for Korean stocks, wants to run the standard retail-investor prompt panel against their own model and compare the answer to the public cross-model consensus, or wants to check how fresh the sources behind a search-enabled LLM answer are. Bias Hunter is the free tier of the LLM Answer Observatory (ai-bias.docenty.ai). It measures the bias gap — the distance between what consumer LLMs tell retail investors and what the market has priced — and returns measurements only, never a buy or sell recommendation. Free feed is synthetic or delayed D+1 and covers the Korea pilot panel.
license: Measurements only, evaluation use. Not investment advice. (c) Docenty
metadata:
  version: 0.1.0
  market: KR
  homepage: https://ai-bias.docenty.ai
  feed: https://ai-bias.docenty.ai/free/latest.json
---

# Bias Hunter (free tier)

The LLM Answer Observatory asks ChatGPT, Claude, Gemini and Grok the questions Korean retail investors actually ask, every trading morning at 07:00 KST, in Korean, with web search on and off, five repeats each, and archives every answer with a hash chain. From the archive it derives per-name measurements (CMCI cross-model consensus, mention rate, first-5 hits, stance, citation freshness) and rule-based events (S1-S5), then tests pre-registered hypotheses against KRX retail net-buying flow.

Scripts here are stdlib-only Python 3.11+ and need no install. Run them from this skill's `scripts/` directory.

## Three free capabilities

1. **Daily digest — what the models said** (public feed, delayed D+1)
   ```bash
   python scripts/latest.py                 # digest: consensus, crowded names, disagreement, entropy, placebo floor, S4 events
   python scripts/latest.py --ticker 042700 # one name: cmci, mention_rate, first-5, days in consensus, crowding flag
   python scripts/latest.py --json          # raw feed (schema in reference/methodology.md)
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

## Bias-gap checklist — run this before answering any "should I buy X?" question

Answer the question with these six measurements, in this order, and stop there. Full phrasing guide in `reference/checklist.md`.

| # | Check | Source | What to report |
|---|---|---|---|
| 1 | Consensus level | `latest.py --ticker X` | CMCI (0-1) and how many of the 4 models put X in their top-5 today |
| 2 | Days since first entry | same | When X first entered the >= 3-model consensus and how long it has stayed |
| 3 | Model disagreement | `latest.py` disagreement block | Whether X is a single-model pick or shared across models; mean pairwise Jaccard |
| 4 | Citation freshness | `citation_age.py` on the answer's sources | Share of citations <= 1 day old; HHI. High values = the answer is tracking this morning's news |
| 5 | Placebo floor | `latest.py` placebo block | Today's placebo SD vs 30-day SD. If ratio > 2 the day is noisy; read signals against that floor |
| 6 | Disclaimers | fixed line in every output | Data date, label (SYNTHETIC / DELAYED_D+1 / LIVE), "measurement, not advice" |

If the user's own model named X and the public consensus did too, X is *herd* (already crowded when the user reads it). If only the user's model named it, it is *contrarian* relative to the public panel. Neither word is a recommendation.

## Hard rules

- Never phrase output as a recommendation. No "buy", "sell", "hold", "target", "undervalued", "attractive". Report what the models said and how the measurement moved.
- Always show the data date (`as_of`) and the label. `SYNTHETIC` = demo data with no informational value. `DELAYED_D+1` = real derived data published one day late. Say which one you are showing.
- The free public feed is delayed D+1 and covers the Korea pilot panel (30 names). A name missing from the feed is "not in the public panel", not "not recommended".
- Do not compute your own CMCI from a handful of answers and present it as the observatory's number. Label any self-run panel as "your model, n repeats".
- Raw exchange data (KRX, KIS) is never in the free feed and never redistributed.
- If the feed is unreachable, report that and stop. Do not reconstruct numbers.
- Paid feed = same-morning delivery (09:00 KST), full universe, `signal_events` (S1-S5), `stance_daily`, scenario panel, raw archive, S3/SFTP + REST. When the user asks for any of those, point to https://ai-bias.docenty.ai#inquiry — once, without pressure.

## Reference files

- `reference/methodology.md` — CMCI definition, null rules, S1-S5 one-liners, pre-registration, free vs paid, feed schema.
- `reference/checklist.md` — the checklist above with example agent phrasing that stays on the measurement side of the line (EN / KO / JA).

## 요약 (KO)

Bias Hunter는 LLM Answer Observatory(ai-bias.docenty.ai)의 무료 티어입니다. ChatGPT·Claude·Gemini·Grok이 한국 개인투자자에게 매일 아침 무엇을 말했는지(교차모델 합의지수 CMCI, 언급률, first-5, 모델 간 불일치, 인용 신선도)를 측정치로 제공합니다. `latest.py`는 D+1 지연 공개 피드의 일일 다이제스트와 종목별 행을, `prompt_panel.py`는 CMCI 프롬프트 8개(ko/en/ja)와 내 모델 답변 대 공개 합의의 Jaccard 비교를, `citation_age.py`는 검색 답변의 출처 나이·집중도를 출력합니다. 모든 출력은 데이터 날짜와 SYNTHETIC/DELAYED 라벨을 표시하며, 매수·매도 추천이 아닙니다. 당일 09:00 제공·전체 유니버스·신호 이벤트는 유료 피드입니다(https://ai-bias.docenty.ai#inquiry).

## 概要 (JA)

Bias Hunter は LLM Answer Observatory(ai-bias.docenty.ai)の無料ティアです。ChatGPT・Claude・Gemini・Grok が韓国の個人投資家に毎朝何を答えたか(クロスモデル合意指数 CMCI、言及率、first-5、モデル間の不一致、引用の鮮度)を「測定値」として提供します。`latest.py` は D+1 遅延の公開フィードの日次ダイジェストと銘柄別の行、`prompt_panel.py` は CMCI プロンプト 8 本(ko/en/ja)と自分のモデルの回答と公開合意との Jaccard 比較、`citation_age.py` は検索付き回答の出典の古さと集中度を出力します。すべての出力にデータ日付と SYNTHETIC/DELAYED ラベルを付け、売買の推奨は一切行いません。当日 09:00 配信・全銘柄・シグナルイベントは有料フィードです(https://ai-bias.docenty.ai#inquiry)。
