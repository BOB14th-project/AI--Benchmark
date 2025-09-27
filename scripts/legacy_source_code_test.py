#!/usr/bin/env python3
"""
Source Code Agent 테스트 스크립트 (Google API)
양자 취약 암호 알고리즘 탐지 테스트
"""

import os
import json
import time
from typing import Dict, Any
from agents.agent_factory import AgentFactory
from clients.google_client import GoogleClient
from config.config_loader import ConfigLoader

def load_test_files_from_directory() -> Dict[str, str]:
    """data/test_files/source_code 디렉토리에서 실제 테스트 파일들을 로드"""
    import os
    from pathlib import Path

    test_files = {}
    source_code_dir = Path("data/test_files/source_code")

    if not source_code_dir.exists():
        print(f"❌ 테스트 파일 디렉토리가 존재하지 않습니다: {source_code_dir}")
        return test_files

    print(f"📁 테스트 파일 디렉토리: {source_code_dir}")

    # 지원하는 파일 확장자
    supported_extensions = {'.py', '.java', '.c', '.cpp', '.js', '.go', '.rs', '.rb'}

    for file_path in source_code_dir.iterdir():
        if file_path.is_file() and file_path.suffix in supported_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():  # 빈 파일이 아닌 경우만
                        test_files[file_path.stem] = content
                        print(f"  ✅ 로드됨: {file_path.name}")
            except Exception as e:
                print(f"  ❌ 로드 실패: {file_path.name} - {e}")

    return test_files

def test_source_code_agent(api_key: str, test_samples: Dict[str, str]):
    """Source Code Agent 테스트 실행"""

    print("🚀 Source Code Agent 테스트 시작")
    print("=" * 60)

    # Google 클라이언트 초기화 (지정된 모델 사용)
    target_model = "models/gemini-2.0-flash-exp"

    try:
        print(f"🔍 지정된 모델 테스트 중: {target_model}")
        google_client = GoogleClient(api_key=api_key, model=target_model)

        # 간단한 테스트 요청으로 모델 확인
        test_response = google_client.make_request("Hello", max_tokens=10)
        print(f"✅ 모델 작동 확인: {target_model}")

    except Exception as e:
        print(f"❌ {target_model} 사용 실패: {str(e)}")
        print("API 쿼터나 권한을 확인해주세요.")
        return

    print(f"🎯 사용할 모델: {target_model}")

    # Source Code Agent 생성
    agent = AgentFactory.create_agent('source_code')

    print(f"📋 Agent 정보:")
    print(f"   - 이름: {agent.name}")
    print(f"   - 설명: {agent.description}")
    print(f"   - 분석 포인트 수: {len(agent.get_analysis_points())}")
    print()

    results = {}

    for sample_name, source_code in test_samples.items():
        print(f"🔍 테스트 케이스: {sample_name}")
        print("-" * 40)

        try:
            # 입력 검증
            if not agent.validate_input(source_code):
                print(f"❌ 입력 검증 실패: {sample_name}")
                continue

            # 프롬프트 생성
            prompt = agent.create_prompt(source_code)

            print(f"📝 프롬프트 길이: {len(prompt)} 문자")

            # API 호출
            start_time = time.time()
            response = google_client.make_request(prompt, max_tokens=2000)
            end_time = time.time()

            print(f"⏱️  응답 시간: {end_time - start_time:.2f}초")
            print(f"📊 토큰 사용량: {response.get('usage', {})}")

            # 결과 파싱
            findings = agent.extract_key_findings(response['content'])

            results[sample_name] = {
                'valid_json': findings['valid_json'],
                'confidence_score': findings['confidence_score'],
                'summary': findings['summary'],
                'analysis_results': findings['analysis_results'],
                'response_time': end_time - start_time,
                'token_usage': response.get('usage', {}),
                'raw_response': response['content'][:500] + "..." if len(response['content']) > 500 else response['content']
            }

            # 결과 출력
            if findings['valid_json']:
                print(f"✅ JSON 파싱 성공")
                print(f"🎯 신뢰도 점수: {findings['confidence_score']}")
                print(f"📄 요약: {findings['summary']}")
                print(f"🔍 탐지된 취약점 수: {len([k for k, v in findings['analysis_results'].items() if v and v.lower() not in ['none', 'not detected', 'no', '']])}")
            else:
                print(f"❌ JSON 파싱 실패")
                print(f"🔧 원시 응답 (처음 200자): {response['content'][:200]}...")

            print()

        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            results[sample_name] = {'error': str(e)}
            print()

    return results

def save_test_results(results: Dict[str, Any], filename: str = "source_code_test_results.json"):
    """테스트 결과 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 테스트 결과가 {filename}에 저장되었습니다.")

def print_summary(results: Dict[str, Any]):
    """테스트 결과 요약 출력"""
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)

    total_tests = len(results)
    successful_tests = len([r for r in results.values() if 'error' not in r and r.get('valid_json', False)])
    failed_tests = total_tests - successful_tests

    print(f"전체 테스트: {total_tests}")
    print(f"성공: {successful_tests} ✅")
    print(f"실패: {failed_tests} ❌")
    print(f"성공률: {(successful_tests/total_tests)*100:.1f}%")

    if successful_tests > 0:
        avg_confidence = sum(r.get('confidence_score', 0) for r in results.values() if 'error' not in r) / successful_tests
        avg_response_time = sum(r.get('response_time', 0) for r in results.values() if 'error' not in r) / successful_tests

        print(f"평균 신뢰도 점수: {avg_confidence:.3f}")
        print(f"평균 응답 시간: {avg_response_time:.2f}초")

    print("\n각 테스트 케이스별 결과:")
    for test_name, result in results.items():
        if 'error' in result:
            print(f"  {test_name}: ❌ {result['error']}")
        else:
            status = "✅" if result.get('valid_json', False) else "❌"
            confidence = result.get('confidence_score', 0)
            print(f"  {test_name}: {status} (신뢰도: {confidence:.3f})")

def main():
    """메인 함수"""
    print("🔐 Source Code Agent 테스트 (Google API)")
    print("양자 취약 암호 알고리즘 탐지 테스트")
    print()

    # API 키 확인
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # config.yaml에서 API 키 로드
        try:
            config_loader = ConfigLoader('config/config.yaml')
            google_config = config_loader.get_llm_config('google')
            api_key = google_config.get('api_key')
            if api_key and api_key != "your_google_api_key_here":
                print("✅ config.yaml에서 Google API 키를 로드했습니다.")
            else:
                raise ValueError("API 키가 설정되지 않았습니다.")
        except Exception as e:
            print(f"❌ config.yaml에서 API 키를 로드할 수 없습니다: {e}")
            api_key = input("Google API 키를 직접 입력하세요: ").strip()
            if not api_key:
                print("API 키가 필요합니다. 종료합니다.")
                return

    # 실제 테스트 파일 로드
    test_samples = load_test_files_from_directory()

    print(f"📦 로드된 테스트 샘플: {len(test_samples)}개")
    for name in test_samples.keys():
        print(f"  - {name}")
    print()

    # 테스트 실행
    results = test_source_code_agent(api_key, test_samples)

    # 결과 요약
    print_summary(results)

    # 결과 저장
    save_test_results(results)

    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    main()