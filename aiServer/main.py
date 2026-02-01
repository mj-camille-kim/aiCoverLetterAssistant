from fastapi import FastAPI, UploadFile, File, Form, Body
from services.exp_extractor import extract_text_from_pdf
from services.exp_extractor import process_experience
from services.exp_extractor import save_experiences_to_vector_db
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    userEmail: str
    data: List[dict]

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 경험 저장 및 분석 API
@app.post("/analyze/pdf")
async def analyze_pdf(userEmail: str = Form(...), file: UploadFile = File(...)):
    results = []
    content = await file.read()
    raw_text = extract_text_from_pdf(content)

    if not raw_text:
        return {"error": "PDF에서 텍스트를 추출할 수 없습니다."}
    
    results.append(process_experience(raw_text, is_json=False))
    save_experiences_to_vector_db(userEmail, results[0])  # 벡터 db 적재
    return results[0]

@app.post("/analyze/json")
async def analyze_json(request: AnalysisRequest):
    results = []
    for item in request.data:
        results.append(process_experience(item, is_json=True))
    save_experiences_to_vector_db(request.userEmail, results[0])   # 벡터 db 적재
    return results[0]