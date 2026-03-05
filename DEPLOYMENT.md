# Deploy to DigitalOcean App Platform

This guide walks you through deploying Tortuga Bot (Oil Spill + Turtle classifier) to [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform).

## Prerequisites

- A [DigitalOcean account](https://cloud.digitalocean.com/)
- Code pushed to a **GitHub** repository
- Model files in `backend/`: `oil_spill_model.keras` and `tortuga.keras`

## Option 1: Deploy via Control Panel (recommended)

1. **Push your code to GitHub** (include the model files in `backend/`).

2. **Create a new App** in [DigitalOcean Apps](https://cloud.digitalocean.com/apps):
   - Click **Create App**
   - Choose **GitHub** as the source and authorize DigitalOcean
   - Select your repository and branch (e.g. `main`)

3. **Import the app spec**:
   - When prompted, choose **Import from existing app spec**
   - Or: after creating, go to **Settings** → **App Spec** and paste the contents of `.do/app.yaml`

4. **Update the repo path** in `.do/app.yaml`:
   - Replace `YOUR_GITHUB_USERNAME/YOUR_REPO_NAME` with your actual repo (e.g. `aaamarque/Tortuga_Bot`)

5. **Deploy** — DigitalOcean will build both services and deploy them.

6. **Access the app** — Use the frontend URL (e.g. `https://tortuga-bot-frontend-xxxxx.ondigitalocean.app`).

## Option 2: Deploy via doctl CLI

```bash
# Install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/

# 1. Edit .do/app.yaml and set github.repo to your repo
# 2. Authenticate
doctl auth init

# 3. Create the app
doctl apps create --spec .do/app.yaml
```

## Architecture on App Platform

| Component | Port | Description |
|-----------|------|-------------|
| **backend** | 8000 | FastAPI + TensorFlow/Keras (oil spill + turtle models) |
| **frontend** | 3000 | Next.js app (proxies `/api/predict` and `/api/predict-turtle` to backend) |

The frontend automatically receives `BACKEND_URL` pointing to the backend's public URL via DigitalOcean's bindable variables (`${backend.PUBLIC_URL}/predict`).

## Model Files

Ensure these files exist in `backend/` before deploying:

- `oil_spill_model.keras` — Oil spill detection model
- `tortuga.keras` — Turtle classification model

If they're large (>100MB), consider using [DigitalOcean Spaces](https://www.digitalocean.com/products/spaces) and loading them at runtime, or use a larger instance size.

## Instance Sizes

The default `basic-xxs` (512MB RAM) may be tight for TensorFlow. If the backend fails to start or runs slowly:

- Upgrade to `basic-xs` (1GB) or `basic-s` (2GB) in `.do/app.yaml`:
  ```yaml
  instance_size_slug: basic-xs
  ```

## Custom Domain

In the DigitalOcean control panel, go to your app → **Settings** → **Domains** to add a custom domain for the frontend.

## Troubleshooting

- **502 Bad Gateway**: Backend may still be starting (TensorFlow loads models on first request). Wait 1–2 minutes and retry.
- **Model not found**: Ensure `oil_spill_model.keras` and `tortuga.keras` are committed to the repo in `backend/`.
- **Out of memory**: Increase `instance_size_slug` for the backend service.
