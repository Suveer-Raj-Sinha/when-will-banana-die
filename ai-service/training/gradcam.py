import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import os

IMG_SIZE = (224, 224)


def occlusion_heatmap(model, img: np.ndarray, step: int = 24) -> np.ndarray:
    """
    Generates an occlusion-based saliency heatmap.

    Args:
        model : Loaded Keras model.
        img   : Float32 array (H x W x 3), already resized to IMG_SIZE.
        step  : Occlusion patch size in pixels.

    Returns:
        Normalised heatmap as float32 array (H x W), values in [0, 1].
    """
    h, w, _ = img.shape
    heat     = np.zeros((h, w), dtype="float32")
    base_pred = model(np.expand_dims(img, 0), training=False).numpy()[0].max()

    for y in range(0, h, step):
        for x in range(0, w, step):
            occluded = img.copy()
            occluded[y:y + step, x:x + step] = 0
            p = model(np.expand_dims(occluded, 0), training=False).numpy()[0].max()
            heat[y:y + step, x:x + step] = base_pred - p

    heat = np.maximum(heat, 0)
    heat /= heat.max() + 1e-8
    return heat


def apply_gradcam(
    image_path:   str,
    model,
    class_index:  int,
    output_path:  str,
    masked_array: np.ndarray | None = None,
) -> None:
    """
    Applies occlusion-based Grad-CAM and saves the superimposed result.

    Args:
        image_path   : Path to the original image (used when masked_array is None).
        model        : Loaded Keras model.
        class_index  : Predicted class index (kept for API compatibility).
        output_path  : Where to save the result PNG.
        masked_array : Optional (224x224x3) uint8 array from segment.py.
                       When provided, heatmap is computed on the masked image
                       but overlaid on top of it for a cleaner visualisation.
    """
    if masked_array is not None:
        img_np = masked_array.astype("float32")
    else:
        img    = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
        img_np = np.array(img, dtype="float32")

    heatmap         = occlusion_heatmap(model, img_np, step=24)
    heatmap_resized = cv2.resize(heatmap, (img_np.shape[1], img_np.shape[0]))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)

    superimposed = cv2.addWeighted(
        img_np.astype("uint8"), 0.6,
        heatmap_colored,        0.4,
        0,
    )
    cv2.imwrite(output_path, cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))


# ---------- Streamlit / App Wrapper ----------

BASE_DIR   = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "food_freshness_v1_fixed.keras")

_model = None


def generate_gradcam(
    image_path:   str,
    class_index:  int,
    output_path:  str  = "gradcam_result.png",
    masked_array: np.ndarray | None = None,
) -> str:
    """
    Loads the model once, applies occlusion-based Grad-CAM, returns saved path.

    Args:
        masked_array : If provided, Grad-CAM runs on the segmented image.
    """
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)

    apply_gradcam(image_path, _model, class_index, output_path, masked_array)
    return output_path
