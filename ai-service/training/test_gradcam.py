import os
import tensorflow as tf
from gradcam import apply_gradcam

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "food_freshness_v1_fixed.keras")

model = tf.keras.models.load_model(MODEL_PATH)

IMAGE_PATH = os.path.join(os.getcwd(), "test.png")
OUTPUT_PATH = "gradcam_result.png"
CLASS_INDEX = 0

if not os.path.exists(IMAGE_PATH):
    print("Place an image named 'test.png' in the project root.")
else:
    apply_gradcam(IMAGE_PATH, model, CLASS_INDEX, OUTPUT_PATH)
    print("Grad-CAM image saved as:", OUTPUT_PATH)
