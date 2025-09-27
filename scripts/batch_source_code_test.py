#!/usr/bin/env python3
"""
Source Code Agent 테스트 스크립트 (실제 파일들, gemini-2.0-flash-exp)
data/test_files/source_code의 모든 파일들을 테스트
"""

import os
import json
import time
from typing import Dict, Any
from pathlib import Path
from agents.agent_factory import AgentFactory
from clients.google_client import GoogleClient
from config.config_loader import ConfigLoader

def load_test_files_batch(batch_size: int = 5) -> list:
    """테스트 파일들을 배치 단위로 로드"""
    source_code_dir = Path("data/test_files/source_code")

    if not source_code_dir.exists():
        print(f"❌ 테스트 파일 디렉토리가 없습니다: {source_code_dir}")
        return []

    supported_extensions = {'.py', '.java', '.c', '.cpp'}
    all_files = []

    for file_path in source_code_dir.iterdir():
        if file_path.is_file() and file_path.suffix in supported_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        all_files.append({
                            'name': file_path.stem,
                            'content': content,
                            'path': str(file_path)
                        })
            except Exception as e:
                print(f"❌ 파일 로드 실패: {file_path.name} - {e}")

    # 배치로 나누기
    batches = []
    for i in range(0, len(all_files), batch_size):
        batches.append(all_files[i:i + batch_size])

    return batches

def test_file_batch(api_key: str, file_batch: list, batch_num: int):
    """파일 배치 테스트"""
    print(f"\n🔍 배치 {batch_num} 테스트 시작 ({len(file_batch)}개 파일)")
    print("=" * 50)

    # Google 클라이언트 초기화
    try:
        google_client = GoogleClient(api_key=api_key, model="models/gemini-2.0-flash-exp")
        test_response = google_client.make_request("Test", max_tokens=5)
        print(f"✅ 모델 작동 확인: gemini-2.0-flash-exp")
    except Exception as e:
        print(f"❌ 모델 초기화 실패: {str(e)}")
        return {}

    # Source Code Agent 생성
    agent = AgentFactory.create_agent('source_code')
    results = {}

    for i, file_info in enumerate(file_batch, 1):
        file_name = file_info['name']
        file_content = file_info['content']

        print(f"\n📄 {i}/{len(file_batch)}: {file_name}")
        print("-" * 30)

        try:
            # 입력 검증
            if not agent.validate_input(file_content):
                print(f"❌ 입력 검증 실패")
                results[file_name] = {'error': 'Input validation failed'}
                continue

            # 프롬프트 생성 (내용 길이 제한)
            if len(file_content) > 5000:
                file_content = file_content[:5000] + "\n... (내용이 길어 일부만 분석)"
                print(f"📏 파일 내용이 길어 5000자로 제한")

            prompt = agent.create_prompt(file_content)
            print(f"📝 프롬프트 길이: {len(prompt)} 문자")

            # API 호출 (타임아웃 추가)
            start_time = time.time()
            response = google_client.make_request(prompt, max_tokens=1500)
            end_time = time.time()

            print(f"⏱️  응답 시간: {end_time - start_time:.2f}초")
            print(f"📊 토큰 사용량: {response.get('usage', {})}")

            # 결과 파싱
            findings = agent.extract_key_findings(response['content'])

            if findings['valid_json']:
                print(f"✅ JSON 파싱 성공")
                print(f"🎯 신뢰도 점수: {findings['confidence_score']}")
                print(f"📄 요약: {findings['summary'][:100]}...")

                # 탐지된 취약점 수 계산
                detected_vulnerabilities = len([
                    k for k, v in findings['analysis_results'].items()
                    if v and v.lower() not in ['none', 'not detected', 'no', '', 'not present', 'no implementations']
                ])
                print(f"🔍 탐지된 취약점 수: {detected_vulnerabilities}")
            else:
                print(f"❌ JSON 파싱 실패")

            results[file_name] = {
                'valid_json': findings['valid_json'],
                'confidence_score': findings['confidence_score'],
                'summary': findings['summary'],
                'detected_vulnerabilities': detected_vulnerabilities if findings['valid_json'] else 0,
                'response_time': end_time - start_time,
                'token_usage': response.get('usage', {}),
                'file_path': file_info['path']
            }

        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            results[file_name] = {'error': str(e), 'file_path': file_info['path']}

        # 배치 간 딜레이 (API 제한 방지)
        if i < len(file_batch):
            time.sleep(1)

    return results

def main():
    """메인 함수"""
    print("🔐 Source Code Agent 실제 파일 테스트")
    print("모델: gemini-2.0-flash-exp")
    print("=" * 60)

    # API 키 로드
    try:
        config_loader = ConfigLoader('config/config.yaml')
        google_config = config_loader.get_llm_config('google')
        api_key = google_config.get('api_key')

        if not api_key or api_key == "your_google_api_key_here":
            print("❌ API 키가 설정되지 않았습니다.")
            return

        print("✅ API 키 로드 완료")
    except Exception as e:
        print(f"❌ API 키 로드 실패: {e}")
        return

    # 테스트 파일들을 배치로 로드
    file_batches = load_test_files_batch(batch_size=3)  # 한 번에 3개씩

    if not file_batches:
        print("❌ 테스트할 파일이 없습니다.")
        return

    total_files = sum(len(batch) for batch in file_batches)
    print(f"📦 총 {total_files}개 파일을 {len(file_batches)}개 배치로 나누어 테스트")

    all_results = {}

    # 배치별 테스트 실행
    for batch_num, file_batch in enumerate(file_batches, 1):
        try:
            batch_results = test_file_batch(api_key, file_batch, batch_num)
            all_results.update(batch_results)

            print(f"\n✅ 배치 {batch_num}/{len(file_batches)} 완료")

            # 배치 간 휴식 (API 제한 방지)
            if batch_num < len(file_batches):
                print("⏳ 배치 간 휴식 (3초)...")
                time.sleep(3)

        except Exception as e:
            print(f"❌ 배치 {batch_num} 실행 중 오류: {e}")

    # 최종 결과 요약
    print_final_summary(all_results)

    # 결과 저장
    save_results(all_results)

def print_final_summary(results: Dict[str, Any]):
    """최종 결과 요약"""
    print("\n" + "=" * 60)
    print("📊 최종 테스트 결과 요약")
    print("=" * 60)

    total_tests = len(results)
    successful_tests = len([r for r in results.values() if 'error' not in r and r.get('valid_json', False)])
    failed_tests = total_tests - successful_tests

    print(f"전체 테스트: {total_tests}")
    print(f"성공: {successful_tests} ✅")
    print(f"실패: {failed_tests} ❌")
    print(f"성공률: {(successful_tests/total_tests)*100:.1f}%")

    if successful_tests > 0:
        # 평균 통계
        avg_confidence = sum(r.get('confidence_score', 0) for r in results.values() if 'error' not in r) / successful_tests
        avg_response_time = sum(r.get('response_time', 0) for r in results.values() if 'error' not in r) / successful_tests
        total_vulnerabilities = sum(r.get('detected_vulnerabilities', 0) for r in results.values() if 'error' not in r)

        print(f"\n📈 평균 통계:")
        print(f"  신뢰도 점수: {avg_confidence:.3f}")
        print(f"  응답 시간: {avg_response_time:.2f}초")
        print(f"  총 탐지된 취약점: {total_vulnerabilities}개")

    # 상위 결과
    print(f"\n🏆 상위 탐지 결과:")
    success_results = [(k, v) for k, v in results.items() if 'error' not in v and v.get('valid_json', False)]
    success_results.sort(key=lambda x: x[1].get('detected_vulnerabilities', 0), reverse=True)

    for i, (filename, result) in enumerate(success_results[:5], 1):
        vuln_count = result.get('detected_vulnerabilities', 0)
        confidence = result.get('confidence_score', 0)
        print(f"  {i}. {filename}: {vuln_count}개 취약점 (신뢰도: {confidence:.3f})")

def save_results(results: Dict[str, Any]):
    """결과 저장"""
    filename = f"source_code_files_test_results_{int(time.time())}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 테스트 결과가 {filename}에 저장되었습니다.")

if __name__ == "__main__":
    main()