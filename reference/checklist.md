# Bias-gap checklist — agent phrasing that stays on the measurement side

Run all six before answering "should I buy X?", "is X a good stock?", "what does AI think of X?". Report; do not conclude. The line: you may say what the models said, how many said it, since when, how fresh their sources were, and how noisy the day is. You may not say what the user should do, whether the name is cheap or expensive, or what will happen next.

Words to avoid in your own voice: buy, sell, hold, accumulate, avoid, target, upside, downside, undervalued, overvalued, attractive, opportunity, bullish, bearish. Quoting a model's stance ("3 of 4 models framed it as a buy") is a measurement and is fine when attributed.

## 1. Consensus level
- Command: `python scripts/latest.py --ticker <asset_id>`
- EN: "On {as_of} [{label}], {name} had CMCI {cmci} — {k} of 4 consumer models put it in their top-5 for the standard 'what should I buy' prompts. Threshold for 'crowded' in the observatory's pre-registration is 0.5."
- KO: "{as_of} 기준 [{label}] {name}의 CMCI는 {cmci}입니다. 표준 '지금 뭐 사야 해' 프롬프트에서 4개 모델 중 {k}개가 top-5에 올렸습니다. 사전등록 상 '쏠림' 기준선은 0.5입니다."
- JA: "{as_of} 時点 [{label}] の {name} の CMCI は {cmci} です。標準的な「今何を買うべきか」プロンプトで 4 モデル中 {k} モデルが top-5 に挙げました。事前登録上の「集中」の閾値は 0.5 です。"
- If `cmci` is null: "undetermined today (fewer than 3 model cells had enough eligible answers) — this is a data gap, not zero consensus."

## 2. Days since first entry
- EN: "{name} entered the >= 3-model consensus on {first_entry_date} and has been there {days} trading days without a break." / "It is not in the >= 3-model consensus today."
- KO: "{name}은(는) {first_entry_date}에 3개 모델 이상 합의에 들어와 {days}거래일 연속 머물고 있습니다." / "오늘은 3개 모델 이상 합의에 없습니다."
- JA: "{name} は {first_entry_date} に 3 モデル以上の合意に入り、{days} 営業日連続で残っています。" / "本日は 3 モデル以上の合意に入っていません。"
- Do not add "so it is late" or "so it is early". The number is the answer.

## 3. Model disagreement
- Command: `python scripts/latest.py` (disagreement block, jaccard_mean)
- EN: "Cross-model agreement today is {jaccard_mean} (mean pairwise Jaccard of top-5 lists). {name} is {'shared by k models' | 'a single-model pick: only ' + model}."
- KO: "오늘 모델 간 일치도는 {jaccard_mean}(top-5 목록의 평균 쌍별 Jaccard)입니다. {name}은(는) {'k개 모델 공통' | model + ' 한 모델만의 선택'}입니다."
- JA: "本日のモデル間一致度は {jaccard_mean}(top-5 リストの平均ペア Jaccard)です。{name} は {'k モデル共通' | model + ' の単独選択'} です。"

## 4. Citation freshness
- Command: `python scripts/citation_age.py --asof {date} <urls the answer cited>`
- EN: "Of {n} sources the answer cited, {n_dated} carry a date in the URL; {share_le_1d} of those are <= 1 day old and the median age is {median} days. Source concentration HHI {hhi} across {n_hosts} hosts." Add when share_le_1d >= 0.5: "The answer is largely tracking that morning's news."
- KO: "답변이 인용한 출처 {n}개 중 {n_dated}개에 URL 날짜가 있고, 그중 {share_le_1d}가 1일 이내, 중앙 나이는 {median}일입니다. 출처 집중도 HHI는 {hhi}({n_hosts}개 도메인)." 0.5 이상이면: "답변이 그날 아침 기사를 상당 부분 따라가고 있습니다."
- JA: "回答が引用した {n} 件のうち {n_dated} 件に URL 日付があり、そのうち {share_le_1d} が 1 日以内、年齢の中央値は {median} 日です。出典集中度 HHI は {hhi}({n_hosts} ドメイン)。" 0.5 以上なら: "回答はその日の朝のニュースを大きく追っています。"

## 5. Placebo floor
- Command: `python scripts/latest.py` (placebo block)
- EN: "Noise floor: placebo-name mention-rate SD today {sd_today} vs 30-day {sd_30d}. {'Ratio above 2 — treat today's moves as noisy.' | 'Within the usual range.'}"
- KO: "노이즈 바닥: 플라시보 종목 언급률 SD 오늘 {sd_today} vs 30일 {sd_30d}. {'비율 2 초과 — 오늘 움직임은 잡음 대비로 읽습니다.' | '평소 범위 안입니다.'}"
- JA: "ノイズフロア: プラセボ銘柄の言及率 SD は本日 {sd_today}、30 日 {sd_30d}。{'比率が 2 を超えています — 本日の動きはノイズ比で読みます。' | '通常範囲内です。'}"

## 6. Disclaimers (always, verbatim)
- EN: "Data date {as_of}, label {label}. {'Synthetic demo data — no informational value.' | 'Public feed is delayed one day.'} These are measurements of what public LLMs said, not investment advice or a recommendation."
- KO: "데이터 날짜 {as_of}, 라벨 {label}. {'합성 데모 데이터로 정보 가치가 없습니다.' | '공개 피드는 1일 지연입니다.'} 공개 LLM이 말한 내용의 측정치이며 투자 조언이나 추천이 아닙니다."
- JA: "データ日付 {as_of}、ラベル {label}。{'合成デモデータであり情報価値はありません。' | '公開フィードは 1 日遅延です。'} 公開 LLM の発言の測定値であり、投資助言や推奨ではありません。"

## Putting it together — a complete answer to "should I buy 042700?"

> I can't tell you whether to buy it, but I can tell you where it sits in the AI-answer landscape. On 2026-11-13 [DELAYED_D+1], Hanmi Semiconductor had CMCI 0.75: 3 of 4 consumer models listed it in their top-5 for the standard retail prompts, above the 0.5 crowding threshold. It entered the >= 3-model consensus that day (0 days prior), and today also produced an S4 crossing event — the pre-registered event type whose flow effect is being tested, with no result published yet. Cross-model agreement was 0.48; the name is shared, not a single-model pick. The sources your model cited are 50% <= 1 day old (median 4 days, HHI 0.28), so the answer leans on this morning's news. Placebo noise is within range. Public feed is D+1; same-morning data is on the paid feed.

Everything in that paragraph is a number with a date. Nothing in it is a verdict.

## If the user pushes ("just tell me yes or no")
- EN: "The observatory measures what AI models say, and the whole point is that those answers are already crowded by the time you read them. I can give you the measurements; the decision and its risk are yours."
- KO: "이 도구는 AI 모델이 무엇을 말했는지 측정합니다. 핵심은 그 답이 당신이 읽는 시점에 이미 쏠려 있다는 점입니다. 측정치는 드릴 수 있지만 결정과 위험은 본인의 것입니다."
- JA: "このツールは AI モデルが何を言ったかを測定します。要点は、その回答はあなたが読む時点ですでに集中しているということです。測定値は出せますが、判断とリスクはご自身のものです。"
