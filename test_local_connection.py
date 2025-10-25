#!/usr/bin/env python3
"""
로컬 AI 서버 연결 테스트 스크립트

사용법:
    python test_local_connection.py

환경 변수 (.env):
    LOCAL_AI_API_KEY=not_required
    LOCAL_AI_MODEL=your-model-name
    LOCAL_AI_BASE_URL=http://localhost:8000/v1
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.local_ai_client import LocalAIClient
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_local_ai_connection():
    """로컬 AI 서버 연결 및 기본 기능 테스트"""

    print("=" * 70)
    print("🧪 로컬 AI 서버 연결 테스트")
    print("=" * 70)

    # 환경 변수에서 설정 로드
    api_key = os.getenv("LOCAL_AI_API_KEY", "not_required")
    model = os.getenv("LOCAL_AI_MODEL")
    base_url = os.getenv("LOCAL_AI_BASE_URL")

    if not model or not base_url:
        print("❌ 환경 변수가 설정되지 않았습니다!")
        print("\n.env 파일에 다음 설정을 추가하세요:")
        print("  LOCAL_AI_API_KEY=not_required")
        print("  LOCAL_AI_MODEL=your-model-name")
        print("  LOCAL_AI_BASE_URL=http://localhost:8000/v1")
        return False

    print(f"\n📋 설정 정보:")
    print(f"  - Model: {model}")
    print(f"  - Base URL: {base_url}")
    print(f"  - API Key: {'***' if api_key != 'not_required' else 'not_required'}")

    # 클라이언트 생성
    try:
        client = LocalAIClient(
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        print(f"  - API Type: {client.api_type}")
    except Exception as e:
        print(f"❌ 클라이언트 생성 실패: {e}")
        return False

    # 1. 서버 연결 테스트
    print("\n" + "=" * 70)
    print("1️⃣ 서버 가용성 테스트")
    print("=" * 70)

    try:
        is_available = client.is_available()
        if is_available:
            print("✅ 서버가 실행 중입니다!")
        else:
            print("❌ 서버에 연결할 수 없습니다.")
            print("\n다음을 확인하세요:")
            print("  1. 로컬 AI 서버가 실행 중인가?")
            print("  2. BASE_URL이 올바른가?")
            print("  3. 방화벽이 포트를 차단하고 있지 않은가?")
            return False
    except Exception as e:
        print(f"❌ 가용성 테스트 실패: {e}")
        return False

    # 2. 모델 목록 조회
    print("\n" + "=" * 70)
    print("2️⃣ 사용 가능한 모델 조회")
    print("=" * 70)

    try:
        models = client.list_available_models()
        if models:
            print(f"✅ 사용 가능한 모델: {len(models)}개")
            for i, m in enumerate(models, 1):
                marker = "👉" if m == model else "  "
                print(f"  {marker} {i}. {m}")

            if model not in models:
                print(f"\n⚠️  경고: 설정된 모델 '{model}'이(가) 목록에 없습니다!")
        else:
            print(f"ℹ️  모델 목록을 가져올 수 없습니다. (커스텀 API일 수 있음)")
    except Exception as e:
        print(f"⚠️  모델 목록 조회 실패: {e}")

    # 3. 간단한 요청 테스트
    print("\n" + "=" * 70)
    print("3️⃣ 간단한 생성 요청 테스트")
    print("=" * 70)

    test_prompt = "Hello! Please respond with 'Connection successful!'"
    print(f"📤 Prompt: {test_prompt}")

    try:
        response = client.make_request(
            prompt=test_prompt,
            max_tokens=100
        )

        print(f"\n✅ 요청 성공!")
        print(f"📥 Response: {response['content'][:200]}")
        if len(response['content']) > 200:
            print(f"           ... (총 {len(response['content'])} 글자)")
        print(f"🔢 Tokens: {response['usage']['total_tokens']}")

    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return False

    # 4. 암호화 알고리즘 탐지 테스트 (실제 벤치마크 시나리오)
    print("\n" + "=" * 70)
    print("4️⃣ 암호화 알고리즘 탐지 테스트")
    print("=" * 70)

    crypto_test_prompt = """Analyze the following code and identify any cryptographic algorithms:

```python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Serialize private key
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
```

Please respond in JSON format with:
{
  "algorithms_found": ["algorithm1", "algorithm2"],
  "quantum_vulnerable": true/false,
  "explanation": "brief explanation"
}
"""

    print("📤 Testing crypto detection capability...")

    try:
        response = client.make_request(
            prompt=crypto_test_prompt,
            max_tokens=500
        )

        print(f"\n✅ 응답 받음!")
        print(f"📥 Response preview:")
        print("-" * 70)
        print(response['content'][:500])
        if len(response['content']) > 500:
            print("... (truncated)")
        print("-" * 70)
        print(f"\n🔢 Token usage:")
        print(f"  - Prompt: {response['usage']['prompt_tokens']}")
        print(f"  - Completion: {response['usage']['completion_tokens']}")
        print(f"  - Total: {response['usage']['total_tokens']}")

        # JSON 유효성 검사
        try:
            import json
            content = response['content'].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

            parsed = json.loads(content)
            print(f"\n✅ JSON 파싱 성공!")
            print(f"  - Algorithms found: {parsed.get('algorithms_found', [])}")
            print(f"  - Quantum vulnerable: {parsed.get('quantum_vulnerable', 'N/A')}")

        except json.JSONDecodeError:
            print(f"\n⚠️  응답이 유효한 JSON이 아닙니다.")
            print(f"   벤치마크에서는 JSON 응답이 필요합니다.")

    except Exception as e:
        print(f"❌ 암호화 탐지 테스트 실패: {e}")
        return False

    # 최종 요약
    print("\n" + "=" * 70)
    print("✅ 모든 테스트 완료!")
    print("=" * 70)
    print("\n다음 단계:")
    print("  1. config/config.yaml에 local_ai provider 추가")
    print("  2. clients/client_factory.py에 LocalAIClient 등록")
    print("  3. 벤치마크 실행:")
    print("     python test_model.py --provider local_ai")
    print("     python run_benchmark.py")

    return True


if __name__ == "__main__":
    try:
        success = test_local_ai_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
