#!/usr/bin/env python3
"""
단일 파일 테스트 스크립트 (gemini-2.0-flash-exp)
"""

import os
import json
import time
from pathlib import Path
from agents.agent_factory import AgentFactory
from clients.google_client import GoogleClient
from config.config_loader import ConfigLoader

def test_single_file(file_path: str):
    """단일 파일 테스트"""
    print(f"🔍 파일 테스트: {file_path}")
    print("=" * 50)

    # API 키 로드
    try:
        config_loader = ConfigLoader('config/config.yaml')
        google_config = config_loader.get_llm_config('google')
        api_key = google_config.get('api_key')
        print("✅ API 키 로드 완료")
    except Exception as e:
        print(f"❌ API 키 로드 실패: {e}")
        return

    # 파일 내용 읽기
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"📄 파일 크기: {len(content)} 문자")
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")
        return

    # Google 클라이언트 초기화
    try:
        google_client = GoogleClient(api_key=api_key, model="models/gemini-2.0-flash-exp")
        print(f"✅ 모델 초기화 완료: gemini-2.0-flash-exp")
    except Exception as e:
        print(f"❌ 모델 초기화 실패: {e}")
        return

    # Source Code Agent 생성
    agent = AgentFactory.create_agent('source_code')
    print(f"✅ Agent 생성 완료")

    try:
        # 입력 검증
        if not agent.validate_input(content):
            print(f"❌ 입력 검증 실패")
            return

        # 프롬프트 생성
        if len(content) > 3000:
            content = content[:3000] + "\n... (일부만 분석)"
            print(f"📏 내용이 길어 3000자로 제한")

        prompt = agent.create_prompt(content)
        print(f"📝 프롬프트 길이: {len(prompt)} 문자")

        # API 호출
        print(f"🚀 API 호출 중...")
        start_time = time.time()
        response = google_client.make_request(prompt, max_tokens=2000)
        end_time = time.time()

        print(f"⏱️  응답 시간: {end_time - start_time:.2f}초")
        print(f"📊 토큰 사용량: {response.get('usage', {})}")

        # 결과 파싱
        findings = agent.extract_key_findings(response['content'])

        if findings['valid_json']:
            print(f"✅ JSON 파싱 성공")
            print(f"🎯 신뢰도 점수: {findings['confidence_score']}")
            print(f"📄 요약: {findings['summary']}")

            # 탐지된 취약점들
            vulnerabilities = []
            for key, value in findings['analysis_results'].items():
                if value and value.lower() not in ['none', 'not detected', 'no', '', 'not present']:
                    vulnerabilities.append(key.replace('_', ' ').title())

            print(f"\n🔍 탐지된 취약점들 ({len(vulnerabilities)}개):")
            for i, vuln in enumerate(vulnerabilities[:5], 1):
                print(f"  {i}. {vuln}")

            if len(vulnerabilities) > 5:
                print(f"  ... 및 {len(vulnerabilities) - 5}개 더")

        else:
            print(f"❌ JSON 파싱 실패")
            print(f"🔧 원시 응답 (처음 300자):")
            print(response['content'][:300] + "...")

        # 결과 저장
        result = {
            'file_path': file_path,
            'valid_json': findings['valid_json'],
            'confidence_score': findings['confidence_score'],
            'summary': findings['summary'],
            'analysis_results': findings['analysis_results'],
            'response_time': end_time - start_time,
            'token_usage': response.get('usage', {}),
            'vulnerabilities_count': len(vulnerabilities) if findings['valid_json'] else 0
        }

        filename = f"single_test_result_{Path(file_path).stem}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 결과가 {filename}에 저장되었습니다.")

    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")

def main():
    """메인 함수"""
    # 테스트할 파일 목록
    test_files = [
        "data/test_files/source_code/rsa_public_key_system.java",
        "data/test_files/source_code/elliptic_curve_crypto.py",
        "data/test_files/source_code/aria_korean_block_cipher.py"
    ]

    print("🔐 단일 파일 테스트")
    print("모델: gemini-2.0-flash-exp")
    print("=" * 60)

    for file_path in test_files:
        if Path(file_path).exists():
            test_single_file(file_path)
            print("\n" + "="*60 + "\n")
        else:
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")

if __name__ == "__main__":
    main()