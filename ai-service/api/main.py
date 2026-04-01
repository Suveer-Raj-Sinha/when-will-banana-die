"""
main.py  —  Food Freshness REST API
=====================================
Run from the project root:
    uvicorn ai-service.api.main:app --reload --port 8000

Swagger UI (auto-generated docs):
    http://localhost:8000/docs

Endpoints:
    POST   /predict           – single image analysis
    POST   /predict/batch     – up to 10 images at once
    GET    /history           – paginated scan history
    GET    /history/{id}      – single scan
    DELETE /history/{id}      – delete a scan
    GET    /stats             – summary stats for dashboard
    GET    /health            – health check
"""

import os
import sys
import uuid
import json
import shutil
import sqlite3
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── make training/ importable ───────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(__file__))   # ai-service/
TRAINING_DIR = os.path.join(BASE_DIR, "training")
sys.path.insert(0, TRAINING_DIR)

from predict import analyze_image  # noqa: E402  (import after path setup)

# ── directories ─────────────────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH    = os.path.join(BASE_DIR, "scans.db")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}


# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id                 TEXT PRIMARY KEY,
            created_at         TEXT NOT NULL,
            food               TEXT,
            status             TEXT,
            predicted_class    TEXT,
            confidence_percent REAL,
            freshness_score    INTEGER,
            days_to_spoil      INTEGER,
            advice             TEXT,
            note               TEXT,
            image_path         TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Ready → {DB_PATH}")


def save_scan(scan_id: str, image_path: str, result: dict, created_at: str):
    conn = get_db()
    conn.execute("""
        INSERT INTO scans
            (id, created_at, food, status, predicted_class,
             confidence_percent, freshness_score, days_to_spoil,
             advice, note, image_path)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        scan_id, created_at,
        result.get("food"),
        result.get("status"),
        result.get("predicted_class"),
        result.get("confidence_percent"),
        result.get("freshness_score"),
        result.get("days_to_spoil"),
        result.get("advice"),
        result.get("note"),
        image_path,
    ))
    conn.commit()
    conn.close()


def row_to_dict(row) -> dict:
    return dict(row)


# ─────────────────────────────────────────────
# LIFESPAN — warm up model on startup
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("[Model] Warming up...")
    try:
        from PIL import Image as PILImage
        warmup_path = os.path.join(UPLOAD_DIR, "_warmup.jpg")
        PILImage.new("RGB", (224, 224), color=(120, 80, 40)).save(warmup_path)
        analyze_image(warmup_path)
        os.remove(warmup_path)
        print("[Model] Ready.")
    except Exception as e:
        print(f"[Model] Warmup skipped ({e}) — will load on first request.")
    yield
    print("[API] Shutdown.")


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
app = FastAPI(
    title="Food Freshness API",
    description=(
        "ML-powered food freshness analysis system for reducing household food waste. "
        "Upload fruit/vegetable images to get freshness status, estimated shelf life, "
        "and storage advice."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images as static files (useful for frontend)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ─────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────
class ScanResult(BaseModel):
    scan_id:             str
    created_at:          str
    food:                str
    status:              str
    predicted_class:     str
    confidence_percent:  float
    freshness_score:     int
    days_to_spoil:       int
    advice:              str
    note:                Optional[str]


class StatsResponse(BaseModel):
    total_scans:   int
    fresh_count:   int
    rotten_count:  int
    top_food:      Optional[str]
    avg_freshness: float
    avg_days_left: float


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def validate_image(file: UploadFile):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: jpg, jpeg, png, webp."
        )


async def save_upload(file: UploadFile) -> tuple[str, str]:
    """Save upload to disk. Returns (scan_id, filepath)."""
    scan_id  = str(uuid.uuid4())
    ext      = os.path.splitext(file.filename or "image.jpg")[1].lower() or ".jpg"
    filepath = os.path.join(UPLOAD_DIR, f"{scan_id}{ext}")
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return scan_id, filepath


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    """Quick health check — call this to confirm the API is running."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ── Single predict ──────────────────────────
@app.post("/predict", response_model=ScanResult, tags=["Prediction"])
async def predict(file: UploadFile = File(...)):
    """
    Analyse a single fruit or vegetable image.

    - **file**: JPG / PNG image of the item

    Returns freshness status, confidence score, estimated days left,
    and storage advice. Every result is saved to history automatically.
    """
    validate_image(file)
    scan_id, filepath = await save_upload(file)

    try:
        result = analyze_image(filepath)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    created_at = datetime.utcnow().isoformat()
    save_scan(scan_id, filepath, result, created_at)

    return ScanResult(
        scan_id=scan_id,
        created_at=created_at,
        food=result["food"],
        status=result["status"],
        predicted_class=result["predicted_class"],
        confidence_percent=result["confidence_percent"],
        freshness_score=result["freshness_score"],
        days_to_spoil=result["days_to_spoil"],
        advice=result["advice"],
        note=result["note"],
    )


# ── Batch predict ───────────────────────────
@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(files: list[UploadFile] = File(...)):
    """
    Analyse up to 10 images in a single request.
    Results are returned in the same order as the uploaded files.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Max 10 images per batch.")

    results = []
    for file in files:
        validate_image(file)
        scan_id, filepath = await save_upload(file)
        try:
            result     = analyze_image(filepath)
            created_at = datetime.utcnow().isoformat()
            save_scan(scan_id, filepath, result, created_at)
            results.append({
                "scan_id":    scan_id,
                "created_at": created_at,
                "filename":   file.filename,
                "error":      None,
                **result,
            })
        except Exception as e:
            results.append({
                "scan_id":  scan_id,
                "filename": file.filename,
                "error":    str(e),
            })

    return {"count": len(results), "results": results}


# ── History ─────────────────────────────────
@app.get("/history", tags=["History"])
def get_history(
    limit:  int           = Query(50,  ge=1, le=200),
    offset: int           = Query(0,   ge=0),
    food:   Optional[str] = Query(None, description="Filter by food name, e.g. banana"),
    status: Optional[str] = Query(None, description="Filter by status: Fresh or Rotten"),
):
    """
    Returns paginated scan history, newest first.
    Use `?food=banana` or `?status=Rotten` to filter.
    """
    conn   = get_db()
    query  = "SELECT * FROM scans WHERE 1=1"
    params: list = []

    if food:
        query += " AND LOWER(food) = LOWER(?)"
        params.append(food)
    if status:
        query += " AND LOWER(status) = LOWER(?)"
        params.append(status)

    total = conn.execute(
        f"SELECT COUNT(*) FROM scans WHERE 1=1"
        + (" AND LOWER(food) = LOWER(?)" if food else "")
        + (" AND LOWER(status) = LOWER(?)" if status else ""),
        [p for p in [food, status] if p]
    ).fetchone()[0]

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "total":  total,
        "limit":  limit,
        "offset": offset,
        "scans":  [row_to_dict(r) for r in rows],
    }


@app.get("/history/{scan_id}", tags=["History"])
def get_scan(scan_id: str):
    """Fetch a single past scan by its ID."""
    conn = get_db()
    row  = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found.")
    return row_to_dict(row)


@app.delete("/history/{scan_id}", tags=["History"])
def delete_scan(scan_id: str):
    """Delete a scan record and its uploaded image file."""
    conn = get_db()
    row  = conn.execute("SELECT image_path FROM scans WHERE id = ?", (scan_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found.")

    image_path = row["image_path"]
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()
    return {"deleted": scan_id}


# ── Stats ───────────────────────────────────
@app.get("/stats", response_model=StatsResponse, tags=["Analytics"])
def get_stats():
    """
    Aggregated statistics across all scans.
    Feed this into your React analytics dashboard.
    """
    conn = get_db()

    total        = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    fresh_count  = conn.execute("SELECT COUNT(*) FROM scans WHERE status='Fresh'").fetchone()[0]
    rotten_count = conn.execute("SELECT COUNT(*) FROM scans WHERE status='Rotten'").fetchone()[0]

    top_food_row = conn.execute("""
        SELECT food, COUNT(*) AS cnt
        FROM scans
        GROUP BY food
        ORDER BY cnt DESC
        LIMIT 1
    """).fetchone()

    avg_row = conn.execute("""
        SELECT AVG(freshness_score), AVG(days_to_spoil)
        FROM scans WHERE status = 'Fresh'
    """).fetchone()

    conn.close()

    return StatsResponse(
        total_scans   = total,
        fresh_count   = fresh_count,
        rotten_count  = rotten_count,
        top_food      = top_food_row["food"] if top_food_row else None,
        avg_freshness = round(avg_row[0] or 0.0, 1),
        avg_days_left = round(avg_row[1] or 0.0, 1),
    )
