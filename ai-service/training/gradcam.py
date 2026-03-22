import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import os

IMG_SIZE = (224, 224)

def occlusion_heatmap(model, img, step=32):
    h, w, _ = img.shape
    heat = np.zeros((h, w), dtype="float32")

    base_pred = model(np.expand_dims(img, 0), training=False).numpy()[0].max()

    for y in range(0, h, step):
        for x in range(0, w, step):
            occluded = img.copy()
            occluded[y:y+step, x:x+step] = 0

            p = model(np.expand_dims(occluded, 0), training=False).numpy()[0].max()
            heat[y:y+step, x:x+step] = base_pred - p

    heat = np.maximum(heat, 0)
    heat /= heat.max() + 1e-8
    return heat


def apply_gradcam(image_path, model, class_index, output_path):
    # Load and preprocess image
    img = Image.open(image_path).convert("RGB")
    img_resized = img.resize(IMG_SIZE)
    img_np = np.array(img_resized, dtype="float32")

    # Generate occlusion heatmap
    heatmap = occlusion_heatmap(model, img_np, step=24)

    # Overlay
    heatmap_resized = cv2.resize(heatmap, (img_np.shape[1], img_np.shape[0]))
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)

    superimposed = cv2.addWeighted(
        img_np.astype("uint8"), 0.6,
        heatmap_colored, 0.4,
        0
    )
    cv2.imwrite(output_path, cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))


# ---------- Streamlit / App Wrapper ----------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "food_freshness_v1_fixed.keras")

_model = None

def generate_gradcam(image_path, class_index, output_path="gradcam_result.png"):
    """
    Loads the model once, applies occlusion-based Grad-CAM,
    and returns the saved image path.
    """
    global _model

    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)

    apply_gradcam(image_path, _model, class_index, output_path)
    return output_path
