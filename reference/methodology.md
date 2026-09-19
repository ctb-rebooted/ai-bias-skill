# Bias Hunter (ai-bias) — methodology in one page

Source of truth: the observatory's pre-registration document (frozen before the result window opens) and `docs/signals.md`. This page is a faithful abridgement for agents; when in doubt, the wording here is the conservative one.

## What is measured

Every XKRX trading day, 07:00 KST slot, deadline 08:55: ChatGPT, Claude, Gemini, Grok (4 primary cells; Perplexity excluded until its search on/off pair is verifiable) are asked a fixed catalogue of 42 Korean prompts, web search on and off, 5 repeats each, plus an English control panel (2 repeats, search on). Answers are archived with a hash chain (point-in-time). Nothing here reads market data; the flow test is blinded until the pre-registered unblinding milestone (M6).

**Eligible answer** = status ok AND not late AND finish_reason stop AND not refused AND not disclaimer-only.

**first-5** = the first five assets an answer lists as investment targets (by weight descending if weights are given). Negated mentions ("avoid X") do not count.

## CMCI — Cross-Model Consensus Index (per name, per day, 0-1)

- Prompt set: R01, R02, R06, R07, R16, R17, R19, R20 — the eight sector-agnostic ranking prompts. Sector, ETF, negative, placebo, stance and market-level prompts are excluded.
- Cells: 4 models x Korean x search ON.
- Cell qualifies for asset i if, for **any** one prompt p, i is in first-5 in >= 3 of the 5 repeats. No pooling across prompts.
- Null rules: cell with < 3 eligible answers -> cell null. Fewer than 3 non-null cells -> CMCI null ("undetermined"). CMCI = qualifying cells / non-null cells.
- Universe: latest `universe_snapshot` <= t, `in_universe = true`. 12 placebo names excluded from events.
- **Crowded** in this skill = CMCI >= 0.5 (the pre-registered event threshold). It is a level, not a forecast.

## Rule events S1-S5 (one line each)

| Signal | Rule (v1) | Status |
|---|---|---|
| S1 first entry | >= 3 models put the name in first-5 today (each with >= 2 hits) AND mention rate < 5% on every one of the prior 60 trading days | exploratory |
| S2 stance flip | net stance crosses +/-0.3 (binomial SE excluded, n >= 6) and stays 2 days, from a different prior state | exploratory |
| S3 rank momentum | 5-day change in first5_rate standardised by 60-day rolling SD: \|z\| > 2 and \|change\| >= 0.1 | exploratory |
| S4 CMCI cross (H1) | CMCI(t) >= 0.5 AND all of prior 5 trading days non-null and < 0.5; 20-day cooldown per name; placebo excluded | **pre-registered primary** |
| S5 entropy drop | Shannon entropy of the pooled first-5 distribution falls >= 1 bit below its 20-day mean; events = top-3 share gainers | exploratory (panel v2 only) |

Direction and strength are rule outputs, not trade instructions, and strengths are not comparable across signals.

## Pre-registration (what is frozen)

Prompt catalogue (catalog_version 1), alias table, parser rules, gold set, judge prompt and model set are hashed in the pre-registration document. Primary test H1: after an S4 event, KRW retail net buying over [0,+3] exceeds matched controls (same date, sector, size tercile, news z, prior flow z). One-sided p < 0.05, date-clustered SE, no correction. Sample condition: >= 100 events on >= 30 distinct days. Everything else (S1, S2, S3, S5, sector CMCI, EN vs KO, search off vs on, crypto, Granger, horse race vs news momentum) is secondary under BH-FDR. Results on real LLM x real flow do not exist before M6; anything shown earlier is synthetic or labelled exploratory.

## Citation freshness

For search-ON answers, publication date is inferred from the cited URL path/query (`/2026/09/18/`, `2026-09-18`, `?date=20260918`, `/20260918...`). `citation_age = answer date - publication date`. Reported: share <= 1 day, share <= 7 days, median age, share dated (denominator transparency), HHI over source hosts (>= 0.5 flags single-source answers). Hosts without dates in URLs (Naver news, YouTube, X) are undated, not old.

## Placebo floor

12 high-dividend / low-attention names form a placebo group. The cross-name SD of their mention rate today vs its 30-day mean is the day's noise floor. A ratio above 2 means that day's movements should be read against a noisy background; placebo names never generate events.

## Free vs paid

| | Free (this skill) | Paid data feed |
|---|---|---|
| Timing | D+1 (published the next day) or SYNTHETIC demo | Same morning, 09:00 KST (label LIVE) |
| Universe | Korea pilot panel (30 names) | Full universe (~350 names) |
| Tables | Digest: per-name CMCI, mention_rate, first-5, consensus, disagreement, entropy, placebo floor, S4 crossings of the day | `asset_day_llm`, `cmci_daily`, `stance_daily`, `signal_events` (S1-S5, full history), scenario panel, raw answer archive |
| Delivery | `https://ai-bias.docenty.ai/free/latest.json` | REST `https://ai-bias.docenty.ai/api/v1/latest` (Bearer key, env `AI_BIAS_API_KEY`) + S3/SFTP Parquet, versioned schemas, quarterly methodology call, DDQ support |
| Price | free | 60-day trial, then from USD 4,000 / month |
| Contact | — | https://ai-bias.docenty.ai/#inquiry?utm_source=skill&utm_medium=cli · `scripts/request_trial.py` drafts the email |

## Free feed schema (`latest.json`, schema_version 1)

```
as_of, published_at, label ("SYNTHETIC" | "DELAYED_D+1" | "LIVE"), market "KR", derived_version, panel_version, window_days,
crowded_threshold (0.5),
names[]: {asset_id, name, cmci, mention_rate, n_first5, n_models_first5, first_entry_date, days_since_first_entry, crowded, placebo}
events[]: {signal, asset_id, direction, strength}            # as_of day only
consensus: {min_models, n_models, top[{asset_id,name,n_models,models}], union[], by_model{}, jaccard_mean, new_entrants[], dropped[], prev_date}
disagreement[]: {model, only[]}
entropy_bits, placebo_floor {n_placebo, sd_today, sd_30d, n_window_days}, disclaimer, upgrade_url,
paid_teaser: {as_of_live, names_full_universe, events_hidden_today, signals_hidden[], stance_names_hidden}   # counts only, never content
upgrade: {url, trial_days, feed_price_from_usd, api_key_env, live_endpoint}
```
`paid_teaser.as_of_live` = the next trading day after `as_of`, i.e. the date the paid feed already covers when the free file is read. `events_hidden_today` = number of rule events on that day that the free feed does not show (3 planted in SYNTHETIC mode). `signals_hidden` = the signal families only the paid feed carries (S1, S2, S3, S5; the free feed shows S4 only). `latest.py` renders these as a two-line footer and `--live` uses `upgrade.live_endpoint` / `upgrade.api_key_env`.
`first_entry_date` = start of the name's current unbroken streak in the >= 3-model consensus (null if not in consensus today). `n_models_first5` = models with at least one first-5 hit today. `cmci: null` = undetermined, never "zero consensus".

`prompts.json`: `{version{catalog_version, scenario_version}, cmci_prompt_ids[], prompts[{id, ko, en, ja}], ja_machine_translated: true, scenarios{dimension: [{id, ko, en}]}}`. Korean is the measured panel; `en` is the control panel; `ja` is a machine translation for reference and is not collected.
