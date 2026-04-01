"""
run.py  —  Start the Food Freshness API
========================================
Run from the project root:
    python run.py

Then open:
    http://localhost:8000/docs   ← interactive Swagger UI
    http://localhost:8000/health ← quick health check
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "ai-service.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,           # auto-restarts when you edit code
        reload_dirs=["ai-service"],
    )
