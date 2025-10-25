#!/usr/bin/env python3
"""
로컬 AI 서버 빠른 설정 스크립트

이 스크립트는 로컬 AI 서버를 벤치마크에 통합하는 과정을 자동화합니다.

사용법:
    python setup_local_ai.py

또는 대화형 모드:
    python setup_local_ai.py --interactive
"""

import os
import sys
import argparse


def setup_env_file():
    """
    .env 파일에 로컬 AI 서버 설정 추가
    """
    env_path = ".env"

    print("\n" + "=" * 70)
    print("📝 .env 파일 설정")
    print("=" * 70)

    # 현재 .env 파일 읽기
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()

    # 이미 LOCAL_AI 설정이 있는지 확인
    has_local_ai = any('LOCAL_AI' in line for line in env_lines)

    if has_local_ai:
        print("ℹ️  .env 파일에 이미 LOCAL_AI 설정이 있습니다.")
        response = input("덮어쓰시겠습니까? (y/N): ").strip().lower()
        if response != 'y':
            print("⏭️  .env 파일 설정을 건너뜁니다.")
            return

        # 기존 LOCAL_AI 설정 제거
        env_lines = [line for line in env_lines if 'LOCAL_AI' not in line]

    # 사용자 입력 받기
    print("\n로컬 AI 서버 정보를 입력하세요:")

    model_name = input("모델 이름 (예: llama3-rag, custom-model): ").strip()
    if not model_name:
        model_name = "custom-model"

    base_url = input("Base URL (예: http://localhost:8000/v1): ").strip()
    if not base_url:
        base_url = "http://localhost:8000/v1"

    api_key = input("API Key (필요없으면 Enter): ").strip()
    if not api_key:
        api_key = "not_required"

    # 새 설정 추가
    new_config = f"""
# Local AI Server Configuration
LOCAL_AI_API_KEY={api_key}
LOCAL_AI_MODEL={model_name}
LOCAL_AI_BASE_URL={base_url}
"""

    # .env 파일에 추가
    with open(env_path, 'a', encoding='utf-8') as f:
        f.write(new_config)

    print(f"\n✅ .env 파일에 설정이 추가되었습니다!")


def setup_config_yaml():
    """
    config/config.yaml 파일에 로컬 AI provider 추가
    """
    config_path = "config/config.yaml"

    print("\n" + "=" * 70)
    print("📝 config.yaml 파일 설정")
    print("=" * 70)

    if not os.path.exists(config_path):
        print(f"❌ {config_path} 파일을 찾을 수 없습니다.")
        return

    # config.yaml 읽기
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()

    # 이미 local_ai 설정이 있는지 확인
    if 'local_ai:' in config_content:
        print("ℹ️  config.yaml에 이미 local_ai 설정이 있습니다.")
        response = input("덮어쓰시겠습니까? (y/N): ").strip().lower()
        if response != 'y':
            print("⏭️  config.yaml 설정을 건너뜁니다.")
            return

    # local_ai 설정 추가
    local_ai_config = """
  local_ai:
    api_key_env: "LOCAL_AI_API_KEY"
    model_env: "LOCAL_AI_MODEL"
    base_url_env: "LOCAL_AI_BASE_URL"
"""

    # llm_providers 섹션 찾아서 추가
    if 'llm_providers:' in config_content:
        # ollama 설정 다음에 추가
        if '  ollama:' in config_content:
            # ollama 섹션의 끝 찾기
            lines = config_content.split('\n')
            insert_index = -1

            for i, line in enumerate(lines):
                if '  ollama:' in line:
                    # ollama 섹션의 끝 찾기 (다음 섹션이 시작되거나 빈 줄)
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith('    ') and not lines[j].startswith('  #'):
                            insert_index = j
                            break
                    break

            if insert_index > 0:
                lines.insert(insert_index, local_ai_config.rstrip())
                config_content = '\n'.join(lines)
            else:
                # 끝에 추가
                config_content += local_ai_config
        else:
            # llm_providers 섹션 끝에 추가
            config_content += local_ai_config
    else:
        print("⚠️  config.yaml에서 llm_providers 섹션을 찾을 수 없습니다.")
        return

    # config.yaml 파일 쓰기
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print(f"✅ config.yaml에 local_ai provider가 추가되었습니다!")


def setup_client_factory():
    """
    clients/client_factory.py에 LocalAIClient 등록
    """
    factory_path = "clients/client_factory.py"

    print("\n" + "=" * 70)
    print("📝 client_factory.py 설정")
    print("=" * 70)

    if not os.path.exists(factory_path):
        print(f"❌ {factory_path} 파일을 찾을 수 없습니다.")
        return

    # client_factory.py 읽기
    with open(factory_path, 'r', encoding='utf-8') as f:
        factory_content = f.read()

    # 이미 LocalAIClient가 등록되어 있는지 확인
    if 'LocalAIClient' in factory_content:
        print("✅ LocalAIClient가 이미 등록되어 있습니다.")
        return

    # import 문 추가
    if 'from .ollama_client import OllamaClient' in factory_content:
        factory_content = factory_content.replace(
            'from .ollama_client import OllamaClient',
            'from .ollama_client import OllamaClient\nfrom .local_ai_client import LocalAIClient'
        )
    else:
        # 다른 import 다음에 추가
        lines = factory_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from .') and 'Client' in line:
                lines.insert(i + 1, 'from .local_ai_client import LocalAIClient')
                break
        factory_content = '\n'.join(lines)

    # _clients dictionary에 추가
    if "'ollama': OllamaClient" in factory_content:
        factory_content = factory_content.replace(
            "'ollama': OllamaClient",
            "'ollama': OllamaClient,\n        'local_ai': LocalAIClient"
        )
    else:
        print("⚠️  _clients dictionary에서 적절한 위치를 찾을 수 없습니다.")
        print("   수동으로 'local_ai': LocalAIClient를 추가하세요.")
        return

    # client_factory.py 파일 쓰기
    with open(factory_path, 'w', encoding='utf-8') as f:
        f.write(factory_content)

    print(f"✅ client_factory.py에 LocalAIClient가 등록되었습니다!")


def verify_setup():
    """
    설정이 올바르게 되었는지 확인
    """
    print("\n" + "=" * 70)
    print("🔍 설정 확인")
    print("=" * 70)

    checks_passed = 0
    total_checks = 4

    # 1. .env 파일 확인
    print("\n1️⃣ .env 파일 확인...")
    if os.path.exists(".env"):
        with open(".env", 'r', encoding='utf-8') as f:
            env_content = f.read()
            if 'LOCAL_AI' in env_content:
                print("   ✅ LOCAL_AI 설정이 있습니다.")
                checks_passed += 1
            else:
                print("   ❌ LOCAL_AI 설정이 없습니다.")
    else:
        print("   ❌ .env 파일이 없습니다.")

    # 2. config.yaml 파일 확인
    print("\n2️⃣ config.yaml 파일 확인...")
    if os.path.exists("config/config.yaml"):
        with open("config/config.yaml", 'r', encoding='utf-8') as f:
            config_content = f.read()
            if 'local_ai:' in config_content:
                print("   ✅ local_ai provider 설정이 있습니다.")
                checks_passed += 1
            else:
                print("   ❌ local_ai provider 설정이 없습니다.")
    else:
        print("   ❌ config.yaml 파일이 없습니다.")

    # 3. local_ai_client.py 확인
    print("\n3️⃣ local_ai_client.py 파일 확인...")
    if os.path.exists("clients/local_ai_client.py"):
        print("   ✅ LocalAIClient 파일이 있습니다.")
        checks_passed += 1
    else:
        print("   ❌ LocalAIClient 파일이 없습니다.")

    # 4. client_factory.py 확인
    print("\n4️⃣ client_factory.py 등록 확인...")
    if os.path.exists("clients/client_factory.py"):
        with open("clients/client_factory.py", 'r', encoding='utf-8') as f:
            factory_content = f.read()
            if 'LocalAIClient' in factory_content and "'local_ai'" in factory_content:
                print("   ✅ LocalAIClient가 등록되어 있습니다.")
                checks_passed += 1
            else:
                print("   ❌ LocalAIClient가 등록되어 있지 않습니다.")
    else:
        print("   ❌ client_factory.py 파일이 없습니다.")

    # 결과
    print("\n" + "=" * 70)
    if checks_passed == total_checks:
        print(f"✅ 모든 설정이 완료되었습니다! ({checks_passed}/{total_checks})")
        return True
    else:
        print(f"⚠️  일부 설정이 누락되었습니다. ({checks_passed}/{total_checks})")
        return False


def main():
    parser = argparse.ArgumentParser(description="로컬 AI 서버 벤치마크 통합 설정")
    parser.add_argument('--interactive', '-i', action='store_true', help="대화형 모드")
    parser.add_argument('--skip-env', action='store_true', help=".env 설정 건너뛰기")
    parser.add_argument('--skip-config', action='store_true', help="config.yaml 설정 건너뛰기")
    parser.add_argument('--skip-factory', action='store_true', help="client_factory 설정 건너뛰기")
    parser.add_argument('--verify-only', action='store_true', help="설정 확인만 수행")

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 로컬 AI 서버 벤치마크 통합 설정")
    print("=" * 70)

    # 확인만 수행
    if args.verify_only:
        verify_setup()
        return

    # .env 파일 설정
    if not args.skip_env:
        setup_env_file()

    # config.yaml 설정
    if not args.skip_config:
        setup_config_yaml()

    # client_factory 설정
    if not args.skip_factory:
        setup_client_factory()

    # 최종 확인
    print("\n" + "=" * 70)
    print("📋 설정 완료!")
    print("=" * 70)

    all_ok = verify_setup()

    if all_ok:
        print("\n다음 단계:")
        print("  1. 로컬 AI 서버가 실행 중인지 확인")
        print("  2. 연결 테스트 실행:")
        print("     python test_local_connection.py")
        print("  3. 벤치마크 실행:")
        print("     python test_model.py --provider local_ai")
    else:
        print("\n설정을 완료하려면:")
        print("  - 누락된 설정을 수동으로 추가하거나")
        print("  - 이 스크립트를 다시 실행하세요")


if __name__ == "__main__":
    main()
