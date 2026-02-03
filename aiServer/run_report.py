# -*- coding: utf-8 -*-
"""
이미 4개 JSON이 있는 기업 폴더에 대해 HTML 보고서만 생성.
사용법: python run_report.py <기업명> [기준경로]
  예: python run_report.py 원클라스
  (기준경로 생략 시 프로젝트 루트 아래 <기업명> 폴더 사용)
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import analysis_report


def main():
    if len(sys.argv) < 2:
        print("사용법: python run_report.py <기업명> [기준경로]")
        print("  예: python run_report.py 원클라스")
        sys.exit(1)
    company_name = sys.argv[1].strip()
    base_dir = sys.argv[2].strip() if len(sys.argv) > 2 else BASE
    company_dir = os.path.join(base_dir, company_name)
    if not os.path.isdir(company_dir):
        print("오류: 폴더가 없습니다:", company_dir)
        sys.exit(2)
    analysis_report.main(company_dir=company_dir, company_name=company_name)


if __name__ == "__main__":
    main()
