"""
Oil Spill Detection FastAPI server.
Loads the Keras model at startup and exposes POST /predict for image classification.
"""
import time
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model

# Model paths relative to this script
MODEL_PATH = Path(__file__).resolve().parent / "oil_spill_model.keras"
TURTLE_MODEL_PATH = Path(__file__).resolve().parent / "tortuga.keras"

# Load models once at startup
model = None
turtle_model = None


def get_model():
    global model
    if model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Copy oil_spill_model.keras into the backend/ folder."
            )
        model = load_model(MODEL_PATH)
    return model


def get_turtle_model():
    global turtle_model
    if turtle_model is None:
        if not TURTLE_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Turtle model not found at {TURTLE_MODEL_PATH}. "
                "Ensure tortuga.keras is in the backend/ folder."
            )
        turtle_model = load_model(TURTLE_MODEL_PATH)
    return turtle_model


app = FastAPI(title="Oil Spill Detection API")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


async def _predict_impl(file: UploadFile):
    """
    Accept multipart upload with field name "file".
    Returns classification: oil_spill or no_oil_spill with confidence and probs.
    """
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No file provided"})

    try:
        contents = await file.read()
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"error": f"Failed to read file: {str(e)}"}
        )

    if not contents:
        return JSONResponse(status_code=400, content={"error": "Empty file"})

    try:
        # Decode image bytes (PIL gives RGB directly)
        pil_img = Image.open(BytesIO(contents)).convert("RGB")
        img = np.array(pil_img, dtype=np.uint8)

        # Resize to 150x150
        pil_img = pil_img.resize((150, 150), Image.Resampling.LANCZOS)
        img = np.array(pil_img, dtype=np.uint8)

        # Normalize to float32 / 255.0
        img = img.astype(np.float32) / 255.0

        # Reshape to (1, 1, 150, 150, 3) for CNN+LSTM (time dimension = 1)
        img = img.reshape(1, 1, 150, 150, 3)

        # Run inference
        start_ms = time.perf_counter()
        prediction = get_model().predict(img, verbose=0)
        inference_ms = int((time.perf_counter() - start_ms) * 1000)

        # Assume output shape (1, 2) or (2,); index 0 = Non Oil Spill, index 1 = Oil Spill
        probs_flat = prediction.flatten()
        if len(probs_flat) < 2:
            return JSONResponse(
                status_code=500, content={"error": "Unexpected model output shape"}
            )

        no_oil_prob = float(probs_flat[0])
        oil_prob = float(probs_flat[1])

        # Model outputs probabilities (softmax); use as-is
        predicted_idx = int(np.argmax(probs_flat))
        label = "oil_spill" if predicted_idx == 1 else "no_oil_spill"
        confidence = oil_prob if predicted_idx == 1 else no_oil_prob

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "probs": {
                "oil_spill": round(oil_prob, 4),
                "no_oil_spill": round(no_oil_prob, 4),
            },
            "inference_ms": inference_ms,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/predict")
@app.post("/")  # Fallback when ingress strips path to /
async def predict(file: UploadFile = File(...)):
    """Oil spill detection. POST / and POST /predict both work."""
    return await _predict_impl(file)


@app.post("/predict-turtle")
async def predict_turtle(file: UploadFile = File(...)):
    """
    Accept multipart upload with field name "file".
    Returns classification: turtle or no_turtle with confidence and probs.
    Uses tortuga.keras model.
    """
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No file provided"})

    try:
        contents = await file.read()
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"error": f"Failed to read file: {str(e)}"}
        )

    if not contents:
        return JSONResponse(status_code=400, content={"error": "Empty file"})

    try:
        pil_img = Image.open(BytesIO(contents)).convert("RGB")
        turtle_m = get_turtle_model()
        input_shape = turtle_m.input_shape

        # Infer target size from model input (e.g. 150, 224)
        if len(input_shape) == 5:
            h, w = int(input_shape[2]), int(input_shape[3])
        else:
            h, w = int(input_shape[1]), int(input_shape[2])
        pil_img = pil_img.resize((w, h), Image.Resampling.LANCZOS)
        img = np.array(pil_img, dtype=np.uint8)
        img = img.astype(np.float32) / 255.0

        # Reshape: (1, H, W, 3) for CNN or (1, 1, H, W, 3) for CNN+LSTM
        if len(input_shape) == 5:
            img = img.reshape(1, 1, h, w, 3)
        else:
            img = img.reshape(1, h, w, 3)

        start_ms = time.perf_counter()
        prediction = turtle_m.predict(img, verbose=0)
        inference_ms = int((time.perf_counter() - start_ms) * 1000)

        probs_flat = prediction.flatten()

        # Handle sigmoid output (single value): turtle_prob = p, no_turtle_prob = 1-p
        if len(probs_flat) == 1:
            turtle_prob = float(probs_flat[0])
            no_turtle_prob = 1.0 - turtle_prob
        elif len(probs_flat) >= 2:
            no_turtle_prob = float(probs_flat[0])
            turtle_prob = float(probs_flat[1])
        else:
            return JSONResponse(
                status_code=500, content={"error": "Unexpected model output shape"}
            )

        predicted_idx = 1 if turtle_prob >= no_turtle_prob else 0
        label = "turtle" if predicted_idx == 1 else "no_turtle"
        confidence = turtle_prob if predicted_idx == 1 else no_turtle_prob

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "probs": {
                "turtle": round(turtle_prob, 4),
                "no_turtle": round(no_turtle_prob, 4),
            },
            "inference_ms": inference_ms,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
