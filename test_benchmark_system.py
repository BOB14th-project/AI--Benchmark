#!/usr/bin/env python3
"""
벤치마크 시스템 테스트 스크립트
각 컴포넌트가 올바르게 작동하는지 확인합니다.
"""

import os
import json
from pathlib import Path
from config.config_loader import ConfigLoader
from clients.client_factory import ClientFactory
from clients.ollama_client import OllamaClient
from agents.agent_factory import AgentFactory
from benchmark_runner import BenchmarkRunner

def test_config_loader():
    """설정 로더 테스트"""
    print("🔧 설정 로더 테스트...")
    try:
        config_loader = ConfigLoader('config/config.yaml')

        # 각 프로바이더 설정 확인
        providers = ['google', 'openai', 'xai']
        for provider in providers:
            config = config_loader.get_llm_config(provider)
            if config.get('api_key') and config['api_key'] != f"your_{provider}_api_key_here":
                print(f"  ✅ {provider} 설정 완료")
            else:
                print(f"  ⚠️  {provider} API 키가 설정되지 않음")

        print("  ✅ 설정 로더 정상 작동")
        return True
    except Exception as e:
        print(f"  ❌ 설정 로더 오류: {e}")
        return False

def test_ollama_connection():
    """Ollama 연결 테스트"""
    print("\n🤖 Ollama 연결 테스트...")
    try:
        client = OllamaClient()

        if client.is_available():
            models = client.list_available_models()
            print(f"  ✅ Ollama 서버 연결됨")
            print(f"  📋 사용 가능한 모델: {models}")

            # 간단한 테스트
            if models:
                test_model = models[0]
                test_client = OllamaClient(model=test_model)
                response = test_client.make_request("Hello", max_tokens=10)
                print(f"  ✅ {test_model} 테스트 성공")
                return True
            else:
                print("  ⚠️  사용 가능한 모델이 없습니다.")
                return False
        else:
            print("  ❌ Ollama 서버에 연결할 수 없습니다.")
            print("  💡 ollama serve를 실행했는지 확인하세요.")
            return False
    except Exception as e:
        print(f"  ❌ Ollama 테스트 오류: {e}")
        return False

def test_agents():
    """에이전트 테스트"""
    print("\n🎯 에이전트 테스트...")
    try:
        agent_types = ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']

        for agent_type in agent_types:
            agent = AgentFactory.create_agent(agent_type)

            # 기본 기능 테스트
            analysis_points = agent.get_analysis_points()
            test_input = "test input"

            if len(analysis_points) > 0:
                print(f"  ✅ {agent_type}: {len(analysis_points)}개 분석 포인트")
            else:
                print(f"  ❌ {agent_type}: 분석 포인트가 없습니다.")

        print("  ✅ 모든 에이전트 정상 작동")
        return True
    except Exception as e:
        print(f"  ❌ 에이전트 테스트 오류: {e}")
        return False

def test_test_files():
    """테스트 파일 존재 확인"""
    print("\n📁 테스트 파일 확인...")

    base_dir = Path("data/test_files")
    agent_dirs = ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']

    total_files = 0
    for agent_dir in agent_dirs:
        dir_path = base_dir / agent_dir
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            file_count = len([f for f in files if f.is_file()])
            total_files += file_count
            print(f"  📂 {agent_dir}: {file_count}개 파일")
        else:
            print(f"  ❌ {agent_dir}: 디렉토리가 없습니다.")

    if total_files > 0:
        print(f"  ✅ 총 {total_files}개 테스트 파일 발견")
        return True
    else:
        print("  ❌ 테스트 파일이 없습니다.")
        return False

def test_single_benchmark():
    """단일 벤치마크 테스트"""
    print("\n🚀 단일 벤치마크 테스트...")

    try:
        runner = BenchmarkRunner()

        # 사용 가능한 모델 확인
        available_models = runner.get_available_models()

        # 첫 번째 사용 가능한 모델로 테스트
        test_provider = None
        test_model = None

        for provider, models in available_models.items():
            if models:
                test_provider = provider
                test_model = models[0]
                break

        if not test_provider:
            print("  ❌ 사용 가능한 모델이 없습니다.")
            return False

        print(f"  🎯 테스트 모델: {test_provider}/{test_model}")

        # 작은 범위로 테스트 실행
        results = runner.run_benchmark(
            providers=[test_provider],
            agents=['source_code'],  # 하나의 에이전트만
            test_limit=1,  # 파일 하나만
            parallel=False
        )

        if results and results.get('summary', {}).get('total_tests', 0) > 0:
            print("  ✅ 벤치마크 테스트 성공")

            # 간단한 결과 출력
            summary = results['summary']
            print(f"    총 테스트: {summary['total_tests']}")
            print(f"    성공: {summary['successful_tests']}")
            print(f"    성공률: {summary['success_rate']:.1%}")

            return True
        else:
            print("  ❌ 벤치마크 실행 결과가 없습니다.")
            return False

    except Exception as e:
        print(f"  ❌ 벤치마크 테스트 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 AI 벤치마크 시스템 테스트")
    print("=" * 60)

    tests = [
        ("설정 로더", test_config_loader),
        ("Ollama 연결", test_ollama_connection),
        ("에이전트", test_agents),
        ("테스트 파일", test_test_files),
        ("벤치마크 실행", test_single_benchmark)
    ]

    results = {}

    for test_name, test_func in tests:
        results[test_name] = test_func()

    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"  {test_name}: {status}")

    print(f"\n전체 결과: {passed}/{total} 테스트 통과 ({passed/total:.1%})")

    if passed == total:
        print("\n🎉 모든 테스트 통과! 시스템이 정상 작동합니다.")
        print("\n💡 다음 명령어로 전체 벤치마크를 실행할 수 있습니다:")
        print("   python benchmark_runner.py --limit 3")
    else:
        print("\n⚠️  일부 테스트가 실패했습니다. 설정을 확인해주세요.")

        if not results.get("설정 로더"):
            print("\n🔧 API 키 설정 방법:")
            print("   config/config.yaml 파일에서 API 키들을 설정하세요.")

        if not results.get("Ollama 연결"):
            print("\n🤖 Ollama 설정 방법:")
            print("   1. ollama serve")
            print("   2. ollama pull deepseek-r1:8b")
            print("   3. ollama pull gemma3:12b")

        if not results.get("테스트 파일"):
            print("\n📁 테스트 파일 확인:")
            print("   data/test_files/ 디렉토리에 테스트 파일들이 있는지 확인하세요.")

if __name__ == "__main__":
    main()