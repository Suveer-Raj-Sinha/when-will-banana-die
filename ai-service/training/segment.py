import numpy as np
import cv2
import torch
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet50, DeepLabV3_ResNet50_Weights
from PIL import Image

IMG_SIZE = (224, 224)
BACKGROUND_CLASS = 0
_model = None


def _load_model():
    global _model
    if _model is None:
        weights = DeepLabV3_ResNet50_Weights.DEFAULT
        _model  = deeplabv3_resnet50(weights=weights)
        _model.eval()
        if torch.cuda.is_available():
            _model = _model.cuda()
    return _model


def _strip_uniform_dark_border(img_np: np.ndarray,
                                dark_thresh: int = 30,
                                min_dark_fraction: float = 0.95
                                ) -> tuple[np.ndarray, tuple]:
    """
    Strips only rows/cols where ≥95% of pixels are uniformly dark (value < 30).
    This catches the thin Streamlit panel border (~3px) without over-cropping
    images that have a legitimately dark background (e.g. banana on dark UI).
    """
    grey = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    h, w = grey.shape

    top = 0
    for r in range(h):
        if (grey[r, :] < dark_thresh).mean() >= min_dark_fraction:
            top = r + 1
        else:
            break

    bot = h - 1
    for r in range(h - 1, -1, -1):
        if (grey[r, :] < dark_thresh).mean() >= min_dark_fraction:
            bot = r - 1
        else:
            break

    left = 0
    for c in range(w):
        if (grey[:, c] < dark_thresh).mean() >= min_dark_fraction:
            left = c + 1
        else:
            break

    right = w - 1
    for c in range(w - 1, -1, -1):
        if (grey[:, c] < dark_thresh).mean() >= min_dark_fraction:
            right = c - 1
        else:
            break

    if top >= bot or left >= right:
        return img_np, (0, h - 1, 0, w - 1)

    cropped = img_np[top:bot + 1, left:right + 1]
    return cropped, (top, bot, left, right)


def _has_light_background(img_np: np.ndarray, threshold: int = 180) -> bool:
    """True if image edges are predominantly bright (white/off-white background)."""
    grey   = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    h, w   = grey.shape
    border = max(8, h // 20)
    edges  = np.concatenate([
        grey[:border,  :].ravel(),
        grey[-border:, :].ravel(),
        grey[:,  :border].ravel(),
        grey[:, -border:].ravel(),
    ])
    return float(edges.mean()) > threshold


def _floodfill_light_bg(img_np: np.ndarray) -> np.ndarray:
    """
    Flood-fills white/off-white background from all bright border pixels.
    Only used when _has_light_background() is True.
    """
    grey  = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    h, w  = grey.shape

    _, binary = cv2.threshold(grey, 180, 255, cv2.THRESH_BINARY)
    canvas    = binary.copy()
    ff_mask   = np.zeros((h + 2, w + 2), np.uint8)

    for x in range(0, w, 2):
        for y_e in [0, h - 1]:
            if canvas[y_e, x] == 255:
                cv2.floodFill(canvas, ff_mask, (x, y_e), 128,
                              loDiff=20, upDiff=20,
                              flags=cv2.FLOODFILL_FIXED_RANGE)
    for y in range(0, h, 2):
        for x_e in [0, w - 1]:
            if canvas[y, x_e] == 255:
                cv2.floodFill(canvas, ff_mask, (x_e, y), 128,
                              loDiff=20, upDiff=20,
                              flags=cv2.FLOODFILL_FIXED_RANGE)

    bg_mask    = (canvas == 128).astype(np.uint8)
    fruit_mask = (1 - bg_mask).astype(np.uint8)

    # Close gaps between fruit pieces (e.g. between banana fingers)
    kernel     = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    fruit_mask = cv2.morphologyEx(fruit_mask, cv2.MORPH_CLOSE, kernel)
    return fruit_mask


def _grabcut_fallback(img_np: np.ndarray) -> np.ndarray:
    """Two-pass GrabCut for dark/complex backgrounds."""
    h, w      = img_np.shape[:2]
    mask      = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    mx, my    = int(w * 0.15), int(h * 0.15)
    rect      = (mx, my, w - 2 * mx, h - 2 * my)
    try:
        cv2.grabCut(img_np, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        cv2.grabCut(img_np, mask, None, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_MASK)
        result = np.where(
            (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0
        ).astype(np.uint8)
        # Close gaps between parts of the same fruit
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
        result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        return result
    except Exception:
        fb = np.zeros((h, w), np.uint8)
        cv2.ellipse(fb, (w // 2, h // 2), (w // 3, h // 3), 0, 0, 360, 1, -1)
        return fb


def _smooth_mask(binary_mask: np.ndarray) -> np.ndarray:
    """Smooth edges — close only, no dilation."""
    mask = binary_mask.astype(np.uint8)
    k    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    mask = cv2.GaussianBlur(mask.astype(np.float32), (11, 11), 0)
    return (mask > 0.4).astype(np.uint8)


def _largest_component(binary_mask: np.ndarray) -> np.ndarray:
    """Keep only the largest connected region."""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
    if n <= 1:
        return binary_mask
    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    return (labels == largest).astype(np.uint8)


def segment_fruit(image_path: str) -> tuple[np.ndarray, np.ndarray, bool]:
    """
    Segments fruit/vegetable from background.

    Steps:
      1. Strip uniform dark border (Streamlit panel frame, ~3px).
      2. Try DeepLabV3 on cleaned image.
      3a. Light/white bg → flood-fill with large close kernel to bridge fruit gaps.
      3b. Dark/complex bg → two-pass GrabCut with large close kernel.
      4. Smooth edges, keep largest component.
    """
    model = _load_model()

    img        = Image.open(image_path).convert("RGB")
    img_resize = img.resize(IMG_SIZE)
    img_np     = np.array(img_resize, dtype=np.uint8)

    # ── Step 1: strip uniform dark border ────────────────────────────────────
    img_clean, (top, bot, left, right) = _strip_uniform_dark_border(img_np)

    # ── Step 2: DeepLabV3 ─────────────────────────────────────────────────────
    clean_pil  = Image.fromarray(img_clean).resize(IMG_SIZE)
    preprocess = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    inp = preprocess(clean_pil).unsqueeze(0)
    if torch.cuda.is_available():
        inp = inp.cuda()

    with torch.no_grad():
        out = model(inp)["out"][0]

    pred_mask        = out.argmax(0).cpu().numpy()
    foreground_mask  = (pred_mask != BACKGROUND_CLASS).astype(np.uint8)
    foreground_ratio = foreground_mask.sum() / foreground_mask.size

    # ── Step 3: fallback ──────────────────────────────────────────────────────
    if foreground_ratio < 0.02:
        # Run fallback on clean image resized to 224
        clean_224 = np.array(Image.fromarray(img_clean).resize(IMG_SIZE), dtype=np.uint8)
        if _has_light_background(clean_224):
            foreground_mask = _floodfill_light_bg(clean_224)
        else:
            foreground_mask = _grabcut_fallback(clean_224)

    # ── Step 4: post-process ──────────────────────────────────────────────────
    foreground_mask = _smooth_mask(foreground_mask)
    foreground_mask = _largest_component(foreground_mask)

    if foreground_mask.sum() / foreground_mask.size < 0.01:
        return img_np, np.zeros_like(img_np), False

    # Place mask back onto full IMG_SIZE canvas
    full_mask = np.zeros((IMG_SIZE[1], IMG_SIZE[0]), np.uint8)
    mh = min(foreground_mask.shape[0], bot - top + 1)
    mw = min(foreground_mask.shape[1], right - left + 1)
    resized_mask = cv2.resize(foreground_mask, (mw, mh))
    full_mask[top:top + mh, left:left + mw] = resized_mask

    mask_3ch    = np.stack([full_mask] * 3, axis=-1)
    masked_img  = (img_np * mask_3ch).astype(np.uint8)
    mask_visual = (mask_3ch * 255).astype(np.uint8)

    return masked_img, mask_visual, True
