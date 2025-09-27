#!/usr/bin/env python3
"""
Google Generative AI의 사용 가능한 모델을 확인하는 스크립트
"""

import google.generativeai as genai
import os
from config.config_loader import ConfigLoader

def list_available_models():
    """사용 가능한 Google Generative AI 모델들을 확인"""

    # API 키 로드
    try:
        config_loader = ConfigLoader('config/config.yaml')
        google_config = config_loader.get_llm_config('google')
        api_key = google_config.get('api_key')

        if not api_key or api_key == "your_google_api_key_here":
            print("❌ API 키가 설정되지 않았습니다.")
            return

        print("✅ API 키를 로드했습니다.")

    except Exception as e:
        print(f"❌ API 키 로드 실패: {e}")
        return

    # Google AI 설정
    genai.configure(api_key=api_key)

    print("\n🔍 사용 가능한 Google Generative AI 모델들:")
    print("=" * 60)

    try:
        models = genai.list_models()

        for model in models:
            print(f"📋 모델명: {model.name}")
            print(f"   - 지원 메서드: {', '.join(model.supported_generation_methods)}")
            print(f"   - 설명: {model.display_name}")
            print()

        # 간단한 테스트를 위한 추천 모델들
        print("\n💡 테스트 권장 모델들:")
        basic_models = [
            "models/gemini-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro"
        ]

        for model_name in basic_models:
            try:
                # 간단한 요청으로 모델 테스트
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, this is a test.")
                print(f"✅ {model_name}: 작동 중")
            except Exception as e:
                print(f"❌ {model_name}: {str(e)[:100]}...")

    except Exception as e:
        print(f"❌ 모델 목록 조회 실패: {e}")

        # 기본 모델들로 개별 테스트
        print("\n🔧 기본 모델들로 개별 테스트:")
        test_models = [
            "gemini-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "models/gemini-pro",
            "models/gemini-1.5-flash"
        ]

        for model_name in test_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Test")
                print(f"✅ {model_name}: 작동 중")
                break  # 첫 번째 작동하는 모델 찾으면 종료
            except Exception as e:
                print(f"❌ {model_name}: {str(e)[:80]}...")

if __name__ == "__main__":
    list_available_models()