import json
import time
import os
import re
import sys

# Windows 콘솔 UTF-8 인코딩 (이모지 출력 오류 방지)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import requests
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutError
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from newspaper import Article

# Google Cloud Vision 라이브러리 체크
try:
    from google.cloud import vision
except ImportError:
    print("❌ 라이브러리 미설치: google-cloud-vision 설치 필요 (pip install google-cloud-vision)")

# ==========================================
# 0. 환경 설정 (.env 파일 또는 환경변수에서 로드)
# ==========================================
_AI_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_AI_SERVER_DIR)  # 프로젝트 루트 (aiServer 상위)

try:
    from dotenv import load_dotenv
    # 프로젝트 루트의 .env 로드 (aiServer에서 실행해도 동작)
    load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))
    load_dotenv()  # 현재 디렉터리 .env도 시도
except ImportError:
    pass  # dotenv 없으면 환경변수 직접 사용

# Google Cloud Vision 인증 (JSON 키 파일 경로) — 상대 경로면 프로젝트 루트 기준으로 절대 경로로 변환
_gcp_cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if _gcp_cred:
    if not os.path.isabs(_gcp_cred):
        _gcp_cred = os.path.normpath(os.path.join(_PROJECT_ROOT, _gcp_cred))
    if os.path.isfile(_gcp_cred):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = _gcp_cred
    else:
        print(f"⚠️ GOOGLE_APPLICATION_CREDENTIALS 파일 없음: {_gcp_cred}")

# API 키 (환경변수에서 가져옴)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

if not OPENAI_API_KEY:
    print("⚠️ 경고: OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# OpenAI 클라이언트 초기화
client_ai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Chrome 109+ 권장
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")  # Windows에서 invalid argument 방지
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Windows에서는 --force-device-scale-factor 제외 (invalid argument 원인 될 수 있음)
    if sys.platform != "win32":
        chrome_options.add_argument("--force-device-scale-factor=2")

    # Linux(GCP 등): 시스템 Chrome 경로 사용
    if sys.platform != "win32":
        chrome_path = "/usr/bin/google-chrome"
        if os.path.isfile(chrome_path):
            chrome_options.binary_location = chrome_path
            chrome_options.add_argument("--disable-software-rasterizer")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # 페이지 로드 대기 시간 제한 (120초 기본 → 60초로 축소, Read timed out 방지)
    driver.set_page_load_timeout(60)
    return driver

# ==========================================
# A-1. 채용공고 수집 및 OCR 단계
# ==========================================
def process_job_full_pipeline(target_url=None, selected_job=None, experience_level=None, save_base_dir="."):
    """채용공고 URL로부터 1차 JSON 생성. 인자를 주지 않으면 input()으로 입력받음."""
    if target_url is None:
        target_url = input("🔗 분석할 채용공고 URL 입력: ").strip()
    if selected_job is None:
        print("\n--- 분석 대상 정보 입력 ---")
        selected_job = input("✅ 지원할 구체적인 직무명을 입력하세요: ").strip()
    if experience_level is None:
        experience_level = input("✅ 경력 구분을 입력하세요: ").strip()
    
    driver = setup_driver()
    try:
        print(f"\n🌐 [1/3] 페이지 접속 중...")
        driver.get(target_url)
        time.sleep(5)

        page_title = driver.title
        match = re.search(r'\[(.*?)\]', page_title)
        raw_company = match.group(1) if match else "Unknown"
        clean_company = re.sub(r'\(주\)|주식회사|㈜|[\\/:*?"<>|]', '', raw_company).strip()
        
        company_dir = os.path.join(save_base_dir, clean_company)
        if not os.path.exists(company_dir): os.makedirs(company_dir)
        print(f"🏢 기업명 확인: {clean_company} (폴더: {os.path.abspath(company_dir)})")

        print("📸 [2/3] 공고 내용 캡처 및 OCR 진행 중...")
        target_element = None
        wait = WebDriverWait(driver, 10)
        # iframe 시도 (사람인/잡코리아 일부 공고)
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    src = iframe.get_attribute("src") or ""
                    if any(k in src for k in ["view", "detail", "job"]):
                        driver.switch_to.frame(iframe)
                        target_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        break
                except Exception:
                    driver.switch_to.default_content()
                    continue
        except Exception:
            driver.switch_to.default_content()

        # iframe 실패 시 메인 페이지 셀렉터 (사람인 relay/일반 상세, 잡코리아 등)
        if not target_element:
            driver.switch_to.default_content()
            selectors = [".jv_detail", ".user_content", "#content", "article", "main", ".job_detail", ".detail_content", "#job_content"]
            for s in selectors:
                try:
                    el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s)))
                    if el.is_displayed():
                        target_element = el
                        break
                except Exception:
                    continue

        # 스크린샷: target_element 있으면 해당 영역, 없거나 실패 시 전체 화면
        try:
            if target_element:
                total_height = driver.execute_script("return document.body.scrollHeight")
                driver.set_window_size(1600, min(total_height + 500, 8000))
                time.sleep(2)
                image_content = target_element.screenshot_as_png
            else:
                image_content = driver.get_screenshot_as_png()
        except Exception:
            image_content = driver.get_screenshot_as_png()

        client_vision = vision.ImageAnnotatorClient()
        ocr_response = client_vision.document_text_detection(image=vision.Image(content=image_content))
        full_ocr_text = ocr_response.full_text_annotation.text 

        print(f"🤖 [3/3] OpenAI를 활용해 정제 중...")
        response = client_ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 채용 공고 정제 전문가입니다."},
                {"role": "user", "content": f"직무 '{selected_job}', 경력 '{experience_level}' 내용 추출:\n{full_ocr_text[:5000]}"}
            ],
            temperature=0
        )
        refined_job_content = response.choices[0].message.content

        data = {
            "company_name": clean_company,
            "company_dir": company_dir, 
            "target_job": f"{selected_job} ({experience_level})",
            "target_url": target_url,
            "full_content": full_ocr_text,         
            "refined_job_content": refined_job_content 
        }
        
        json_path = os.path.join(company_dir, f"{clean_company}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"✨ A-1 완료! 파일 저장됨: {json_path}")
        return data
    except Exception as e:
        print(f"❌ A-1 오류 발생: {e}")
        return None
    finally:
        driver.quit()

# ==========================================
# A-2. JD 전략 분석 단계
# ==========================================
def analyze_jd_strategy(data):
    if not data: return None
    company_name = data.get('company_name', 'Unknown')
    company_dir = data.get('company_dir', '.')
    
    print(f"🧠 '{company_name}' 전략 분석 시작 (OpenAI)...")
    strategy_prompt = f"""
    당신은 전문 채용 컨설턴트입니다. 아래 [직무 상세]를 바탕으로 합격 전략서를 작성하세요.
    [직무 상세]: {data['refined_job_content']}
    [공고 전문]: {data['full_content'][:2000]}
    (1. HARD SKILL, 2. SOFT SKILL, 3. 인재상, 4. 이유, 5. 시사점 포함)
    """
    
    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "전략적인 채용 분석 전문가입니다. 불렛포인트 중심, 구어체로 작성하세요."},
                {"role": "user", "content": strategy_prompt}
            ],
            temperature=0.2
        )
        strategy_result = response.choices[0].message.content
        data['jd_analysis_report'] = strategy_result
        
        json_path = os.path.join(company_dir, f"{company_name}_JD분석.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"✨ A-2 단계 완료! 파일 저장됨: {json_path}")
        return data
    except Exception as e:
        print(f"❌ A-2 오류: {e}")
        return data

# ==========================================
# B. 뉴스 분석 단계
# ==========================================
def run_news_analysis(data):
    if not data: return None
    company_name = data.get("company_name", "")
    company_dir = data.get("company_dir", ".")
    
    print(f"📰 [B] '{company_name}' 뉴스 분석 중...")
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": company_name, "display": 5, "sort": "sim"}
    
    news_results = []
    try:
        res = requests.get(url, headers=headers, params=params)
        items = res.json().get('items', [])
        for i in items:
            link = i['originallink'] or i['link']
            try:
                article = Article(link, language='ko')
                article.download(); article.parse()
                content = article.text.strip()
            except:
                content = i['description']

            resp = client_ai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "시니어 기업분석가. JSON으로 응답."},
                    {"role": "user", "content": f"'{company_name}' 분석: {content[:2000]}"}
                ],
                response_format={ "type": "json_object" }
            )
            news_results.append({
                "title": re.sub(r'<[^>]*>', '', i['title']),
                "link": link,
                "pubDate": i.get("pubDate", ""),
                "analysis": json.loads(resp.choices[0].message.content)
            })
            
        data["news_analysis"] = {"news_list": news_results, "analyzed_at": time.strftime('%Y-%m-%d %H:%M:%S')}
        save_path = os.path.join(company_dir, f"{company_name}_NEWS.json")
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data["news_analysis"], f, ensure_ascii=False, indent=4)
        print(f"✅ 뉴스 분석 완료! 저장됨: {save_path}")
    except Exception as e:
        print(f"❌ 뉴스 분석 오류: {e}")
    return data

# ==========================================
# C. 기업 홈페이지(상세) 분석 단계
# ==========================================
def run_homepage_analysis(data):
    if not data: return None
    target_url = data.get("target_url") 
    company_name = data.get("company_name", "Unknown")
    company_dir = data.get("company_dir", ".") 
    
    print(f"🚀 [C] '{company_name}' 정밀 크롤링 시작...")
    driver = setup_driver()
    raw_text = ""
    try:
        try:
            driver.get(target_url)
        except SeleniumTimeoutError:
            print("⚠️ 메인 페이지 로드 타임아웃(60초), 현재 페이지 소스로 진행합니다.")
        time.sleep(3)
        detail_link = None
        for el in driver.find_elements(By.TAG_NAME, "a"):
            href = el.get_attribute("href") or ""
            if "company-info/view" in href:
                detail_link = href
                break

        if detail_link:
            try:
                driver.get(detail_link)
            except SeleniumTimeoutError:
                print("⚠️ 상세 페이지 로드 타임아웃(60초), 현재 페이지 소스로 진행합니다.")
            time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content_fold = soup.find('div', class_='content_fold')
        raw_text = content_fold.get_text(strip=False) if content_fold else ""

        if not raw_text or len(raw_text.strip()) < 50:
            data["company_homepage_info"] = {"summary": {"company_overview": "홈페이지 수집 내용이 없거나 타임아웃되었습니다."}}
        else:
            response = client_ai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "기업 분석가. JSON 응답."},
                          {"role": "user", "content": f"요약: {raw_text[:2000]}"}],
                response_format={"type": "json_object"}
            )
            data["company_homepage_info"] = {"summary": json.loads(response.choices[0].message.content)}

        save_path = os.path.join(company_dir, f"{company_name}_homepage.json")
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data["company_homepage_info"], f, ensure_ascii=False, indent=4)
        print(f"✨ [성공] 홈페이지 분석 완료: {save_path}")
    except Exception as e:
        print(f"❌ 홈페이지 분석 오류: {e}")
        if "company_homepage_info" not in data:
            data["company_homepage_info"] = {"summary": {"company_overview": f"홈페이지 분석 중 오류: {e}"}}
    finally:
        driver.quit()
    return data

# ==========================================
# 전체 파이프라인 (API/스크립트 공용)
# ==========================================
def run_full_analysis_pipeline(target_url=None, selected_job=None, experience_level=None, save_base_dir="."):
    """
    채용공고 URL → 공고 기준 폴더 생성 → 4개 JSON → HTML 보고서까지 한 번에 실행.
    (프론트에서 전달받은 공고 URL/직무/경력 기준으로 폴더명·파일 생성)
    반환: (final_data, company_dir) 또는 (None, None)
    """
    final_data = process_job_full_pipeline(
        target_url=target_url,
        selected_job=selected_job,
        experience_level=experience_level,
        save_base_dir=save_base_dir,
    )
    if not final_data:
        return None, None
    final_data = analyze_jd_strategy(final_data)
    final_data = run_news_analysis(final_data)
    final_data = run_homepage_analysis(final_data)
    company_dir = final_data.get("company_dir", ".")
    company_name = final_data.get("company_name", "")
    # 4개 JSON을 하나로 합쳐 _report.json 저장 후 HTML 생성
    try:
        import analysis_report
        filenames = analysis_report._json_filenames(company_name)
        merged = {}
        for fn in filenames:
            path = os.path.join(company_dir, fn)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    merged[fn] = json.load(f)
        report_path = os.path.join(company_dir, f"{company_name}_통합.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        print(f"📦 통합 JSON 저장: {report_path}")
        abs_dir = os.path.abspath(company_dir)
        analysis_report.main(company_dir=abs_dir, company_name=company_name)
    except Exception as e:
        print(f"⚠️ 보고서 생성 실패: {e}")
    return final_data, company_dir


# ==========================================
# 메인 실행부 (공고 기준 폴더 생성 → 4개 JSON → HTML 보고서까지 통합)
# ==========================================
if __name__ == "__main__":
    final_data, company_dir = run_full_analysis_pipeline()
    if final_data:
        print("\n🎉 모든 분석이 완료되었습니다.")
        print("📁 결과 폴더:", os.path.abspath(company_dir))
        # 같은 공고 기준 폴더에 HTML 보고서 자동 생성
        try:
            import analysis_report  # noqa: F401
            company_name = final_data.get("company_name", "")
            abs_dir = os.path.abspath(company_dir)
            analysis_report.main(company_dir=abs_dir, company_name=company_name)
        except Exception as e:
            print("⚠ HTML 자동 생성 실패:", e)
            print("💡 수동 생성: python run_report.py <기업명>")