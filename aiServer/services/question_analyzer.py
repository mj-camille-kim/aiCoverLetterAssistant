import json
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from dotenv import load_dotenv
load_dotenv()

def generate_coverletter_guide(
    question: str,
    company_person: str,
    jd_analysis: str,
    model_name: str = "gpt-5-nano-2025-08-07",
    temperature: float = 0.2,
) -> str:
    """
    자기소개서 문항 분석 및 작성 가이드 생성 함수

    Args:
        question (str): 자소서 질문 문항 (예: "지원동기")
        company_person (str): 기업 인재상 / 핵심 가치
        jd_analysis (str): 직무 분석 내용
        model_name (str): 사용할 OpenAI 모델명
        temperature (float): 모델 temperature

    Returns:
        str: JSON 형식의 자소서 작성 가이드
    """

    model = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    system_prompt = f"""
    당신은 전문 자기소개서 컨설턴트입니다. 아래 정보를 바탕으로 하나의 완성된 JSON 객체를 생성하세요.

    **규칙**
    1. q_type은 반드시 q_type 후보군 중 하나여야 합니다.
    2. q_intention은 반드시 q_intention 후보군 중 하나여야 합니다.

    [질문 문항]: {question}
    [기업 인재상]: {company_person}
    [JD 분석 내용]: {jd_analysis}

    [JSON 구조 가이드]:
    {{
      "analysis": {{
        "q_type": "q_type 후보 중 택 1",
        "q_intention": ["q_intention 후보 중 택 1~3"]
      }},
      "core_competency": "문항종류/문항의도/{question}/{company_person}/{jd_analysis}를 참고하여 드러나야 할 핵심 역량과 경험(1-2문장)",
      "guideline": "문항종류/문항의도/{question}/{company_person}/{jd_analysis}를 참고하여 해당 문항에 포함되어야 할 내용과 기승전결에 대한 구체적인 가이드라인(3-4문장)"
    }}
    
    [선택 후보군]:
    - q_type 후보군: [직무역량, 경험/성과, 지원동기, 문제해결, 포부/비전, 성격/인성, 성장과정, 가치관, 산업이해, 사회이슈, 도전정신, 협업능력, 자기소개]
    - q_intention 후보군: [직무적합성, 성과증명, 문제인식, 협업능력, 성장목표, 회사적합성, 책임감, 고객지향, 도전정신, 학습능력, 산업이해, 성격특성, 조직적합성, 문제해결, 윤리/ESG, 소통능력, 리더십, 직무태도, 신뢰, 사회적책임, 창의성, 의사소통, 전문성, 사회공헌]
    """

    response = model.invoke(system_prompt)
    print (json.loads(response.content))
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"error": "JSON 파싱 실패", "raw_content": response.content}
    

def exp_recommendation (userEmail, core_competency):
    embedding = OpenAIEmbeddings(model="text-embedding-3-large")

    vectorstore = Chroma(
        persist_directory="../my_chroma_db",  # 벡터db 경로
        embedding_function=embedding,
        collection_name="user_experiences"
      )
      
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3,
                       "filter": {"userEmail": userEmail}}
    )
    # question_analyze가 딕셔너리라면 검색에 쓸 텍스트 키를 추출해야 함
    query_text = core_competency
    docs = retriever.invoke(query_text)
    metadata_list = [doc.metadata for doc in docs]

    return metadata_list
