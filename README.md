# Tortuga Bot

ML-powered image classification app with two models: **Oil Spill Detection** (satellite/RGB imagery) and **Turtle Classification** (marine life). Built with Next.js, React, and FastAPI.

## Features

- **Oil Spill Detector** — Upload satellite or aerial images to detect oil spills using a CNN+LSTM model
- **Turtle Classifier** — Upload images to detect turtles in marine environments
- **Confidence scores & probabilities** — See predictions with class probabilities and inference time
- **Modern UI** — Clean, responsive interface with drag-and-drop upload

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.10+ |
| **ML** | TensorFlow/Keras, OpenCV |

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Browser   │────▶│  Next.js (React) │────▶│  FastAPI        │
│   (UI)      │     │  API Routes      │     │  + Keras       │
└─────────────┘     │  (proxy)         │     │  Models        │
                    └──────────────────┘     └─────────────────┘
```

- **Frontend**: Next.js serves the React app and proxies API requests to avoid CORS
- **Backend**: FastAPI loads Keras models, runs inference, and returns JSON predictions

## Quick Start

### Prerequisites

- Python 3.10+ with pip
- Node.js 18+ with npm

### 1. Clone the repo

```bash
git clone https://github.com/aaamarque/Tortuga_Bot.git
cd Tortuga_Bot
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### 3. Start the frontend

In a **new terminal**:

```bash
cd oil_webappd
npm install
npm run dev
```

### 4. Open the app

Go to [http://localhost:3000](http://localhost:3000) and use the **Oil Spill** or **Turtle** tab to upload an image.

## Project Structure

```
├── backend/
│   ├── server.py          # FastAPI app with /predict and /predict-turtle
│   ├── requirements.txt
│   ├── oil_spill_model.keras
│   └── tortuga.keras
├── oil_webappd/           # Next.js frontend
│   ├── app/
│   │   ├── page.tsx       # Oil Spill Detector
│   │   ├── turtle/        # Turtle Classifier
│   │   └── api/           # Proxy routes (predict, predict-turtle)
│   └── components/
└── RUN.md                 # Detailed run instructions
```

## Model Files

Place the models in the `backend/` folder:

- `oil_spill_model.keras` — Oil spill detection
- `tortuga.keras` — Turtle classification
If you have them elsewhere:

```bash
cp /path/to/oil_spill_model.keras backend/oil_spill_model.keras
cp /path/to/tortuga.keras backend/tortuga.keras
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/predict` | POST | Oil spill detection (multipart/form-data, field: `file`) |
| `/predict-turtle` | POST | Turtle classification (multipart/form-data, field: `file`) |

**Response format:**

```json
{
  "label": "turtle" | "no_turtle",
  "confidence": 0.95,
  "probs": { "turtle": 0.95, "no_turtle": 0.05 },
  "inference_ms": 42
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://127.0.0.1:8000/predict` | FastAPI base URL (proxy target) |

Copy `oil_webappd/.env.local.example` to `oil_webappd/.env.local` to customize.


