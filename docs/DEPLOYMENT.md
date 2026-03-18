# Deployment — PlanMyBerlin on GCP Cloud Run

This document describes how to deploy **PlanMyBerlin** to **Google Cloud Run** using the container setup in this repo.

## Assumptions
- You are using **Google Cloud Run (managed)**.
- You have a Google Cloud project and permissions to deploy containers.
- You store secrets in **Secret Manager**.
- The container image is built from the repo root at `kmemis-AE.2.5/` (this folder is your project).

## 1) Build & push the container image

From the repo root (`plan-my-berlin/`):

```bash
# Build
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/planmyberlin
```

If you prefer Artifact Registry (recommended):
```bash
gcloud builds submit --tag $AR_REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$AR_REPOSITORY/planmyberlin
```

## 2) Deploy with “proper” scaling (Hard #1)

PlanMyBerlin is designed to run with:
- `min-instances = 1` (keep a warm instance during demo)
- `max-instances = 1` (avoid parallel cold starts)
- `concurrency = 50` (Streamlit loads many static assets and uses long-polling; too-low values can cause `429` and broken UI)

Note: Cloud Run’s `concurrency` defaults can still allow scaling to multiple instances unless you set `--min-instances` and `--max-instances` explicitly on deploy.

Example deploy command (replace image + region):

```bash
gcloud run deploy planmyberlin \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/planmyberlin \
  --region $GCP_REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --min-instances 1 \
  --max-instances 1 \
  --concurrency 50
```

## 3) Configure secrets (Secret Manager)

At minimum, the app needs:
- `OPENAI_API_KEY` (used for embeddings + TripProfile parsing when OpenAI is selected)

If you plan to use Gemini parsing from the UI dropdown, also set:
- `GEMINI_API_KEY`

Example using Secret Manager (adjust secret names and versions):

```bash
gcloud run deploy planmyberlin \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/planmyberlin \
  --region $GCP_REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --min-instances 1 \
  --max-instances 1 \
  --concurrency 1 \
  --set-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest
```

## 4) Important note about vectorstore ingest

In this deployment, the container entrypoint runs:

- `python -m planmyberlin.rag.ingest`

on **every container start** (Option A1).

This guarantees that the production knowledge base matches the current repo’s `data/raw/*.md` content baked into the image, and avoids “stale embeddings” during your presentation.

Because the ingest is fast (your local run was ~1–2 seconds), it is safe for demo readiness.

## 5) Verify after deploy

After Cloud Run reports `READY`, open the service URL in a browser and:
1. Generate a plan with a simple request (e.g. “2 days, low budget, Kreuzberg and Mitte”).
2. Confirm the UI loads (it should run ingestion once on the first boot).
3. Optionally test Gemini parsing by selecting Gemini in the dropdown (requires `GEMINI_API_KEY`).

