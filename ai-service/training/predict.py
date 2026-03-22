import tensorflow as tf
import numpy as np
from PIL import Image
import os
import random

# Absolute-safe paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # ai-service/
MODEL_PATH = os.path.join(BASE_DIR, "models", "food_freshness_v1.keras")
DATA_DIR = os.path.join(BASE_DIR, "data", "Train")

IMG_SIZE = (224, 224)

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Load class names from folders
class_names = sorted([
    d for d in os.listdir(DATA_DIR)
    if os.path.isdir(os.path.join(DATA_DIR, d))
])

# Smart interpretation layer
CLASS_LOGIC = {
    "apples": (5, 7, "Store in a cool place."),
    "banana": (4, 6, "Keep at room temperature."),
    "bittergroud": (3, 5, "Use for cooking soon."),
    "capsicum": (4, 6, "Good for salads and cooking."),
    "cucumber": (2, 4, "Best consumed quickly."),
    "okra": (2, 4, "Use while fresh."),
    "oranges": (3, 5, "Can be stored a few more days."),
    "potato": (7, 10, "Store in a dark, cool place."),
    "tomato": (2, 4, "Use soon for best taste.")
}

def analyze_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE)

    arr = np.array(img)
    arr = np.expand_dims(arr, axis=0)

    preds = model.predict(arr)[0]
    idx = int(np.argmax(preds))
    label = class_names[idx]
    confidence = float(preds[idx])

    is_fresh = label.startswith("fresh")
    food_key = label.replace("fresh", "").replace("rotten", "")
    food = food_key.capitalize()

    # Defaults
    freshness_score = 0
    days_left = 0
    advice = "Unsupported item."

    if food_key in CLASS_LOGIC:
        min_d, max_d, base_advice = CLASS_LOGIC[food_key]

        if is_fresh:
            freshness_score = int(70 + confidence * 30)   # 70–100
            days_left = random.randint(min_d, max_d)
            advice = base_advice
            status = "Fresh"
        else:
            freshness_score = int(confidence * 40)        # 0–40
            days_left = 0
            advice = "Not safe to consume."
            status = "Rotten"
    else:
        status = "Unknown"

    # Confidence-based note
    note = None
    confidence_percent = round(confidence * 100, 2)
    if confidence_percent < 50:
        note = "Low confidence. Please retake the image in better lighting."
    elif confidence_percent < 80:
        note = "Moderate confidence. Result may vary."

    return {
    "food": food,
    "status": status,
    "predicted_class": label,
    "class_index": idx,   # <--- add this
    "confidence_percent": confidence_percent,
    "freshness_score": freshness_score,
    "days_to_spoil": days_left,
    "advice": advice,
    "note": note
}



# CLI Test
if __name__ == "__main__":
    test_image = os.path.join(os.getcwd(), "test.png")

    print("Loading image from:", test_image)

    if not os.path.exists(test_image):
        print("Place an image named 'test.png' in the project root.")
    else:
        result = analyze_image(test_image)
        print("\nPrediction Result:\n", result)
