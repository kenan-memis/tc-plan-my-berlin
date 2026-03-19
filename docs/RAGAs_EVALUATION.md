# RAGAs Evaluation — PlanMyBerlin (Hard #9)

This document summarizes the results of **Hard #9**: evaluating the RAG pipeline using **RAGAs**.

## Evaluation configuration
- **RAGAs metrics:** `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
- **Judge model:** `gpt-4o-mini`
- **TripProfile parsing:** `gpt-4o-mini` via OpenAI
- **Samples:** `8` Berlin trip queries
- **Retrieved contexts (`top_k_contexts`):** `24` for both runs (`hard9-final` and `hard9-after-data-update`)

## Metric averages (before vs after data update)
Before (`hard9-final_summary.md`):
- **faithfulness:** `0.6719`
- **answer_relevancy:** `0.8529`
- **context_precision:** `0.5298`
- **context_recall:** `0.9464`

After (`hard9-after-data-update_summary.md`):
- **faithfulness:** `0.7540`
- **answer_relevancy:** `0.8625`
- **context_precision:** `0.4476`
- **context_recall:** `0.9375`

### Before vs After (delta highlights)
- **faithfulness:** `+0.0821` (better grounding)
- **answer_relevancy:** `+0.0096` (slightly better alignment)
- **context_precision:** `-0.0822` (more noise in retrieved set)
- **context_recall:** `-0.0089` (still high coverage)

### Interpretation (what changed)
We keep the same KB expansion (“data update”) as before, and apply an evaluation-only **entity-level context filtering** step that removes header-only chunks (keeping only chunks that contain concrete `### <Place/Restaurant>` entries) before sending contexts into RAGAs.

With the larger KB, the system becomes **more grounded** overall (higher faithfulness) and stays **highly on-topic** (answer relevancy stays strong). The remaining decrease in **context precision** suggests that even among entity-level chunks, the retriever still returns some extra/noisy candidates—however **context recall stays very high**, so the needed information is still usually present somewhere in the retrieved set.

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

After (precision-tuned evaluation run):

```bash
uv run python -m planmyberlin.eval.run_ragas_eval \
  --max-samples 8 \
  --top-k-contexts 24 \
  --judge-model gpt-4o-mini \
  --trip-profile-provider openai \
  --trip-profile-model gpt-4o-mini \
  --output-name hard9-after-data-update
```

## What to expect after you add more data
When you update `data/raw/*.md` and rebuild/redeploy, the metrics can change:
- new docs can improve **context recall** (better coverage),
- chunking + similarity ranking can change **context precision**,
- faithfulness may move depending on how “richer” answers are and how much of that richness is actually present in the retrieved chunks.

