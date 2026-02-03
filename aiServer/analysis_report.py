# -*- coding: utf-8 -*-
"""프론트에서 전달받은 공고 기준 폴더의 4개 JSON → Sky 형식 HTML 보고서 생성 (analysis.py와 통합 사용).
CSV(company_names_500_filtered.csv)에 기업명이 있으면 MongoDB에서 사업보고서 데이터 조회, 없으면 dart 폴더 JSON 사용."""
import csv
import json
import os
import re
import sys
import html as html_module
from glob import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # aiServer 상위 = 프로젝트 루트

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))
    load_dotenv()
except ImportError:
    pass

DART_DIR = os.path.join(SCRIPT_DIR, "dart")
DART_CSV_PATH = os.path.join(DART_DIR, "company_names_500_filtered.csv")

# MongoDB: MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION 환경변수 사용 (없으면 dart 폴더만 사용)
MONGO_URI = os.environ.get("MONGO_URI", "").strip()
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "my_data").strip() or "my_data"
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "json_data").strip() or "json_data"


# ---------------------------------------------------------------------------
# dart 폴더 DB 조회 함수
# ---------------------------------------------------------------------------
def _load_dart_company_set():
    """dart/company_names_500_filtered.csv에서 기업명 집합 로드 (정규화된 이름으로 저장)."""
    if not os.path.exists(DART_CSV_PATH):
        return set()
    companies = set()
    with open(DART_CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("company_name", "").strip()
            if name:
                companies.add(name)
                companies.add(_normalize_company_name(name))
    return companies


def _find_dart_json(company_name):
    """dart 폴더에서 {company_name}_사업보고서*.json 파일 경로 반환. 없으면 None."""
    # 패턴: CJ_사업보고서.json, 고려아연_사업보고서_완성.json 등
    pattern = os.path.join(DART_DIR, f"{company_name}_사업보고서*.json")
    matches = glob(pattern)
    if matches:
        return matches[0]
    return None


def _load_dart_data(company_name):
    """dart JSON 파일 로드. 없으면 None."""
    path = _find_dart_json(company_name)
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ---------------------------------------------------------------------------
# MongoDB 조회 (CSV에 기업명이 있을 때 우선 사용)
# ---------------------------------------------------------------------------
def _normalize_company_name(name):
    """기업명 정규화: (주) 제거, 공백 제거."""
    if not name or not isinstance(name, str):
        return ""
    s = name.replace("(주)", "").replace("주)", "").replace(" ", "").strip()
    return s


def _load_dart_data_from_mongo(company_name):
    """MongoDB에서 기업명으로 사업보고서 데이터 조회. 없거나 연결 실패 시 None.
    문서 구조: company_info, financial_statements, business_overview, products_services
    (my_data.json_data: company_info.company_name / metadata.company_name 등 지원)
    """
    if not MONGO_URI:
        return None
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client[MONGO_DB_NAME]
        coll = db[MONGO_COLLECTION]
        norm = _normalize_company_name(company_name)
        # 정확 매칭 + company_info.company_name / metadata.company_name 정규식 매칭
        search_term = re.escape(norm) if norm else re.escape(company_name)
        q = {"$or": [
            {"company_name": company_name},
            {"companyName": company_name},
            {"company_name": norm},
            {"companyName": norm},
            {"company_info.company_name": {"$regex": search_term}},
            {"metadata.company_name": {"$regex": search_term}},
        ]}
        doc = coll.find_one(q)
        client.close()
        if not doc:
            return None
        # _id는 JSON 직렬화를 위해 제거 (또는 str 변환)
        if "_id" in doc:
            doc = dict(doc)
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        print(f"[MongoDB] 조회 실패: {e}")
        return None


def _parse_dart_financial(dart_data):
    """dart JSON의 financial_statements에서 재무지표 딕셔너리 추출.
    반환: {"유동자산": int, "비유동자산": int, "자산총계": int, "부채총계": int,
           "자본총계": int, "매출액": int, "영업이익": int, "당기순이익": int}
    보험사 등 특수 업종도 지원 (자산총계, 부채총계, 자본총계는 필수 추출)
    """
    result = {
        "유동자산": None,
        "비유동자산": None,
        "자산총계": None,
        "부채총계": None,
        "자본총계": None,
        "매출액": None,
        "영업이익": None,
        "당기순이익": None,
    }
    if not dart_data:
        return result
    fs = dart_data.get("financial_statements") or {}
    tables = fs.get("tables") or []
    
    # 모든 테이블 순회하며 재무지표 추출
    for tbl in tables:
        table_rows = tbl.get("table") or []
        unit_str = tbl.get("unit", "")
        # 단위 파악: 백만원, 천원, 원 등
        unit_mult = 1
        if "천" in unit_str and "백만" not in unit_str:
            unit_mult = 0.001  # 천원 → 백만원 변환
        elif "원" in unit_str and "백만" not in unit_str and "천" not in unit_str:
            unit_mult = 0.000001  # 원 → 백만원 변환
        
        # 각 행에서 항목명 매칭
        for row in table_rows:
            if not row or len(row) < 2:
                continue
            label_raw = str(row[0]).strip()
            label = label_raw.replace("[", "").replace("]", "").replace(" ", "").replace(".", "")
            val_str = str(row[1]).replace(",", "").replace(" ", "")
            
            # 숫자 추출
            match = re.search(r"[-+]?\d+(?:\.\d+)?", val_str)
            if not match:
                continue
            val = float(match.group())
            val_converted = int(val * unit_mult) if unit_mult != 1 else int(val)
            
            # 0이거나 너무 작은 값은 무시
            if val_converted == 0:
                continue
            
            # 항목 매핑 (유연한 매칭 - 보험사 등 특수 업종 포함)
            if result["유동자산"] is None and any(k in label for k in ["유동자산", "Ⅰ유동자산"]):
                result["유동자산"] = val_converted
            elif result["비유동자산"] is None and any(k in label for k in ["비유동자산", "Ⅱ비유동자산"]):
                result["비유동자산"] = val_converted
            elif result["자산총계"] is None and any(k in label for k in ["자산총계", "자산총액", "총자산"]):
                result["자산총계"] = val_converted
            # 부채: 일반 제조업 + 보험사(보험계약부채 등)
            elif result["부채총계"] is None and any(k in label for k in ["부채총계", "부채총액", "총부채", "부채및자본총계"]):
                # "부채및자본총계"는 제외 (자산총계와 같음)
                if "자본" not in label:
                    result["부채총계"] = val_converted
            # 자본: 일반 제조업 + 보험사(납입자본 등)
            elif result["자본총계"] is None and any(k in label for k in ["자본총계", "자본총액", "총자본", "납입자본"]):
                result["자본총계"] = val_converted
            # 매출액: 일반 제조업 + 보험사(보험료수익 등)
            elif result["매출액"] is None and any(k in label for k in ["매출액", "영업수익", "수익합계", "보험료수익"]):
                result["매출액"] = val_converted
            # 영업이익
            elif result["영업이익"] is None and any(k in label for k in ["영업이익", "영업손익", "보험영업이익"]):
                result["영업이익"] = val_converted
            # 당기순이익
            elif result["당기순이익"] is None and any(k in label for k in ["당기순이익", "당기순손익", "순이익", "순손익"]):
                result["당기순이익"] = val_converted
    
    # 보험사 등: 자산총계는 있는데 부채/자본 총계가 없으면 개별 항목 합산
    if result["자산총계"] and (result["부채총계"] is None or result["자본총계"] is None):
        for tbl in tables:
            table_rows = tbl.get("table") or []
            unit_str = tbl.get("unit", "")
            unit_mult = 1
            if "천" in unit_str and "백만" not in unit_str:
                unit_mult = 0.001
            elif "원" in unit_str and "백만" not in unit_str and "천" not in unit_str:
                unit_mult = 0.000001
            
            liabilities_sum = 0
            equity_sum = 0
            for row in table_rows:
                if not row or len(row) < 2:
                    continue
                label = str(row[0]).strip().replace("[", "").replace("]", "").replace(" ", "")
                val_str = str(row[1]).replace(",", "").replace(" ", "")
                match = re.search(r"[-+]?\d+(?:\.\d+)?", val_str)
                if not match:
                    continue
                val = float(match.group())
                val_converted = int(val * unit_mult) if unit_mult != 1 else int(val)
                if val_converted == 0:
                    continue
                
                # 부채 항목 (보험계약부채, 기타부채, 차입금 등)
                if any(k in label for k in ["보험계약부채", "기타부채", "차입금", "사채", "미지급금", "예수부채"]):
                    liabilities_sum += val_converted
                # 자본 항목 (납입자본, 이익잉여금, 자본잉여금 등)
                elif any(k in label for k in ["납입자본", "이익잉여금", "자본잉여금", "기타포괄손익누계액"]):
                    equity_sum += val_converted
            
            if result["부채총계"] is None and liabilities_sum > 0:
                result["부채총계"] = liabilities_sum
            if result["자본총계"] is None and equity_sum > 0:
                result["자본총계"] = equity_sum
    
    # 최종 검증: 자산 = 부채 + 자본 (오차 10% 이내면 계산으로 보정)
    if result["자산총계"] and result["자본총계"] and result["부채총계"] is None:
        result["부채총계"] = result["자산총계"] - result["자본총계"]
    elif result["자산총계"] and result["부채총계"] and result["자본총계"] is None:
        result["자본총계"] = result["자산총계"] - result["부채총계"]
    
    return result


def _get_dart_company_info(dart_data):
    """dart JSON에서 company_info 반환."""
    if not dart_data:
        return {}
    return dart_data.get("company_info") or {}


def _get_dart_business_overview(dart_data):
    """dart JSON에서 사업 개요 텍스트 반환."""
    if not dart_data:
        return ""
    bo = dart_data.get("business_overview") or {}
    return bo.get("content") or ""


def _get_dart_products_services(dart_data):
    """dart JSON에서 주요 제품/서비스 텍스트 반환."""
    if not dart_data:
        return ""
    ps = dart_data.get("products_services") or {}
    return ps.get("content") or ""


def check_dart_available(company_name):
    """dart DB에 해당 기업이 존재하는지 확인. (CSV + JSON 파일 존재 여부)"""
    companies = _load_dart_company_set()
    if company_name not in companies:
        return False
    return _find_dart_json(company_name) is not None


def _json_filenames(company_name):
    """기업명 기준 4개 JSON 파일명."""
    return [
        f"{company_name}.json",
        f"{company_name}_JD분석.json",
        f"{company_name}_NEWS.json",
        f"{company_name}_homepage.json",
    ]


def _merged_report_path(company_dir, company_name):
    """통합 보고서 JSON 경로."""
    name = company_name or "대주산업"
    base = company_dir if company_dir else os.path.join(SCRIPT_DIR, name)
    return os.path.join(base, f"{name}_통합.json")


def load_merged_report(company_dir=None, company_name=None):
    """
    통합 JSON 1개({company_name}_통합.json)를 로드하여 build_html에 넘길 data 딕셔너리 반환.
    파일이 없으면 None.
    """
    path = _merged_report_path(company_dir, company_name)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_json_files(company_dir=None, company_name=None):
    """
    4개 JSON 파일을 로드하여 딕셔너리로 반환.
    company_dir: 기업 폴더 경로 (공고 분석 시 생성된 폴더)
    company_name: 기업명 (폴더명과 동일). 둘 다 없으면 SCRIPT_DIR 아래 '대주산업' 폴더 기준.
    """
    name = (company_name or "대주산업")
    if company_dir:
        base = company_dir
    else:
        base = os.path.join(SCRIPT_DIR, name)
    filenames = _json_filenames(name)
    data = {}
    for filename in filenames:
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"파일 없음: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data[filename] = json.load(f)
    return data


def escape(s):
    """HTML 이스케이프."""
    if s is None:
        return ""
    return html_module.escape(str(s).strip())


def parse_jd_sections(jd_analysis_report):
    """jd_analysis_report 텍스트에서 HARD SKILL / SOFT SKILL 블록 추출."""
    text = jd_analysis_report or ""
    hard_lines = []
    soft_lines = []
    # #### 1. HARD SKILL ... #### 2. SOFT SKILL ... #### 3. 인재상
    parts = re.split(r"\n####\s+\d+\.\s+", text, flags=re.IGNORECASE)
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        if part.upper().startswith("HARD SKILL"):
            body = re.sub(r"^HARD\s+SKILL\s*", "", part, flags=re.I).strip()
            for line in body.split("\n"):
                line = line.strip()
                if line.startswith("- **"):
                    m = re.match(r"^-\s+\*\*(.+?)\*\*:\s*(.*)$", line)
                    if m:
                        hard_lines.append("• {}: {}".format(m.group(1).strip(), m.group(2).strip()))
                    else:
                        hard_lines.append("• " + re.sub(r"^-\s+\*\*|\*\*:\s*", "", line))
                elif line.startswith("- ") and line not in ("- ", ""):
                    hard_lines.append("• " + line[2:].strip())
        elif part.upper().startswith("SOFT SKILL"):
            body = re.sub(r"^SOFT\s+SKILL\s*", "", part, flags=re.I).strip()
            for line in body.split("\n"):
                line = line.strip()
                if line.startswith("- **"):
                    m = re.match(r"^-\s+\*\*(.+?)\*\*:\s*(.*)$", line)
                    if m:
                        soft_lines.append("• {}: {}".format(m.group(1).strip(), m.group(2).strip()))
                    else:
                        soft_lines.append("• " + re.sub(r"^-\s+\*\*|\*\*:\s*", "", line))
                elif line.startswith("- ") and line not in ("- ", ""):
                    soft_lines.append("• " + line[2:].strip())
    hard_text = "\n".join(hard_lines) if hard_lines else "• (JD 분석 내용 참조)"
    soft_text = "\n".join(soft_lines) if soft_lines else "• (JD 분석 내용 참조)"
    return hard_text, soft_text, jd_analysis_report or ""


def _jd_detail_without_123_and_talent(jd_report):
    """
    합격 전략서에서 1번(HARD SKILL), 2번(SOFT SKILL) 제거하고,
    3번(인재상) 내용은 JD 직무분석 탭 하단(인재상/조직 문화)용으로 분리.
    반환: (jd_detail_4_5_이하, section3_인재상_텍스트)
    """
    if not jd_report or not jd_report.strip():
        return "", ""
    text = jd_report.strip()
    parts = re.split(r"\n####\s+", text)
    section3_text = ""
    detail_parts = []
    section_num = 1
    for i, part in enumerate(parts):
        part_stripped = part.strip()
        if not part_stripped:
            continue
        if part_stripped.upper().startswith("1. HARD SKILL"):
            continue
        if part_stripped.upper().startswith("2. SOFT SKILL"):
            continue
        if re.match(r"^3\.\s*인재상", part_stripped, re.I):
            body = re.sub(r"^3\.\s*인재상\s*", "", part_stripped, flags=re.I).strip()
            if body:
                section3_text = body
            continue
        if i > 0:
            # 4번→1번, 5번→2번 등으로 재매김
            renumbered = re.sub(r"^\d+\.\s*", "{}. ".format(section_num), part_stripped, count=1)
            detail_parts.append("#### " + renumbered)
            section_num += 1
        else:
            detail_parts.append(part_stripped)
    jd_detail = "\n\n".join(detail_parts) if detail_parts else ""
    return jd_detail, section3_text


def _format_news_date(item):
    """뉴스 항목에서 날짜 추출 후 읽기 쉬운 형식으로 반환. 없으면 '날짜 없음'."""
    raw = item.get("pubDate") or item.get("date") or item.get("published") or ""
    if not raw or not str(raw).strip():
        return "날짜 없음"
    raw = str(raw).strip()
    try:
        from datetime import datetime
        # YYYYMMDD (8자리)
        if raw.isdigit() and len(raw) >= 8:
            return "{}년 {}월 {}일".format(raw[:4], raw[4:6].lstrip("0") or "1", raw[6:8].lstrip("0") or "1")
        # YYYY-MM-DD
        if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
            return "{}년 {}월 {}일".format(raw[:4], raw[5:7].lstrip("0") or "1", raw[8:10].lstrip("0") or "1")
        # RFC 2822: "Wed, 29 Jan 2026 12:00:00 +0900"
        if "," in raw and len(raw) >= 20:
            dt = datetime.strptime(raw[:25].rstrip(), "%a, %d %b %Y %H:%M:%S")
            return dt.strftime("%Y년 %m월 %d일")
        # ISO: 2026-01-29T12:00:00
        if "T" in raw and len(raw) >= 10:
            dt = datetime.strptime(raw[:19], "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y년 %m월 %d일")
        # 2026-01-29 18:15:25 (analyzed_at 등)
        if len(raw) >= 19 and raw[4] == "-" and raw[10] == " ":
            dt = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y년 %m월 %d일")
    except Exception:
        pass
    # "2일 전" 등 상대 표기 또는 그대로 표시
    return raw if len(raw) <= 30 else raw[:27] + "..."


def news_analysis_to_summary(item):
    """뉴스 analysis 객체를 짧은 AI 요약 문장으로 변환."""
    analysis = item.get("analysis") or {}
    title = (item.get("title") or "").lower()
    parts = []
    if "current_price" in analysis or "current_stock_price" in analysis:
        price = analysis.get("current_price") or analysis.get("current_stock_price")
        pct = analysis.get("price_change_percentage") or analysis.get("percentage_change")
        if price is not None:
            parts.append("주가 {}원".format(price))
        if pct is not None:
            parts.append("전일 대비 {}% {}".format(abs(pct), "상승" if pct >= 0 else "하락"))
    if "status_update" in analysis:
        su = analysis["status_update"]
        cur = su.get("current_status") or ""
        prev = su.get("previous_status") or ""
        if cur or prev:
            parts.append("{} 해제 후 {} 재지정 예고".format(prev or "-", cur or "-"))
    if "market_performance" in analysis:
        mp = analysis["market_performance"]
        parts.append(mp.get("overall_trend", ""))
    if "key_drivers" in analysis:
        kd = analysis["key_drivers"]
        pos = kd.get("positive") or []
        neg = kd.get("negative") or []
        if pos:
            parts.append("호재: " + ", ".join(pos[:2]))
        if neg:
            parts.append("부담: " + ", ".join(neg[:2]))
    if not parts:
        parts.append(analysis.get("investment_advice") or title[:80])
    return " ".join(parts).strip() or "관련 기사 요약."


def _normalize_summary(homepage):
    """homepage.json 구조 통일: summary / summary.summary / summary.company(아모텍) / 한글 플랫 모두 지원."""
    summary = homepage.get("summary") or {}
    inner = summary.get("summary") if isinstance(summary.get("summary"), dict) else {}
    if not inner and isinstance(summary.get("company"), dict):
        inner = summary.get("company") or {}
    # summary 자체에 영문 키가 있는 경우(티케이엘리베이터코리아)도 수집
    def _v(*keys, default="—"):
        for k in keys:
            if k in summary and summary[k]:
                return summary[k]
            if isinstance(inner, dict) and k in inner and inner[k]:
                return inner[k]
        return default
    addr = summary.get("address")
    if isinstance(addr, dict):
        address_val = addr.get("full_address") or summary.get("주소") or "—"
    else:
        address_val = (addr.strip() if isinstance(addr, str) and addr else "") or summary.get("주소") or "—"
    def _strip_url(u):
        return (u or "").strip() or "#"
    # 아모텍: company.businessDescription, company.companyVision.mainBusinessFocus, company.coreProducts
    company_vision_inner = (inner.get("companyVision") or {}) if isinstance(inner, dict) else {}
    def _main_business():
        if isinstance(summary.get("기업비전"), dict) and summary["기업비전"].get("주요 사업내용"):
            return summary["기업비전"].get("주요 사업내용")
        mb = company_vision_inner.get("mainBusinessFocus") if isinstance(company_vision_inner, dict) else None
        if mb:
            return [mb] if isinstance(mb, str) else mb
        return None

    def _main_products():
        bev = summary.get("기업비전")
        if isinstance(bev, dict) and bev.get("주요 취급품목"):
            return bev.get("주요 취급품목")
        return None

    def _ceo_val():
        v = _v("대표자명", "representative", "CEO", default=None)
        if v is None:
            return "—"
        if isinstance(v, list):
            return ", ".join(str(x) for x in v if x)
        return str(v)

    return {
        "업종": _v("업종", "industry", default="—"),
        "대표자명": _ceo_val(),
        "홈페이지": _strip_url(_v("홈페이지", "website", default="")),
        "주소": address_val,
        "사업내용": summary.get("사업내용"),
        "business_content": _v("business_content", "businessDescription", default=None),
        "business_activities": _v("business_activities", default=None),
        "기업비전": summary.get("기업비전"),
        "주요_사업내용_리스트": _main_business(),
        "주요_취급품목": _main_products(),
        "coreProducts": inner.get("coreProducts") if isinstance(inner, dict) else None,
        "keyProducts": (company_vision_inner.get("keyProducts") or []) if isinstance(company_vision_inner, dict) else None,
        "company_vision": _v("company_vision", default=None),
        "company_overview": _v("company_overview", default=None),
        "business_vision": _v("business_vision", default=None),
        "organizational_culture": summary.get("organizational_culture"),
    }


def build_html(data, company_name=None, dart_data=None):
    """Sky_Analysis_Report.html과 동일한 형식의 HTML 문자열 생성. data 키는 '{company_name}.json' 등.
    dart_data: dart 폴더의 사업보고서 JSON (재무지표 등 포함). 있으면 우선 사용.
    """
    name = company_name or "대주산업"
    f1, f2, f3, f4 = _json_filenames(name)
    company = data.get(f1) or {}
    jd_data = data.get(f2) or {}
    news_data = data.get(f3) or {}
    homepage = data.get(f4) or {}
    s = _normalize_summary(homepage)
    full_content = (company.get("full_content") or "")[:3000]
    company_name = company.get("company_name") or name
    target_job = company.get("target_job") or "—"

    # dart 데이터에서 재무지표 및 기업정보 추출
    dart_fin = _parse_dart_financial(dart_data) if dart_data else {}
    dart_info = _get_dart_company_info(dart_data) if dart_data else {}
    dart_biz_overview = _get_dart_business_overview(dart_data) if dart_data else ""

    # 기업 기본 정보 (dart 우선 → homepage → company.json 순서)
    industry = dart_info.get("industry") or s["업종"] or "—"
    ceo = dart_info.get("ceo_name") or s["대표자명"] or "—"
    url_home = dart_info.get("homepage") or s["홈페이지"] or "#"
    address = dart_info.get("address") or s["주소"] or "—"
    # 설립일: dart 우선
    founded = "—"
    if dart_info.get("establishment_date"):
        founded = dart_info["establishment_date"]
    elif full_content:
        m = re.search(r"(\d{4})\s*년\s*(?:창립|설립)", full_content)
        if m:
            founded = "{}년 (공고 기준)".format(m.group(1))
        else:
            m = re.search(r"(\d{2,4})\s*년\s*상반기", full_content)
            if m:
                y = m.group(1)
                founded = "20{}년 상반기 (공고 기준)".format(y) if len(y) <= 2 else "{}년 (공고 기준)".format(y)

    # 기업 개요: 홈페이지 → 채용공고 순으로 반영 (dart 사업개요는 재무지표 탭에 표시)
    vision_lines = []
    # 1) 홈페이지 company_overview / business_vision / company_vision (문자열) 우선
    overview = (s.get("company_overview") or "").strip()
    bvision = (s.get("business_vision") or "").strip()
    cv_raw = s.get("company_vision")
    # company_vision이 dict인 경우(캠아이티 등): core_business, main_products 등으로 문자열 생성
    if isinstance(cv_raw, dict):
        parts = []
        if cv_raw.get("core_business"):
            parts.append(str(cv_raw["core_business"]))
        mp = cv_raw.get("main_products") or cv_raw.get("key_products")
        if mp and isinstance(mp, list):
            parts.append("주요 제품: " + ", ".join(str(x) for x in mp))
        elif mp:
            parts.append("주요 제품: " + str(mp))
        cv_text = " | ".join(parts).strip()
    else:
        cv_text = (cv_raw or "").strip() if isinstance(cv_raw, str) else ""
    if overview:
        vision_lines.append("기업 개요")
        vision_lines.append("- " + overview)
    if bvision:
        vision_lines.append("")
        vision_lines.append("비전/지향점")
        vision_lines.append("- " + bvision)
    if cv_text:
        if "비전" not in "\n".join(vision_lines):
            vision_lines.append("")
            vision_lines.append("비전/지향점")
        vision_lines.append("- " + cv_text)
    # 2) 홈페이지 organizational_culture (객체 → 불릿)
    org_culture = s.get("organizational_culture")
    if org_culture and isinstance(org_culture, dict):
        vision_lines.append("")
        vision_lines.append("조직 문화")
        for k, v in org_culture.items():
            if v and str(v).strip():
                vision_lines.append("- " + str(v).strip())
    # 3) 홈페이지 기업비전(객체, 대주산업 형)
    bev = s.get("기업비전") or {}
    if bev and isinstance(bev, dict):
        vision_lines.append("")
        vision_lines.append("비전/주요 사업")
        for k, v in bev.items():
            if isinstance(v, list):
                vision_lines.append("- {}: {}".format(k, ", ".join(str(x) for x in v)))
            elif v:
                vision_lines.append("- {}: {}".format(k, v))
    # 4) 공고 전문(full_content) 앞부분 — 개요가 아직 비었거나 보강
    if full_content and len(vision_lines) < 4:
        vision_lines.append("")
        vision_lines.append("채용 공고 소개")
        first_lines = [x.strip() for x in full_content.split("\n") if x.strip()][:10]
        for line in first_lines:
            if len(line) > 3 and not line.startswith("모집부문") and not line.startswith("담당업무") and not line.startswith("자격요건"):
                vision_lines.append("- " + line)
    vision_text = "\n".join(vision_lines) if vision_lines else "기업 개요 및 비전 (채용 공고·홈페이지 참조)."
    vision_text = escape(vision_text).replace("\n", "<br>\n")

    # JD 분석: 상단 카드(HARD/SOFT) + 하단 상세(1·2번 제거, 3번 인재상은 JD 탭 하단에 표시)
    jd_report = jd_data.get("jd_analysis_report") or ""
    hard_text, soft_text, _ = parse_jd_sections(jd_report)
    jd_detail_only, jd_talent_section = _jd_detail_without_123_and_talent(jd_report)
    hard_html = escape(hard_text).replace("\n", "<br>\n")
    soft_html = escape(soft_text).replace("\n", "<br>\n")
    jd_full_esc = escape(jd_detail_only)
    jd_full_esc = re.sub(r"\n", "<br>\n", jd_full_esc)
    jd_full_esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", jd_full_esc)

    # 주요 사업: 기업 개요 탭용 (홈페이지/공고 기반)
    main_business_lines = ["주요 사업내용"]
    biz_list = s.get("사업내용")
    if isinstance(biz_list, list):
        for x in biz_list:
            main_business_lines.append("- " + str(x))
    elif isinstance(biz_list, str) and biz_list.strip():
        main_business_lines.append("- " + biz_list.strip())
    main_biz_list = s.get("주요_사업내용_리스트")
    if main_biz_list:
        for x in (main_biz_list if isinstance(main_biz_list, list) else [main_biz_list]):
            if x and str(x).strip():
                main_business_lines.append("- " + str(x).strip())
    main_products = s.get("주요_취급품목")
    if isinstance(main_products, list):
        main_business_lines.append("- 주요 취급품목: " + ", ".join(str(p) for p in main_products))
    biz_str = s.get("business_content") or s.get("business_activities")
    if biz_str:
        main_business_lines.append("- " + str(biz_str))
    core_products = s.get("coreProducts")
    if isinstance(core_products, list):
        for item in core_products:
            if isinstance(item, dict):
                cat = item.get("category") or item.get("categoryName") or ""
                details = item.get("details") or []
                if cat:
                    detail_str = ", ".join(details) if isinstance(details, list) else str(details)
                    main_business_lines.append("- [{}] {}".format(cat, detail_str) if detail_str else "- " + cat)
            elif item:
                main_business_lines.append("- " + str(item))
    key_products = s.get("keyProducts")
    if isinstance(key_products, list) and key_products:
        main_business_lines.append("- 주요 제품: " + ", ".join(str(p) for p in key_products))
    main_business_text = "\n".join(main_business_lines)
    main_business_html = escape(main_business_text).replace("\n", "<br>\n")
    main_business_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", main_business_html)

    # 인재상/조직 문화: JD 직무분석 탭용 (JD 3번 + 홈페이지)
    talent_lines = ["인재상/조직 문화"]
    if jd_talent_section:
        for line in jd_talent_section.split("\n"):
            line = line.strip()
            if line and (line.startswith("- ") or line.startswith("• ")):
                talent_lines.append(line if line.startswith("- ") else "- " + line[1:].strip())
            elif line:
                talent_lines.append("- " + line)
    if overview:
        talent_lines.append("- " + overview)
    if bvision:
        talent_lines.append("- " + bvision)
    if cv_text:
        talent_lines.append("- " + cv_text)
    org_culture = s.get("organizational_culture")
    if org_culture and isinstance(org_culture, dict):
        for k, v in org_culture.items():
            if v and str(v).strip():
                talent_lines.append("- " + str(v).strip())
    if not (overview or bvision or cv_text or (org_culture and isinstance(org_culture, dict)) or jd_talent_section):
        talent_lines.append("- 채용 공고상 기업 비전 및 조직 문화는 공고·홈페이지를 참조해 주세요.")
    talent_text = "\n".join(talent_lines)
    talent_html = escape(talent_text).replace("\n", "<br>\n")
    talent_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", talent_html)

    # 재무: 데이터 없음 시 "-" 표시
    def fm(val):
        if val is None or val == "":
            return "—"
        return str(val)

    # 뉴스 (각 항목 pubDate 반영, 없으면 analyzed_at 기준 표기)
    news_list = news_data.get("news_list") or []
    analyzed_at = news_data.get("analyzed_at") or ""
    news_items_html = []
    for n in news_list[:10]:
        title = n.get("title") or "(제목 없음)"
        link = n.get("link") or "#"
        date_str = _format_news_date(n)
        if date_str == "날짜 없음" and analyzed_at:
            date_str = _format_news_date({"pubDate": analyzed_at})
        summary_text = news_analysis_to_summary(n)
        news_items_html.append(
            """
                        <div class="news-item">
                            <a href="{link}" class="news-title" target="_blank">🔗 {title}</a>
                            <div style="font-size:0.85rem; color:var(--text-dim); margin-bottom:8px;">{date}</div>
                            <div class="pre-wrap" style="color:var(--text); font-size:0.9rem;"><strong>AI 요약:</strong> {summary}</div>
                        </div>""".format(
                link=escape(link),
                title=escape(title),
                date=escape(date_str),
                summary=escape(summary_text),
            )
        )
    news_html = "\n".join(news_items_html) if news_items_html else "<p>수집된 뉴스가 없습니다.</p>"

    # Sky 형식과 동일한 HTML (제목·탭·스타일 동일, 내용만 치환)
    html_template = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{company_name} 분석 리포트</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
    <style>
        :root {{
            --bg: #f8fafc; --card: #ffffff; --primary: #0f172a; --text: #334155; --text-dim: #64748b; --accent: #0ea5e9; --border: #e0f2fe;
            --sky-bg: #f0f9ff; --hard-line: #ef4444; --soft-line: #10b981;
        }}
        body {{ font-family: 'Pretendard', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 40px; line-height: 1.6; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ margin-bottom: 30px; border-bottom: 3px solid var(--accent); padding-bottom: 20px; }}
        .header h1 {{ margin: 0; color: var(--primary); font-size: 2rem; }}

        .tabs {{ display: flex; gap: 5px; margin-bottom: -1px; }}
        .tab {{ background: #e0f2fe; border: 1px solid var(--border); border-bottom: none; color: #0369a1; padding: 10px 20px; cursor: pointer; border-radius: 8px 8px 0 0; font-weight: 600; text-decoration: none; display: inline-block; }}
        .tab:hover {{ background: #bae6fd; color: #0369a1; }}
        .tab.active {{ background: var(--card); color: var(--accent); border-top: 3px solid var(--accent); padding-bottom: 11px; }}
        .content-box:has(#tab2:target) a.tab[href="#tab2"], .content-box:has(#tab3:target) a.tab[href="#tab3"], .content-box:has(#tab4:target) a.tab[href="#tab4"] {{ background: var(--card); color: var(--accent); border-top: 3px solid var(--accent); padding-bottom: 11px; }}
        .content-box:has(#tab2:target) a.tab[href="#tab1"], .content-box:has(#tab3:target) a.tab[href="#tab1"], .content-box:has(#tab4:target) a.tab[href="#tab1"] {{ background: #e0f2fe; color: #0369a1; border-top: 1px solid var(--border); padding-bottom: 10px; }}

        .content-box {{ background: var(--card); border: 1px solid var(--border); padding: 40px; border-radius: 0 0 12px 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        /* v-html 내부 script 미실행 → 링크(#hash) + :target으로 탭 전환 (클릭 시 반응) */
        .tab-content:target {{ display: block !important; }}
        #tab1.tab-content {{ display: block; }}
        .content-box:has(#tab2:target) #tab1.tab-content {{ display: none !important; }}
        .content-box:has(#tab3:target) #tab1.tab-content {{ display: none !important; }}
        .content-box:has(#tab4:target) #tab1.tab-content {{ display: none !important; }}

        .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        .info-table th {{ text-align: left; background: var(--sky-bg); color: #0369a1; padding: 12px 15px; border: 1px solid var(--border); font-weight: 600; }}
        .info-table td {{ padding: 12px 15px; border: 1px solid var(--border); color: var(--text); }}

        .jd-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
        .skill-card {{ padding: 20px; border-radius: 8px; border: 1px solid var(--border); background: #ffffff; }}
        .skill-card.hard {{ border-left: 5px solid var(--hard-line); }}
        .skill-card.soft {{ border-left: 5px solid var(--soft-line); }}

        .section-card {{ background: var(--sky-bg); padding: 25px; border-radius: 12px; margin-top: 20px; border: 1px solid var(--border); }}
        .pre-wrap {{ white-space: pre-wrap; font-size: 0.95rem; }}

        .news-item {{ padding: 15px 0; border-bottom: 1px solid var(--border); }}
        .news-title {{ font-size: 1.1rem; color: #0284c7; text-decoration: none; font-weight: 700; display: block; margin-bottom: 5px; }}

        h2 {{ color: var(--primary); border-left: 5px solid var(--accent); padding-left: 12px; margin-bottom: 25px; font-size: 1.4rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>{company_name} 기업 분석 보고서</h1></div>
        <div class="tabs">
            <a href="#tab1" class="tab active">기업 개요</a>
            <a href="#tab2" class="tab">JD 직무 분석</a>
            <a href="#tab3" class="tab">재무 지표</a>
            <a href="#tab4" class="tab">최신 뉴스</a>
        </div>
        <div class="content-box">
            <div id="tab1" class="tab-content active">
                <h2>🏢 기본 기업 정보</h2>
                <table class="info-table">
                    <tr><th style="width:180px;">기업명</th><td>(주){company_name}</td></tr>
                    <tr><th>업종</th><td>{industry}</td></tr>
                    <tr><th>대표자</th><td>{ceo}</td></tr>
                    <tr><th>설립일</th><td>{founded}</td></tr>
                    <tr><th>주소</th><td>{address}</td></tr>
                    <tr><th>홈페이지</th><td><a href="{url_home}" target="_blank" style="color:var(--accent); font-weight:600;">{url_home}</a></td></tr>
                </table>
                <div class="section-card pre-wrap"><strong>[비전 및 지향점]</strong><br><br>{vision_html}</div>
                <div class="section-card pre-wrap" style="margin-top:20px;"><strong>[주요 사업]</strong><br><br>{main_business_html}</div>
            </div>

            <div id="tab2" class="tab-content">
                <h2>🎯 '(주){company_name}:{target_job}' 직무 요약</h2>
                <div class="jd-grid">
                    <div class="skill-card hard"><strong style="color:var(--hard-line);">HARD SKILL</strong><br><br><div class="pre-wrap">{hard_html}</div></div>
                    <div class="skill-card soft"><strong style="color:var(--soft-line);">SOFT SKILL</strong><br><br><div class="pre-wrap">{soft_html}</div></div>
                </div>
                <div class="section-card">
                    <div class="pre-wrap">{jd_detail_html}</div>
                </div>
                <div class="section-card" style="margin-top:20px;">
                    <div class="pre-wrap"><strong>[인재상/조직 문화]</strong><br><br>{talent_html}</div>
                </div>
            </div>

            <div id="tab3" class="tab-content">
                <h2>📊 핵심 재무 지표 요약</h2>
                <div class="section-card">
                    <table class="info-table">
                        <thead>
                            <tr><th>주요 재무 항목</th><th>금액 (백만 원)</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>유동자산</td><td>{fa}</td></tr>
                            <tr><td>비유동자산</td><td>{nfa}</td></tr>
                            <tr><td><b>자산총계</b></td><td><b>{ta}</b></td></tr>
                            <tr><td>부채총계</td><td>{tl}</td></tr>
                            <tr><td>자본총계</td><td>{te}</td></tr>
                            <tr><td colspan="2" style="background:#f0f9ff; height:10px;"></td></tr>
                            <tr><td>매출액</td><td>{rev}</td></tr>
                            <tr><td>영업이익</td><td>{oi}</td></tr>
                            <tr><td>당기순이익</td><td>{ni}</td></tr>
                        </tbody>
                    </table>
                </div>
                {dart_biz_section}
            </div>

            <div id="tab4" class="tab-content">
                <h2>📰 최신 뉴스 업데이트</h2>
                <div class="news-list">
                    {news_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    # dart 재무지표 우선 사용
    fa_val = dart_fin.get("유동자산")
    nfa_val = dart_fin.get("비유동자산")
    ta_val = dart_fin.get("자산총계")
    tl_val = dart_fin.get("부채총계")
    te_val = dart_fin.get("자본총계")
    rev_val = dart_fin.get("매출액")
    oi_val = dart_fin.get("영업이익")
    ni_val = dart_fin.get("당기순이익")

    # dart 사업개요 및 주요 제품/서비스 섹션 (재무지표 탭에 표시)
    dart_biz_section = ""
    if dart_biz_overview or dart_data:
        dart_products = _get_dart_products_services(dart_data) if dart_data else ""
        dart_parts = []
        if dart_biz_overview:
            summary = dart_biz_overview[:2500].strip()
            if len(dart_biz_overview) > 2500:
                summary += "..."
            dart_parts.append("<h3 style='margin-top:20px;'>📋 사업의 개요 (사업보고서)</h3>")
            dart_parts.append("<div class='section-card pre-wrap'>" + escape(summary).replace("\n", "<br>\n") + "</div>")
        if dart_products:
            summary = dart_products[:2500].strip()
            if len(dart_products) > 2500:
                summary += "..."
            dart_parts.append("<h3 style='margin-top:20px;'>🏭 주요 제품 및 서비스 (사업보고서)</h3>")
            dart_parts.append("<div class='section-card pre-wrap'>" + escape(summary).replace("\n", "<br>\n") + "</div>")
        if dart_parts:
            dart_biz_section = "\n".join(dart_parts)

    return html_template.format(
        company_name=escape(company_name),
        industry=escape(industry),
        ceo=escape(ceo),
        founded=escape(founded),
        address=escape(address),
        url_home=escape(url_home),
        vision_html=vision_text,
        main_business_html=main_business_html,
        target_job=escape(target_job),
        hard_html=hard_html,
        soft_html=soft_html,
        jd_detail_html=jd_full_esc,
        talent_html=talent_html,
        fa=fm(fa_val),
        nfa=fm(nfa_val),
        ta=fm(ta_val),
        tl=fm(tl_val),
        te=fm(te_val),
        rev=fm(rev_val),
        oi=fm(oi_val),
        ni=fm(ni_val),
        dart_biz_section=dart_biz_section,
        news_html=news_html,
    )


def build_html_from_dir(company_dir, company_name):
    """
    지정한 회사 폴더에서 통합 JSON 1개(_통합.json) 또는 4개 JSON을 읽어 HTML 문자열 반환.
    _통합.json이 있으면 그것만 사용, 없으면 기존 4개 파일 로드.
    dart 폴더에 기업이 있으면 재무지표 등 dart 데이터 우선 사용.
    API에서 분석 완료 후 HTML을 만들 때 사용.
    """
    data = load_merged_report(company_dir=company_dir, company_name=company_name)
    if data is None:
        data = load_json_files(company_dir=company_dir, company_name=company_name)
    # 사업보고서 데이터: CSV에 기업명이 있으면 MongoDB 우선 조회, 없으면 dart 폴더 JSON
    dart_data = None
    if company_name in _load_dart_company_set():
        dart_data = _load_dart_data_from_mongo(company_name)
        if dart_data:
            print(f"[MongoDB] '{company_name}' 사업보고서 데이터 로드됨 (재무지표 포함)")
        if not dart_data and _find_dart_json(company_name):
            dart_data = _load_dart_data(company_name)
            if dart_data:
                print(f"[dart 폴더] '{company_name}' 사업보고서 데이터 로드됨 (재무지표 포함)")
    return build_html(data, company_name=company_name, dart_data=dart_data)


def main(company_dir=None, company_name=None):
    """통합 JSON 1개 또는 4개 JSON 로드 → HTML 생성 → 파일 저장.
    company_dir/company_name은 공고 기준으로 전달.
    dart 폴더에 기업이 있으면 재무지표 등 dart 데이터 우선 사용.
    """
    name = company_name or "대주산업"
    base = company_dir if company_dir else os.path.join(SCRIPT_DIR, name)
    data = load_merged_report(company_dir=base, company_name=name)
    if data is None:
        data = load_json_files(company_dir=base, company_name=name)
        print("4개 JSON 로드 완료. Sky 형식 HTML 생성 중...")
    else:
        print("통합 JSON 로드 완료. Sky 형식 HTML 생성 중...")

    # 사업보고서 데이터: CSV에 기업명이 있으면 MongoDB 우선 조회, 없으면 dart 폴더 JSON
    dart_data = None
    if name in _load_dart_company_set():
        dart_data = _load_dart_data_from_mongo(name)
        if dart_data:
            print(f"[MongoDB] '{name}' 사업보고서 데이터 로드됨 (재무지표 포함)")
        if not dart_data and _find_dart_json(name):
            dart_data = _load_dart_data(name)
            if dart_data:
                print(f"[dart 폴더] '{name}' 사업보고서 데이터 로드됨 (재무지표 포함)")
    if not dart_data:
        print(f"[사업보고서] '{name}' → CSV/DB에 없음, 기본 데이터만 사용")

    html_str = build_html(data, company_name=name, dart_data=dart_data)
    output_path = os.path.join(base, f"{name}_Analysis_Report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_str)
    print("HTML 저장 완료: {}".format(output_path))
    return output_path


if __name__ == "__main__":
    import sys
    # 사용법: python analysis_report.py [company_dir] [company_name]
    company_dir = sys.argv[1] if len(sys.argv) > 1 else None
    company_name = sys.argv[2] if len(sys.argv) > 2 else None
    main(company_dir=company_dir, company_name=company_name)
