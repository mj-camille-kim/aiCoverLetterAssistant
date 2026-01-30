from fastapi import FastAPI, UploadFile, File, Body
from services.exp_extractor import extract_text_from_pdf
from services.exp_extractor import process_experience
from fastapi.middleware.cors import CORSMiddleware
from typing import List

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
async def analyze_pdf(file: UploadFile = File(...)):
    content = await file.read()
    raw_text = extract_text_from_pdf(content)

    if not raw_text:
        return {"error": "PDF에서 텍스트를 추출할 수 없습니다."}
    
    return process_experience(raw_text, is_json=False)

@app.post("/analyze/json")
async def analyze_json(data: List[dict] = Body(...)):
    results = []
    for item in data:
        results.append(process_experience(item, is_json=True))
    return results # 결과 리스트로 반환