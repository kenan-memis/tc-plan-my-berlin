# RAGAs Evaluation — PlanMyBerlin (Hard #9)

This document summarizes the results of **Hard #9**: evaluating the RAG pipeline using **RAGAs**.

## Evaluation configuration
- **RAGAs metrics:** `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
- **Judge model:** `gpt-4o-mini`
- **TripProfile parsing:** `gpt-4o-mini` via OpenAI
- **Samples:** `8` Berlin trip queries
- **Retrieved contexts (`top_k_contexts`):** `24`

## Metric averages (from `hard9-final_summary.md`)
- **faithfulness:** `0.6719`
- **answer_relevancy:** `0.8529`
- **context_precision:** `0.5298`
- **context_recall:** `0.9464`

## How to interpret these results
- **Faithfulness (0.6719):** about 2/3 of the answer’s atomic claims are supported by the retrieved contexts. This indicates some remaining risk of unsupported details (hallucination-like behavior), but the system is not completely ungrounded.
- **Answer relevancy (0.8529):** answers are usually aligned with the user’s question and generally on-topic.
- **Context recall (0.9464):** the retriever often includes the needed information somewhere in the retrieved set (high coverage).
- **Context precision (0.5298):** the retrieved set contains a substantial amount of irrelevant/noisy chunks. This can indirectly reduce faithfulness (extra noise -> more opportunities for unsupported claims).

## Artifacts / where the raw results live
Run output is saved under:
- `planmyberlin/eval/results/hard9-final.json`
- `planmyberlin/eval/results/hard9-final_summary.md`

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

