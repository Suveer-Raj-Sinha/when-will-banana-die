"""
predict.py  —  Food Freshness Inference
========================================
Run from project root for a CLI test:
    cd ai-service/training
    python predict.py
"""

import tensorflow as tf
import numpy as np
import json
import os
import sys
from PIL import Image

BASE_DIR   = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "food_freshness_v2.keras")
IMG_SIZE   = (224, 224)

sys.path.insert(0, os.path.dirname(__file__))
from recipes import get_storage_tips

# ─────────────────────────────────────────────
# SHELF LIFE RANGES  (min_days, max_days)
# ─────────────────────────────────────────────
SHELF_LIFE = {
    "apples":      (3,  9),
    "banana":      (2,  7),
    "bittergroud": (2,  5),
    "capsicum":    (3,  7),
    "cucumber":    (1,  4),
    "okra":        (1,  4),
    "oranges":     (3,  7),
    "potato":      (5, 12),
    "tomato":      (1,  5),
}

_model = None

def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}.\n"
                "Run ai-service/training/train_v2.py first."
            )
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def _estimate_days(food_key: str, is_fresh: bool, confidence: float) -> int:
    if food_key not in SHELF_LIFE or not is_fresh:
        return 0
    min_d, max_d = SHELF_LIFE[food_key]
    c = max(0.5, min(1.0, confidence))
    t = (c - 0.5) / 0.5
    return round(min_d + t * (max_d - min_d))


def _freshness_score(is_fresh: bool, confidence: float) -> int:
    if is_fresh:
        return round(55 + confidence * 45)
    else:
        return round((1 - confidence) * 45)


def analyze_image(image_path: str) -> dict:
    model = _load_model()

    class_names_path = os.path.join(BASE_DIR, "models", "class_names.json")
    with open(class_names_path) as f:
        class_names = json.load(f)

    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = np.expand_dims(np.array(img, dtype="float32"), axis=0)

    preds      = model.predict(arr, verbose=0)[0]
    idx        = int(np.argmax(preds))
    label      = class_names[idx]
    confidence = float(preds[idx])

    is_fresh = label.startswith("fresh")
    food_key = label.replace("fresh", "").replace("rotten", "")
    food     = food_key.capitalize()

    days_left      = _estimate_days(food_key, is_fresh, confidence)
    freshness      = _freshness_score(is_fresh, confidence)
    confidence_pct = round(confidence * 100, 2)

    tips   = get_storage_tips(food_key)
    advice = tips.get("short", "Consume soon.")

    if not is_fresh:
        advice = "Not safe to consume. Discard immediately."
        status = "Rotten"
    elif food_key in SHELF_LIFE:
        status = "Fresh"
    else:
        status = "Unknown"
        advice = "Item not in knowledge base."

    note = None
    if confidence_pct < 50:
        note = "Low confidence — retake the photo in better lighting."
    elif confidence_pct < 75:
        note = "Moderate confidence — result may vary."

    return {
        "food":               food,
        "food_key":           food_key,
        "status":             status,
        "predicted_class":    label,
        "class_index":        idx,
        "confidence_percent": confidence_pct,
        "freshness_score":    freshness,
        "days_to_spoil":      days_left,
        "advice":             advice,
        "storage_tips":       tips,
        "note":               note,
    }


if __name__ == "__main__":
    test_image = os.path.join(os.getcwd(), "test.jpg")
    print("Loading image from:", test_image)
    if not os.path.exists(test_image):
        print("Place an image named 'test.jpg' in the project root and re-run.")
    else:
        result = analyze_image(test_image)
        print("\nPrediction Result:")
        for k, v in result.items():
            print(f"  {k:22s}: {v}")
