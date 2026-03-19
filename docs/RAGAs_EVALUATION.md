# RAGAs Evaluation — PlanMyBerlin (Hard #9)

This document summarizes the results of **Hard #9**: evaluating the RAG pipeline using **RAGAs**.

## Evaluation configuration
- **RAGAs metrics:** `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
- **Judge model:** `gpt-4o-mini`
- **TripProfile parsing:** `gpt-4o-mini` via OpenAI
- **Samples:** `8` Berlin trip queries
- **Retrieved contexts (`top_k_contexts`):** `24`

## Metric averages (before vs after data update)
Before (`hard9-final_summary.md`):
- **faithfulness:** `0.6719`
- **answer_relevancy:** `0.8529`
- **context_precision:** `0.5298`
- **context_recall:** `0.9464`

After (`hard9-after-data-update_summary.md`):
- **faithfulness:** `0.7383`
- **answer_relevancy:** `0.8622`
- **context_precision:** `0.3312`
- **context_recall:** `0.9375`

### Before vs After (delta highlights)
- **faithfulness:** `+0.0664` (better grounding)
- **answer_relevancy:** `+0.0093` (slightly better alignment)
- **context_precision:** `-0.1986` (retrieval became noisier)
- **context_recall:** `-0.0089` (still high coverage)

### Interpretation (what changed)
After adding more knowledge base data, the system’s **faithfulness improved** (more answer claims were supported by retrieved contexts) and **answer relevancy stayed strong**. However, **context precision dropped significantly**, meaning the retriever returned more irrelevant/noisy chunks; this is a risk factor because extra noise can lead to unsupported details. Even with that precision drop, **context recall remained very high**, so the needed information is still usually present somewhere in the retrieved set, which helps the model stay grounded.

## Artifacts / where the raw results live
Run output is saved under:
- `planmyberlin/eval/results/hard9-final.json`
- `planmyberlin/eval/results/hard9-final_summary.md`
- `planmyberlin/eval/results/hard9-after-data-update_summary.md`

## How to reproduce
From the repo root (`plan-my-berlin/`):

```bash
uv run python -m planmyberlin.eval.run_ragas_eval \
  --max-samples 8 \
  --top-k-contexts 24 \
  --judge-model gpt-4o-mini \
  --trip-profile-provider openai \
  --trip-profile-model gpt-4o-mini \
  --output-name hard9-final
```

## What to expect after you add more data
When you update `data/raw/*.md` and rebuild/redeploy, the metrics can change:
- new docs can improve **context recall** (better coverage),
- chunking + similarity ranking can change **context precision**,
- faithfulness may move depending on how “richer” answers are and how much of that richness is actually present in the retrieved chunks.

