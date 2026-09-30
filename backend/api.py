"""
FastAPI entry point for the Code AI backend.

Endpoints:
  POST /api/review   — start a code review (async)
  GET  /api/review/{job_id}  — poll for status / result
  GET  /api/health   — health check
"""

import os
import uuid
import threading
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Literal

from review_service import run_review


# ──────────────────────────────────────────────
# APP SETUP
# ──────────────────────────────────────────────
app = FastAPI(title="Code AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# IN-MEMORY JOB STORE  (sufficient for prototype)
# ──────────────────────────────────────────────
jobs: dict[str, dict] = {}


# ──────────────────────────────────────────────
# SCHEMAS
# ──────────────────────────────────────────────
class ReviewRequest(BaseModel):
    repository_url: str
    audit_type: Literal["security", "performance", "best practices", "everything"] = "everything"
    model: Literal["gemini", "claude", "chatgpt"] = "gemini"


class ReviewStartResponse(BaseModel):
    job_id: str
    status: str
    message: str


# ──────────────────────────────────────────────
# BACKGROUND WORKER
# ──────────────────────────────────────────────
def _run_review_job(job_id: str, repository_url: str, audit_type: str):
    jobs[job_id]["status"] = "running"

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")

        result = run_review(
            repository_url=repository_url,
            api_key=api_key,
            audit_type=audit_type,
            inventory_path=f"inventory_{job_id}.json",
            review_path=f"review_{job_id}.json",
        )

        review_data = result["review_result"]

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        jobs[job_id]["result"] = review_data

    except Exception as exc:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(exc)
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Code AI Backend"}


@app.post("/api/review", response_model=ReviewStartResponse)
def start_review(body: ReviewRequest):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "repository_url": body.repository_url,
        "audit_type": body.audit_type,
        "model": body.model,
        "created_at": datetime.utcnow().isoformat(),
        "result": None,
        "error": None,
    }

    # Run review in background thread so the HTTP response returns immediately
    thread = threading.Thread(
        target=_run_review_job,
        args=(job_id, body.repository_url, body.audit_type),
        daemon=True,
    )
    thread.start()

    return ReviewStartResponse(
        job_id=job_id,
        status="queued",
        message="Review started. Poll /api/review/{job_id} for status.",
    )


@app.get("/api/review/{job_id}")
def get_review_status(job_id: str):
    job = jobs.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return job
