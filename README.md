# 🍎 Food Freshness Analyzer

> An ML-powered food freshness analysis system for reducing household food waste.

Upload an image of any fruit or vegetable and get instant freshness status, estimated days left before spoilage, confidence score, and storage advice — powered by a fine-tuned MobileNetV2 model.

---

## Features

- **Freshness Classification** — detects fresh vs rotten across 9 food types
- **Shelf Life Estimation** — confidence-weighted days-left prediction (no random guessing)
- **Grad-CAM Visualization** — shows exactly which part of the image the model focused on
- **REST API** — full FastAPI backend with scan history and analytics
- **Scan History** — every prediction saved to SQLite with filtering and pagination
- **Batch Processing** — analyze up to 10 images in a single API request
- **Analytics Endpoint** — aggregated stats for dashboards

---

## Supported Foods

| Fresh | Rotten |
|-------|--------|
| Apples, Banana, Bitter Gourd | Rotten Apples, Rotten Banana, Rotten Bitter Gourd |
| Capsicum, Cucumber, Okra | Rotten Capsicum, Rotten Cucumber, Rotten Okra |
| Oranges, Potato, Tomato | Rotten Oranges, Rotten Potato, Rotten Tomato |

---

## Project Structure

```
When-will-banana-die/
├── run.py                        # Start the FastAPI server
├── requirements.txt
└── ai-service/
    ├── api/
    │   ├── __init__.py
    │   └── main.py               # FastAPI app — all endpoints
    ├── training/
    │   ├── train_v2.py           # Model training (two-phase fine-tuning)
    │   ├── predict.py            # Inference logic
    │   ├── app.py                # Streamlit UI
    │   └── gradcam.py            # Grad-CAM / occlusion heatmap
    └── models/
        ├── food_freshness_v2.keras
        ├── class_names.json
        ├── eval_report.txt
        ├── confusion_matrix.png
        └── training_history.png
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/When-will-banana-die.git
cd When-will-banana-die
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Training the Model

Place your dataset in `ai-service/data/Train/` with one subfolder per class (e.g. `freshbanana/`, `rottenbanana/`).

```bash
python ai-service/training/train_v2.py
```

This runs a **two-phase fine-tuning** process:

- **Phase 1** — MobileNetV2 frozen, only the classification head trains (lr = 1e-3)
- **Phase 2** — Top layers of MobileNetV2 unfrozen and fine-tuned (lr = 1e-5)

After training, the following are saved to `ai-service/models/`:

| File | Description |
|------|-------------|
| `food_freshness_v2.keras` | Trained model |
| `class_names.json` | Class label order |
| `eval_report.txt` | Per-class precision, recall, F1 |
| `confusion_matrix.png` | Visual prediction accuracy grid |
| `training_history.png` | Accuracy and loss curves across both phases |

---

## Running the App

### Streamlit UI (quick visual test)

```bash
cd ai-service/training
streamlit run app.py
```

Opens at: **http://localhost:8501**

### FastAPI Backend

```bash
python run.py
```

Opens at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

> Both can run at the same time on their respective ports.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict` | Analyse a single image |
| `POST` | `/predict/batch` | Analyse up to 10 images |
| `GET` | `/history` | All past scans (supports `?food=` and `?status=` filters) |
| `GET` | `/history/{id}` | Single scan by ID |
| `DELETE` | `/history/{id}` | Delete a scan |
| `GET` | `/stats` | Aggregated stats (totals, averages, top food) |
| `GET` | `/health` | Health check |

### Example — single prediction

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@banana.jpg"
```

```json
{
  "scan_id": "a1b2c3d4-...",
  "created_at": "2026-04-01T06:30:00",
  "food": "Banana",
  "status": "Fresh",
  "predicted_class": "freshbanana",
  "confidence_percent": 94.7,
  "freshness_score": 84,
  "days_to_spoil": 5,
  "advice": "Keep at room temperature away from direct sunlight.",
  "note": null
}
```

---

## ML Architecture

- **Base model** — MobileNetV2 pretrained on ImageNet
- **Fine-tuning** — Top 54 layers unfrozen in phase 2
- **Regularization** — Dropout (0.3) + data augmentation (flip, rotate, zoom, brightness)
- **Explainability** — Occlusion-based Grad-CAM heatmap
- **Shelf life** — Confidence-weighted linear interpolation (not random)

---

## Requirements

```
tensorflow
numpy
Pillow
opencv-python
scikit-learn
matplotlib
fastapi
uvicorn[standard]
python-multipart
aiofiles
streamlit
```

---

## Roadmap

- [ ] React frontend with mobile camera capture
- [ ] Expiry calendar with iCal export
- [ ] Recipe suggestions based on expiring items
- [ ] Analytics dashboard
- [ ] Docker container

---

## License

MIT
