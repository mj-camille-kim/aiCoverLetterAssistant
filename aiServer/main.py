# -*- coding: utf-8 -*-
import os
import uuid
import threading

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
from pydantic import BaseModel

from services.exp_extractor import extract_text_from_pdf
from services.exp_extractor import process_experience
from services.exp_extractor import save_experiences_to_vector_db

# final_1 채용공고 분석 API 통합
from analysis_job import run_full_analysis_pipeline
import analysis_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 기존: 경험 분석 요청
class AnalysisRequest(BaseModel):
    userEmail: str
    data: List[dict]

# final_1: 채용공고 분석 요청
class AnalyzeJobRequest(BaseModel):
    target_url: str
    selected_job: str
    experience_level: str

# job_id → { "status": "pending" | "completed" | "failed", "html": str | None, "error": str | None }
_job_store = {}
_job_lock = threading.Lock()


def _run_analysis(job_id: str, target_url: str, selected_job: str, experience_level: str):
    try:
        final_data, company_dir = run_full_analysis_pipeline(
            target_url=target_url.strip(),
            selected_job=selected_job.strip(),
            experience_level=experience_level.strip(),
            save_base_dir=BASE_DIR,
        )
        if not final_data or not company_dir:
            with _job_lock:
                _job_store[job_id] = {"status": "failed", "html": None, "error": "분석 파이프라인 실패"}
            return
        company_name = final_data.get("company_name", "")
        abs_dir = os.path.abspath(company_dir)
        html = analysis_report.build_html_from_dir(abs_dir, company_name)
        with _job_lock:
            _job_store[job_id] = {"status": "completed", "html": html, "error": None}
    except Exception as e:
        with _job_lock:
            _job_store[job_id] = {"status": "failed", "html": None, "error": str(e)}


app = FastAPI(title="AI Cover Letter Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 기존: 경험 저장 및 분석 API ==========
@app.post("/analyze/pdf")
async def analyze_pdf(userEmail: str = Form(...), file: UploadFile = File(...)):
    results = []
    content = await file.read()
    raw_text = extract_text_from_pdf(content)

    if not raw_text:
        return {"error": "PDF에서 텍스트를 추출할 수 없습니다."}

    results.append(process_experience(raw_text, is_json=False))
    save_experiences_to_vector_db(userEmail, results[0])
    return results[0]


@app.post("/analyze/json")
async def analyze_json(request: AnalysisRequest):
    results = []
    for item in request.data:
        results.append(process_experience(item, is_json=True))
    save_experiences_to_vector_db(request.userEmail, results[0])
    return results[0]


# ========== final_1: 채용공고 분석 API ==========
@app.post("/analyze")
def analyze_start(req: AnalyzeJobRequest):
    """
    채용공고 URL + 직무 + 경력 입력 → 즉시 202 Accepted + job_id (JSON).
    실제 분석은 백그라운드에서 수행되며, 결과는 GET /analyze/result/{job_id} 로 조회.
    """
    job_id = uuid.uuid4().hex[:12]
    with _job_lock:
        _job_store[job_id] = {"status": "pending", "html": None, "error": None}
    thread = threading.Thread(
        target=_run_analysis,
        args=(job_id, req.target_url, req.selected_job, req.experience_level),
    )
    thread.daemon = True
    thread.start()
    return JSONResponse(
        status_code=202,
        content={"job_id": job_id},
    )


@app.get("/analyze/result/{job_id}")
def analyze_result(job_id: str):
    """
    분석 결과 조회. 완료 시 HTML 본문(text/html) 반환.
    진행 중이면 202, 실패 시 500, 없으면 404.
    """
    with _job_lock:
        job = _job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id를 찾을 수 없습니다.")
    status = job.get("status", "pending")
    if status == "completed":
        html = job.get("html")
        if html:
            return HTMLResponse(content=html)
        raise HTTPException(status_code=500, detail="결과 HTML이 없습니다.")
    if status == "failed":
        raise HTTPException(status_code=500, detail=job.get("error") or "분석 실패")
    return JSONResponse(
        status_code=202,
        content={"status": "processing", "job_id": job_id},
    )


@app.get("/")
def root():
    return {
        "message": "AI Cover Letter Assistant + 채용공고 분석 API",
        "analyze_post": "POST /analyze (body: target_url, selected_job, experience_level) → 202 { job_id }",
        "result_get": "GET /analyze/result/{job_id} → 200 HTML (완료) | 202 (진행 중)",
        "analyze_pdf": "POST /analyze/pdf (Form: userEmail, file) → 경험 추출",
        "analyze_json": "POST /analyze/json (body: userEmail, data) → 경험 분석",
    }
