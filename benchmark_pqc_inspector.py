#!/usr/bin/env python3
"""
PQC Inspector AI-Server 벤치마크 스크립트

AI-Server의 RAG 강화 에이전트들과 llama3:8b를 비교 평가합니다.
"""

import os
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from clients.pqc_inspector_client import PQCInspectorClient
from clients.ollama_client import OllamaClient
from agents.agent_factory import AgentFactory
from utils.test_case_manager import TestCaseManager
from utils.metrics_calculator import MetricsCalculator


class PQCInspectorBenchmark:
    def __init__(self, pqc_base_url: str = "http://localhost:8000",
                 ollama_base_url: str = "http://localhost:11434"):
        self.pqc_base_url = pqc_base_url
        self.ollama_base_url = ollama_base_url

        # 테스트 케이스 매니저
        self.test_manager = TestCaseManager(
            test_cases_dir="data/test_cases",
            ground_truth_dir="data/ground_truth",
            test_files_dir="data/test_files"
        )

        # 메트릭 계산기
        self.metrics_calculator = MetricsCalculator()

        # 결과 저장
        self.results = []

    def check_servers(self) -> bool:
        """서버 상태 확인"""
        print("=" * 80)
        print("🔍 서버 상태 확인")
        print("=" * 80)

        # PQC Inspector 확인
        try:
            pqc_client = PQCInspectorClient(base_url=self.pqc_base_url)
            if pqc_client.is_available():
                print(f"✅ PQC Inspector 서버 실행 중: {self.pqc_base_url}")
                agents = pqc_client.list_available_models()
                print(f"   사용 가능한 에이전트: {agents}")
            else:
                print(f"❌ PQC Inspector 서버 접속 불가: {self.pqc_base_url}")
                print("   AI-Server를 먼저 실행해주세요: cd AI-Server && python main.py")
                return False
        except Exception as e:
            print(f"❌ PQC Inspector 확인 실패: {e}")
            return False

        # Ollama 확인
        try:
            ollama_client = OllamaClient(base_url=self.ollama_base_url)
            available_models = ollama_client.list_available_models()
            if 'llama3:8b' in available_models:
                print(f"✅ Ollama 서버 실행 중: {self.ollama_base_url}")
                print(f"   llama3:8b 모델 사용 가능")
            else:
                print(f"⚠️  llama3:8b 모델이 없습니다.")
                print(f"   사용 가능한 모델: {available_models}")
                print(f"   설치 명령: ollama pull llama3:8b")
                return False
        except Exception as e:
            print(f"❌ Ollama 확인 실패: {e}")
            return False

        print("=" * 80)
        return True

    def run_benchmark(self, limit_per_agent: int = None, agent_filter: List[str] = None):
        """벤치마크 실행"""
        if not self.check_servers():
            print("\n❌ 서버 확인 실패. 벤치마크를 종료합니다.")
            return

        print("\n" + "=" * 80)
        print("🚀 PQC Inspector vs llama3:8b 벤치마크 시작")
        print("=" * 80)

        # 에이전트 타입 매핑
        agent_types = {
            'source_code': 'source_code',
            'assembly_binary': 'assembly_binary',
            'logs_config': 'logs_config'
        }

        # 필터 적용
        if agent_filter:
            agent_types = {k: v for k, v in agent_types.items() if k in agent_filter}

        total_tests = 0
        for agent_type in agent_types.keys():
            # 테스트 케이스 로드
            test_cases = self.test_manager.load_test_cases(agent_type)
            if limit_per_agent:
                test_cases = test_cases[:limit_per_agent]

            print(f"\n📁 {agent_type}: {len(test_cases)}개 테스트 파일")
            total_tests += len(test_cases) * 2  # PQC Inspector + llama3:8b

            for idx, test_case in enumerate(test_cases, 1):
                print(f"\n--- 테스트 {idx}/{len(test_cases)}: {test_case['file_name']} ---")

                # 1. PQC Inspector 에이전트 테스트
                pqc_result = self.test_pqc_inspector(agent_type, test_case)
                if pqc_result:
                    self.results.append(pqc_result)
                    print(f"✅ PQC Inspector ({agent_type}): "
                          f"F1={pqc_result.get('f1_score', 0):.3f}, "
                          f"시간={pqc_result.get('response_time', 0):.2f}초")

                # 2. llama3:8b 테스트
                llama_result = self.test_llama3(agent_type, test_case)
                if llama_result:
                    self.results.append(llama_result)
                    print(f"✅ llama3:8b ({agent_type}): "
                          f"F1={llama_result.get('f1_score', 0):.3f}, "
                          f"시간={llama_result.get('response_time', 0):.2f}초")

        print("\n" + "=" * 80)
        print(f"📊 벤치마크 완료: 총 {len(self.results)}/{total_tests} 테스트")
        print("=" * 80)

    def test_pqc_inspector(self, agent_type: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """PQC Inspector 에이전트 테스트"""
        try:
            # 클라이언트 생성 (에이전트 타입을 model로 지정)
            client = PQCInspectorClient(
                model=agent_type,  # source_code, assembly_binary, logs_config
                base_url=self.pqc_base_url
            )

            # 파일 경로 생성
            file_path = test_case.get('file_path', '')
            if not Path(file_path).exists():
                print(f"⚠️  파일 없음: {file_path}")
                return None

            # 파일 업로드 및 분석
            prompt = f"FILE_PATH:{file_path}"
            result = client.benchmark_request(prompt)

            if not result.get('success'):
                print(f"❌ PQC Inspector 실패: {result.get('error')}")
                return None

            # 응답 파싱
            response_content = result.get('content', '{}')
            try:
                analysis_result = json.loads(response_content)
            except json.JSONDecodeError:
                print(f"⚠️  JSON 파싱 실패")
                analysis_result = {}

            # 메트릭 계산
            ground_truth = test_case.get('ground_truth', {})
            metrics = self.metrics_calculator.calculate_metrics(
                analysis_result,
                ground_truth
            )

            return {
                'provider': 'pqc_inspector',
                'model': agent_type,
                'agent_type': agent_type,
                'test_id': test_case.get('test_id'),
                'file_name': test_case.get('file_name'),
                'response_time': result.get('response_time', 0),
                'json_valid': result.get('json_valid', False),
                **metrics,
                'raw_response': analysis_result
            }

        except Exception as e:
            print(f"❌ PQC Inspector 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def test_llama3(self, agent_type: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """llama3:8b 테스트"""
        try:
            # Ollama 클라이언트 생성
            client = OllamaClient(
                model='llama3:8b',
                base_url=self.ollama_base_url
            )

            # 에이전트 생성 (프롬프트 템플릿용)
            agent = AgentFactory.create_agent(agent_type)

            # 입력 데이터 준비
            input_data = test_case.get('input_data', '')
            if len(input_data) > 4000:
                input_data = input_data[:4000] + "\n... (truncated)"

            # 프롬프트 생성
            prompt = agent.create_prompt(input_data)

            # API 호출
            result = client.benchmark_request(prompt)

            if not result.get('success'):
                print(f"❌ llama3:8b 실패: {result.get('error')}")
                return None

            # 응답 파싱
            response_content = result.get('content', '')
            try:
                # JSON 추출 시도
                if '{' in response_content and '}' in response_content:
                    json_start = response_content.find('{')
                    json_end = response_content.rfind('}') + 1
                    json_text = response_content[json_start:json_end]
                    analysis_result = json.loads(json_text)
                else:
                    analysis_result = {}
            except json.JSONDecodeError:
                print(f"⚠️  JSON 파싱 실패")
                analysis_result = {}

            # 메트릭 계산
            ground_truth = test_case.get('ground_truth', {})
            metrics = self.metrics_calculator.calculate_metrics(
                analysis_result,
                ground_truth
            )

            return {
                'provider': 'ollama',
                'model': 'llama3:8b',
                'agent_type': agent_type,
                'test_id': test_case.get('test_id'),
                'file_name': test_case.get('file_name'),
                'response_time': result.get('response_time', 0),
                'json_valid': result.get('json_valid', False),
                **metrics,
                'raw_response': analysis_result
            }

        except Exception as e:
            print(f"❌ llama3:8b 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_results(self, output_file: str = None):
        """결과 저장"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"pqc_inspector_vs_llama3_results_{timestamp}.json"

        output_path = Path("results") / output_file
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'benchmark_info': {
                    'timestamp': datetime.now().isoformat(),
                    'pqc_base_url': self.pqc_base_url,
                    'ollama_base_url': self.ollama_base_url,
                    'total_tests': len(self.results)
                },
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 결과 저장됨: {output_path}")
        return output_path

    def print_summary(self):
        """결과 요약 출력"""
        if not self.results:
            print("\n⚠️  결과 없음")
            return

        print("\n" + "=" * 80)
        print("📊 벤치마크 결과 요약")
        print("=" * 80)

        # 프로바이더별 집계
        pqc_results = [r for r in self.results if r['provider'] == 'pqc_inspector']
        llama_results = [r for r in self.results if r['provider'] == 'ollama']

        def calc_avg(results, key):
            vals = [r.get(key, 0) for r in results if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0

        print("\n🤖 PQC Inspector (RAG 강화 에이전트)")
        print(f"   테스트 수: {len(pqc_results)}")
        print(f"   평균 F1 Score: {calc_avg(pqc_results, 'f1_score'):.3f}")
        print(f"   평균 Precision: {calc_avg(pqc_results, 'precision'):.3f}")
        print(f"   평균 Recall: {calc_avg(pqc_results, 'recall'):.3f}")
        print(f"   평균 응답시간: {calc_avg(pqc_results, 'response_time'):.2f}초")

        print("\n🦙 llama3:8b (Ollama)")
        print(f"   테스트 수: {len(llama_results)}")
        print(f"   평균 F1 Score: {calc_avg(llama_results, 'f1_score'):.3f}")
        print(f"   평균 Precision: {calc_avg(llama_results, 'precision'):.3f}")
        print(f"   평균 Recall: {calc_avg(llama_results, 'recall'):.3f}")
        print(f"   평균 응답시간: {calc_avg(llama_results, 'response_time'):.2f}초")

        # 에이전트별 집계
        print("\n📋 에이전트별 성능 비교")
        agent_types = set(r['agent_type'] for r in self.results)
        for agent_type in sorted(agent_types):
            pqc_agent = [r for r in pqc_results if r['agent_type'] == agent_type]
            llama_agent = [r for r in llama_results if r['agent_type'] == agent_type]

            print(f"\n  {agent_type}:")
            print(f"    PQC Inspector: F1={calc_avg(pqc_agent, 'f1_score'):.3f}, "
                  f"시간={calc_avg(pqc_agent, 'response_time'):.2f}초")
            print(f"    llama3:8b:     F1={calc_avg(llama_agent, 'f1_score'):.3f}, "
                  f"시간={calc_avg(llama_agent, 'response_time'):.2f}초")

        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="PQC Inspector vs llama3:8b 벤치마크"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='에이전트당 테스트 파일 수 제한 (예: 3)'
    )
    parser.add_argument(
        '--agents',
        nargs='+',
        choices=['source_code', 'assembly_binary', 'logs_config'],
        default=None,
        help='테스트할 에이전트 선택'
    )
    parser.add_argument(
        '--pqc-url',
        default='http://localhost:8000',
        help='PQC Inspector 서버 URL'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama 서버 URL'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='결과 파일 이름'
    )

    args = parser.parse_args()

    # 벤치마크 실행
    benchmark = PQCInspectorBenchmark(
        pqc_base_url=args.pqc_url,
        ollama_base_url=args.ollama_url
    )

    benchmark.run_benchmark(
        limit_per_agent=args.limit,
        agent_filter=args.agents
    )

    # 결과 출력 및 저장
    benchmark.print_summary()
    benchmark.save_results(args.output)


if __name__ == "__main__":
    main()
