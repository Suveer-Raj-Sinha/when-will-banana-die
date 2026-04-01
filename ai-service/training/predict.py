"""
predict.py  —  Food Freshness Inference
========================================
Drop-in replacement for the original predict.py.

Changes vs v1:
  - Uses food_freshness_v2.keras  (fine-tuned model)
  - days_to_spoil is confidence-weighted interpolation, not random.randint
  - freshness_score uses a smoother formula
  - Cleaner separation between model logic and CLASS_LOGIC lookup
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import os

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(__file__))   # ai-service/
MODEL_PATH = os.path.join(BASE_DIR, "models", "food_freshness_v2.keras")
IMG_SIZE   = (224, 224)

# ─────────────────────────────────────────────
# PER-ITEM KNOWLEDGE BASE
# (min_days, max_days, storage_advice)
# min/max = expected shelf life at low/high freshness confidence
# ─────────────────────────────────────────────
CLASS_LOGIC = {
    "apples":      (3,  9,  "Store refrigerated or in a cool, dark place."),
    "banana":      (2,  7,  "Keep at room temperature away from direct sunlight."),
    "bittergroud": (2,  5,  "Refrigerate in a paper bag; use within a few days."),
    "capsicum":    (3,  7,  "Keep in the crisper drawer of the refrigerator."),
    "cucumber":    (1,  4,  "Refrigerate and consume quickly after cutting."),
    "okra":        (1,  4,  "Store in a paper bag in the refrigerator."),
    "oranges":     (3,  7,  "Keep at room temperature for a week, or refrigerate longer."),
    "potato":      (5, 12,  "Store in a cool, dark, well-ventilated place."),
    "tomato":      (1,  5,  "Keep at room temperature; refrigeration dulls flavour."),
}

# ─────────────────────────────────────────────
# MODEL (loaded once)
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# DAYS-LEFT ESTIMATE
# ─────────────────────────────────────────────
def _estimate_days(food_key: str, is_fresh: bool, confidence: float) -> int:
    """
    Confidence-weighted linear interpolation.

    For fresh items:
      confidence = 0.50  →  min_days   (barely fresh)
      confidence = 1.00  →  max_days   (clearly fresh)

    For rotten items:
      always 0
    """
    if food_key not in CLASS_LOGIC or not is_fresh:
        return 0

    min_d, max_d, _ = CLASS_LOGIC[food_key]
    c = max(0.5, min(1.0, confidence))        # clamp to [0.5, 1.0]
    t = (c - 0.5) / 0.5                       # normalise → [0, 1]
    return round(min_d + t * (max_d - min_d))


def _freshness_score(is_fresh: bool, confidence: float) -> int:
    """
    Maps confidence to a 0–100 freshness score.
      Fresh  :  score in 55–100  (higher confidence → higher score)
      Rotten :  score in  0– 45  (higher confidence it's rotten → lower score)
    """
    if is_fresh:
        return round(55 + confidence * 45)
    else:
        return round((1 - confidence) * 45)


# ─────────────────────────────────────────────
# MAIN INFERENCE FUNCTION
# ─────────────────────────────────────────────
def analyze_image(image_path: str) -> dict:
    """
    Runs inference on a single image and returns a result dict.

    Returns:
        {
          food             : str   – capitalised food name
          status           : str   – "Fresh" | "Rotten" | "Unknown"
          predicted_class  : str   – raw class label
          class_index      : int   – index into class_names list
          confidence_percent: float
          freshness_score  : int   – 0–100
          days_to_spoil    : int   – estimated days remaining (0 if rotten)
          advice           : str   – storage / usage advice
          note             : str | None  – low/medium confidence warning
        }
    """
    model = _load_model()

    # ── Load class names ──
    class_names_path = os.path.join(BASE_DIR, "models", "class_names.json")
    with open(class_names_path) as f:
        import json
        class_names = json.load(f)

    # ── Preprocess ──
    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = np.expand_dims(np.array(img, dtype="float32"), axis=0)

    # ── Predict ──
    preds      = model.predict(arr, verbose=0)[0]
    idx        = int(np.argmax(preds))
    label      = class_names[idx]
    confidence = float(preds[idx])

    # ── Decode label ──
    is_fresh = label.startswith("fresh")
    food_key = label.replace("fresh", "").replace("rotten", "")
    food     = food_key.capitalize()

    # ── Compute outputs ──
    days_left      = _estimate_days(food_key, is_fresh, confidence)
    freshness      = _freshness_score(is_fresh, confidence)
    confidence_pct = round(confidence * 100, 2)

    if food_key in CLASS_LOGIC:
        _, _, advice = CLASS_LOGIC[food_key]
        status = "Fresh" if is_fresh else "Rotten"
        if not is_fresh:
            advice = "Not safe to consume. Discard immediately."
    else:
        status = "Unknown"
        advice = "Item not in knowledge base."

    # ── Confidence note ──
    note = None
    if confidence_pct < 50:
        note = "Low confidence — retake the photo in better lighting."
    elif confidence_pct < 75:
        note = "Moderate confidence — result may vary."

    return {
        "food":              food,
        "status":            status,
        "predicted_class":   label,
        "class_index":       idx,
        "confidence_percent": confidence_pct,
        "freshness_score":   freshness,
        "days_to_spoil":     days_left,
        "advice":            advice,
        "note":              note,
    }


# ─────────────────────────────────────────────
# CLI TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_image = os.path.join(os.getcwd(), "test.png")
    print("Loading image from:", test_image)

    if not os.path.exists(test_image):
        print("Place an image named 'test.png' in the project root and re-run.")
    else:
        result = analyze_image(test_image)
        print("\nPrediction Result:")
        for k, v in result.items():
            print(f"  {k:22s}: {v}")
