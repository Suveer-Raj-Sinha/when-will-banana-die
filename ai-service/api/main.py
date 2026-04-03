"""
main.py  —  Food Freshness REST API
=====================================
Run from the project root:
    uvicorn ai-service.api.main:app --reload --port 8000

Swagger UI:
    http://localhost:8000/docs

Endpoints:
    POST   /predict               – single image analysis
    POST   /predict/batch         – up to 10 images at once
    GET    /history               – paginated scan history
    GET    /history/{id}          – single scan
    DELETE /history/{id}          – delete a scan
    GET    /stats                 – summary stats
    GET    /recipes               – recipes for all foods
    GET    /recipes/{food}        – recipes for a specific food
    GET    /recipes/expiring      – recipes for items expiring soon
    GET    /storage-tips/{food}   – detailed storage tips for a food
    GET    /health                – health check
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

# ── path setup ───────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(__file__))
TRAINING_DIR = os.path.join(BASE_DIR, "training")
sys.path.insert(0, TRAINING_DIR)

from predict import analyze_image
from recipes import get_storage_tips, get_recipes, get_recipes_for_expiring, RECIPES

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH    = os.path.join(BASE_DIR, "scans.db")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}


# ─────────────────────────────────────────────
# DATABASE
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
            food_key           TEXT,
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
            (id, created_at, food, food_key, status, predicted_class,
             confidence_percent, freshness_score, days_to_spoil,
             advice, note, image_path)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        scan_id, created_at,
        result.get("food"),
        result.get("food_key"),
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
# LIFESPAN
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
        print(f"[Model] Warmup skipped ({e})")
    yield
    print("[API] Shutdown.")


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
app = FastAPI(
    title="Food Freshness API",
    description="ML-powered food freshness analysis system for reducing household food waste.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ─────────────────────────────────────────────
# RESPONSE MODELS
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
    storage_tips:        dict
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
    scan_id  = str(uuid.uuid4())
    ext      = os.path.splitext(file.filename or "image.jpg")[1].lower() or ".jpg"
    filepath = os.path.join(UPLOAD_DIR, f"{scan_id}{ext}")
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return scan_id, filepath


# ─────────────────────────────────────────────
# ROUTES — SYSTEM
# ─────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
# ROUTES — PREDICTION
# ─────────────────────────────────────────────
@app.post("/predict", response_model=ScanResult, tags=["Prediction"])
async def predict(file: UploadFile = File(...)):
    """Analyse a single fruit or vegetable image."""
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
        storage_tips=result["storage_tips"],
        note=result["note"],
    )


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(files: list[UploadFile] = File(...)):
    """Analyse up to 10 images in a single request."""
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
            results.append({"scan_id": scan_id, "created_at": created_at,
                            "filename": file.filename, "error": None, **result})
        except Exception as e:
            results.append({"scan_id": scan_id, "filename": file.filename, "error": str(e)})

    return {"count": len(results), "results": results}


# ─────────────────────────────────────────────
# ROUTES — HISTORY
# ─────────────────────────────────────────────
@app.get("/history", tags=["History"])
def get_history(
    limit:  int           = Query(50, ge=1, le=200),
    offset: int           = Query(0,  ge=0),
    food:   Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
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
        "SELECT COUNT(*) FROM scans WHERE 1=1"
        + (" AND LOWER(food) = LOWER(?)" if food else "")
        + (" AND LOWER(status) = LOWER(?)" if status else ""),
        [p for p in [food, status] if p]
    ).fetchone()[0]

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {"total": total, "limit": limit, "offset": offset,
            "scans": [row_to_dict(r) for r in rows]}


@app.get("/history/{scan_id}", tags=["History"])
def get_scan(scan_id: str):
    conn = get_db()
    row  = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found.")
    return row_to_dict(row)


@app.delete("/history/{scan_id}", tags=["History"])
def delete_scan(scan_id: str):
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


# ─────────────────────────────────────────────
# ROUTES — STATS
# ─────────────────────────────────────────────
@app.get("/stats", response_model=StatsResponse, tags=["Analytics"])
def get_stats():
    conn         = get_db()
    total        = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    fresh_count  = conn.execute("SELECT COUNT(*) FROM scans WHERE status='Fresh'").fetchone()[0]
    rotten_count = conn.execute("SELECT COUNT(*) FROM scans WHERE status='Rotten'").fetchone()[0]
    top_food_row = conn.execute("""
        SELECT food, COUNT(*) AS cnt FROM scans
        GROUP BY food ORDER BY cnt DESC LIMIT 1
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


# ─────────────────────────────────────────────
# ROUTES — RECIPES
# ─────────────────────────────────────────────
@app.get("/recipes", tags=["Recipes"])
def all_recipes():
    """Returns the full recipe database for all supported foods."""
    return {"foods": list(RECIPES.keys()), "recipes": RECIPES}


@app.get("/recipes/expiring", tags=["Recipes"])
def recipes_for_expiring():
    """
    Checks your scan history for fresh items expiring within 3 days
    and returns recipe suggestions sorted by urgency (fewest days first).
    """
    conn  = get_db()
    rows  = conn.execute(
        "SELECT * FROM scans WHERE status='Fresh' AND days_to_spoil <= 3 "
        "ORDER BY days_to_spoil ASC LIMIT 20"
    ).fetchall()
    conn.close()

    scans       = [row_to_dict(r) for r in rows]
    suggestions = get_recipes_for_expiring(scans)

    return {
        "expiring_count": len(suggestions),
        "suggestions":    suggestions,
    }


@app.get("/recipes/{food}", tags=["Recipes"])
def recipes_for_food(food: str):
    """
    Returns recipes for a specific food.
    Example: /recipes/banana  /recipes/tomato
    """
    food_key = food.lower()
    result   = get_recipes([food_key])
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No recipes found for '{food}'. "
                   f"Supported: {', '.join(RECIPES.keys())}"
        )
    return {"food": food_key, "recipes": result[food_key]}


# ─────────────────────────────────────────────
# ROUTES — STORAGE TIPS
# ─────────────────────────────────────────────
@app.get("/storage-tips/{food}", tags=["Storage Tips"])
def storage_tips(food: str):
    """
    Returns detailed storage tips for a specific food.
    Example: /storage-tips/banana  /storage-tips/potato
    """
    tips = get_storage_tips(food.lower())
    if not tips:
        raise HTTPException(status_code=404, detail=f"No tips found for '{food}'.")
    return {"food": food.lower(), "tips": tips}
