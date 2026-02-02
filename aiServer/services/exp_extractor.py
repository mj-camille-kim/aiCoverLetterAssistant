import pdfplumber
import io
import openai
import json
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import os
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# PDF 파일에서 텍스트 추출 함수
def extract_text_from_pdf(file_content: bytes) -> str:

    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            pages_text = [
                page.extract_text() or "" 
                for page in pdf.pages
            ]
        
            full_text = "\n".join(pages_text).strip()
        
            import re
            full_text = re.sub(r'\n+', '\n', full_text)
            
            return full_text
            
    except Exception as e:
        print(f"PDF 추출 중 오류 발생: {e}")
        return ""


def process_experience(data, is_json=False):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    if is_json:
        prompt = f"""
        다음은 사용자가 STARI 기법으로 직접 작성한 경험 데이터입니다.
        이 내용을 바탕으로 1) 요약 제목을 짓고 2) 역량 키워드 소프트스킬 3개, 하드스킬 3개 추출해주세요.
        
        데이터: {json.dumps(data, ensure_ascii=False)}
        """
    else:
        prompt = f"""
        다음은 사용자의 경험 원문입니다. 사용자의 경험이 여러 개라면 각각 분리해서 처리해주세요.
        
        **경험으로 간주하는 기준** : 아이디어로 머무르지 않고, 실제로 행동하여 결과를 만들어낸 사례만 경험으로 간주합니다.

        각 경험을 1) STARI 기법으로 분류하고, 2) 요약 제목을 짓고, 3) 핵심 키워드 6개(소프트스킬 3개, 하드스킬 3개)를 추출해주세요.
        STARI: situation, task, action, result, insight

        원문: {data}
        """

    prompt += """
    **출력 규칙**
    반드시 결과물을 JSON 형식으로 출력하세요. 
    최상위 experiences를 배열로 감싸서 만들지 마세요. 해당 객체가 최상위 depth가 되도록 해야합니다.
    classifySTARI의 각 항목이 원문 분량과 비교해 짧지 않도록 상세히 작성해주세요. 말투는 '-습니다.'체로 통일해주세요.

    {
      "title": "...",
      "classifySTARI": {"situation": "...", "task": "...", "action": "...", "result": "...", "insight": "..."}, 
      "keywords": ["...", "...", "...", "...", "...", "..."]
    }
    """

    response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "experience_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "experiences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "classifySTARI": {
                                "type": "object",
                                "properties": {
                                    "situation": {"type": "string"},
                                    "task": {"type": "string"},
                                    "action": {"type": "string"},
                                    "result": {"type": "string"},
                                    "insight": {"type": "string"}
                                },
                                "required": ["situation", "task", "action", "result", "insight"],
                                "additionalProperties": False
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["title", "classifySTARI", "keywords"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["experiences"],
            "additionalProperties": False
        }
    }
}

    response = client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format
    )
    
    # JSON 문자열을 파이썬 객체로 변환
    result = json.loads(response.choices[0].message.content)
        
    return result


def save_experiences_to_vector_db(userEmail, analysis_result, db_path="../my_chroma_db"):
    experiences_list = analysis_result.get('experiences', [])
    if not experiences_list:
        print("저장할 경험 데이터가 없습니다.")
        return None

    documents = []
    for exp in experiences_list:
        stari = exp.get('classifySTARI', {})
        keywords = exp.get('keywords', [])
        keywords_text = ", ".join(keywords)
        title = exp.get('title', '제목 없음')

        page_content = f"""키워드: {keywords_text}
상황(Situation): {stari.get('situation', '')}
과제(Task): {stari.get('task', '')}
행동(Action): {stari.get('action', '')}
결과(Result): {stari.get('result', '')}
통찰(Insight): {stari.get('insight', '')}"""

        metadata = {
            "userEmail" : userEmail,
            "title": title,
            "keywords": keywords_text,
            "rawText": "".join([stari.get(k, '') for k in ['situation', 'task', 'action', 'result', 'insight']])
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    # 한 번에 모든 문서를 DB에 저장
    Chroma.from_documents(
        documents=documents,
        embedding=OpenAIEmbeddings(model="text-embedding-3-large"), # 오타 수정
        persist_directory=db_path,
        collection_name="user_experiences"
    )
    
    print(f"{len(documents)}개의 경험이 '{db_path}'에 성공적으로 저장되었습니다.")
    print(page_content)
    return 0