#!/usr/bin/env python3
"""
통합 벤치마크 실행 시스템
모든 모델과 에이전트를 대상으로 성능을 평가합니다.
"""

import os
import json
import time
import argparse
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from config.config_loader import ConfigLoader
from clients.client_factory import ClientFactory
from clients.ollama_client import OllamaClient
from agents.agent_factory import AgentFactory
from utils.test_case_manager import TestCaseManager

class BenchmarkRunner:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_loader = ConfigLoader(config_path)
        self.test_manager = TestCaseManager(
            test_cases_dir="data/test_cases",
            ground_truth_dir="data/ground_truth",
            test_files_dir="data/test_files"
        )
        self.results = {}
        self.lock = threading.Lock()

    def get_available_models(self) -> Dict[str, List[str]]:
        """사용 가능한 모델들을 조회"""
        models = {
            'google': ['gemini-2.0-flash-exp'],
            'openai': ['gpt-4.1'],
            'xai': ['grok-3-mini'],
            'ollama': ['llama3:8b', 'gemma3:12b', 'codellama:7b']
        }

        # Ollama 모델 가용성 확인
        try:
            ollama_client = OllamaClient()
            if ollama_client.is_available():
                available_ollama = ollama_client.list_available_models()
                models['ollama'] = [m for m in models['ollama'] if m in available_ollama]
                print(f"✅ Ollama 사용 가능한 모델: {models['ollama']}")
            else:
                models['ollama'] = []
                print("❌ Ollama 서버가 실행되지 않거나 모델이 없습니다.")
        except Exception as e:
            models['ollama'] = []
            print(f"❌ Ollama 확인 실패: {e}")

        return models

    def load_test_files(self, agent_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """특정 에이전트 타입의 테스트 파일들을 로드"""
        test_cases = self.test_manager.load_test_cases(agent_type)

        if limit:
            test_cases = test_cases[:limit]

        print(f"📁 {agent_type}: {len(test_cases)}개 테스트 파일 로드됨")
        return test_cases

    def run_single_test(self, provider: str, model: str, agent_type: str,
                       test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 테스트 실행"""
        try:
            # 클라이언트 생성
            if provider == 'ollama':
                client = ClientFactory.create_client(provider, {
                    'api_key': 'not_required',
                    'model': model,
                    'base_url': 'http://localhost:11434'
                })
            else:
                llm_config = self.config_loader.get_llm_config(provider)
                llm_config['model'] = model
                client = ClientFactory.create_client(provider, llm_config)

            # 에이전트 생성
            agent = AgentFactory.create_agent(agent_type)

            # 입력 데이터 준비
            input_data = test_case.get('input_data', '')
            if not input_data:
                return {
                    'error': 'No input data',
                    'test_id': test_case.get('test_id', 'unknown')
                }

            # 컨텍스트 길이 제한 (모델별로 다르게 설정 가능)
            max_length = 4000 if provider == 'ollama' else 6000
            if len(input_data) > max_length:
                input_data = input_data[:max_length] + "\n... (truncated for length)"

            # 입력 검증
            if not agent.validate_input(input_data):
                return {
                    'error': 'Input validation failed',
                    'test_id': test_case.get('test_id', 'unknown')
                }

            # 프롬프트 생성
            prompt = agent.create_prompt(input_data)

            # API 호출
            max_tokens = 1500 if provider == 'ollama' else 2000
            response = client.benchmark_request(prompt, max_tokens)

            if not response['success']:
                return {
                    'error': response['error'],
                    'test_id': test_case.get('test_id', 'unknown'),
                    'response_time': response['response_time']
                }

            # 결과 파싱
            findings = agent.extract_key_findings(response['content'])

            # 취약점 수 계산
            detected_vulnerabilities = 0
            if findings['valid_json']:
                detected_vulnerabilities = len([
                    k for k, v in findings['analysis_results'].items()
                    if v and v.lower() not in ['none', 'not detected', 'no', '', 'not present', 'no implementations']
                ])

            return {
                'test_id': test_case.get('test_id', 'unknown'),
                'provider': provider,
                'model': model,
                'agent_type': agent_type,
                'success': True,
                'valid_json': findings['valid_json'],
                'confidence_score': findings['confidence_score'],
                'detected_vulnerabilities': detected_vulnerabilities,
                'response_time': response['response_time'],
                'json_valid': response['json_valid'],
                'summary': findings['summary'],
                'analysis_results': findings['analysis_results'],
                'usage': response.get('usage', {}),
                'file_path': test_case.get('file_path', ''),
                'timestamp': time.time()
            }

        except Exception as e:
            return {
                'test_id': test_case.get('test_id', 'unknown'),
                'provider': provider,
                'model': model,
                'agent_type': agent_type,
                'success': False,
                'error': str(e),
                'response_time': 0,
                'timestamp': time.time()
            }

    def run_benchmark(self, providers: List[str] = None, agents: List[str] = None,
                     test_limit: Optional[int] = None, parallel: bool = False) -> Dict[str, Any]:
        """전체 벤치마크 실행"""
        print("🚀 벤치마크 시작")
        print("=" * 60)

        # 기본값 설정
        if providers is None:
            providers = ['google', 'openai', 'xai', 'ollama']
        if agents is None:
            agents = ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']

        available_models = self.get_available_models()

        # 에이전트별로 테스트 파일을 한 번만 로드
        agent_test_files = {}
        for agent_type in agents:
            agent_test_files[agent_type] = self.load_test_files(agent_type, test_limit)

        # 실행할 테스트 조합 생성
        test_combinations = []
        for provider in providers:
            if provider not in available_models or not available_models[provider]:
                print(f"⚠️  {provider} 모델이 사용 불가능합니다.")
                continue

            for model in available_models[provider]:
                for agent_type in agents:
                    test_cases = agent_test_files[agent_type]
                    if test_cases:
                        for test_case in test_cases:
                            test_combinations.append((provider, model, agent_type, test_case))

        print(f"📊 총 {len(test_combinations)}개 테스트 조합")

        # 병렬 또는 순차 실행
        if parallel and len(test_combinations) > 1:
            results = self._run_parallel_tests(test_combinations)
        else:
            results = self._run_sequential_tests(test_combinations)

        # 결과 정리
        self.results = {
            'summary': self._generate_summary(results),
            'detailed_results': results,
            'metadata': {
                'total_tests': len(test_combinations),
                'timestamp': time.time(),
                'providers': providers,
                'agents': agents,
                'test_limit': test_limit
            }
        }

        return self.results

    def _run_sequential_tests(self, test_combinations: List) -> List[Dict[str, Any]]:
        """순차 테스트 실행"""
        results = []

        for i, (provider, model, agent_type, test_case) in enumerate(test_combinations, 1):
            print(f"\n📋 테스트 {i}/{len(test_combinations)}: {provider}/{model}/{agent_type}")
            print(f"    파일: {test_case.get('test_id', 'unknown')}")

            result = self.run_single_test(provider, model, agent_type, test_case)
            results.append(result)

            if result.get('success'):
                print(f"    ✅ 완료 ({result['response_time']:.2f}초)")
                if result['valid_json']:
                    print(f"    🎯 신뢰도: {result['confidence_score']:.3f}")
                    print(f"    🔍 취약점: {result['detected_vulnerabilities']}개")
            else:
                print(f"    ❌ 실패: {result.get('error', 'Unknown error')}")

            # API 제한 방지를 위한 딜레이
            if provider != 'ollama' and i < len(test_combinations):
                time.sleep(1)

        return results

    def _run_parallel_tests(self, test_combinations: List) -> List[Dict[str, Any]]:
        """병렬 테스트 실행"""
        results = []
        max_workers = 3  # 동시 실행 수 제한

        print(f"🔄 병렬 처리 (최대 {max_workers}개 동시 실행)")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_test = {}

            for provider, model, agent_type, test_case in test_combinations:
                future = executor.submit(
                    self.run_single_test, provider, model, agent_type, test_case
                )
                future_to_test[future] = (provider, model, agent_type, test_case)

            for i, future in enumerate(as_completed(future_to_test), 1):
                provider, model, agent_type, test_case = future_to_test[future]

                try:
                    result = future.result()
                    results.append(result)

                    print(f"✅ 완료 {i}/{len(test_combinations)}: {provider}/{model}/{agent_type}")

                except Exception as e:
                    print(f"❌ 실패 {i}/{len(test_combinations)}: {provider}/{model}/{agent_type} - {e}")
                    results.append({
                        'provider': provider,
                        'model': model,
                        'agent_type': agent_type,
                        'test_id': test_case.get('test_id', 'unknown'),
                        'success': False,
                        'error': str(e)
                    })

        return results

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """결과 요약 생성"""
        total = len(results)
        successful = len([r for r in results if r.get('success', False)])

        summary = {
            'total_tests': total,
            'successful_tests': successful,
            'success_rate': successful / total if total > 0 else 0,
            'by_provider': {},
            'by_agent': {},
            'by_model': {}
        }

        # 프로바이더별 통계
        for result in results:
            if not result.get('success'):
                continue

            provider = result.get('provider', 'unknown')
            agent = result.get('agent_type', 'unknown')
            model = result.get('model', 'unknown')

            # 프로바이더별
            if provider not in summary['by_provider']:
                summary['by_provider'][provider] = {
                    'total': 0, 'successful': 0, 'avg_response_time': 0,
                    'avg_confidence': 0, 'avg_vulnerabilities': 0
                }

            p_stats = summary['by_provider'][provider]
            p_stats['total'] += 1
            if result.get('success'):
                p_stats['successful'] += 1
                p_stats['avg_response_time'] += result.get('response_time', 0)
                p_stats['avg_confidence'] += result.get('confidence_score', 0)
                p_stats['avg_vulnerabilities'] += result.get('detected_vulnerabilities', 0)

            # 에이전트별
            if agent not in summary['by_agent']:
                summary['by_agent'][agent] = {'total': 0, 'successful': 0}
            summary['by_agent'][agent]['total'] += 1
            if result.get('success'):
                summary['by_agent'][agent]['successful'] += 1

            # 모델별
            model_key = f"{provider}/{model}"
            if model_key not in summary['by_model']:
                summary['by_model'][model_key] = {'total': 0, 'successful': 0}
            summary['by_model'][model_key]['total'] += 1
            if result.get('success'):
                summary['by_model'][model_key]['successful'] += 1

        # 평균 계산
        for provider, stats in summary['by_provider'].items():
            if stats['successful'] > 0:
                stats['avg_response_time'] /= stats['successful']
                stats['avg_confidence'] /= stats['successful']
                stats['avg_vulnerabilities'] /= stats['successful']
                stats['success_rate'] = stats['successful'] / stats['total']

        return summary

    def save_results(self, filename: str = None) -> str:
        """결과를 JSON과 CSV 형식으로 저장"""
        if filename is None:
            timestamp = int(time.time())
            json_filename = f"benchmark_results_{timestamp}.json"
            csv_filename = f"benchmark_results_{timestamp}.csv"
        else:
            base_name = filename.rsplit('.', 1)[0]
            json_filename = f"{base_name}.json"
            csv_filename = f"{base_name}.csv"

        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        # JSON 저장
        json_filepath = results_dir / json_filename
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # CSV 저장
        csv_filepath = results_dir / csv_filename
        self._save_csv_results(csv_filepath)

        print(f"💾 결과가 저장되었습니다:")
        print(f"   JSON: {json_filepath}")
        print(f"   CSV: {csv_filepath}")
        return str(json_filepath)

    def _save_csv_results(self, filepath: Path):
        """결과를 CSV 형식으로 저장"""
        detailed_results = self.results.get('detailed_results', [])

        if not detailed_results:
            print("❌ CSV로 저장할 결과가 없습니다.")
            return

        # CSV 헤더 정의
        fieldnames = [
            'test_id', 'provider', 'model', 'agent_type', 'success',
            'valid_json', 'confidence_score', 'detected_vulnerabilities',
            'response_time', 'json_valid', 'summary', 'file_path',
            'total_tokens', 'prompt_tokens', 'completion_tokens',
            'timestamp', 'error'
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in detailed_results:
                # 기본 데이터 추출
                csv_row = {
                    'test_id': result.get('test_id', ''),
                    'provider': result.get('provider', ''),
                    'model': result.get('model', ''),
                    'agent_type': result.get('agent_type', ''),
                    'success': result.get('success', False),
                    'valid_json': result.get('valid_json', False),
                    'confidence_score': result.get('confidence_score', 0),
                    'detected_vulnerabilities': result.get('detected_vulnerabilities', 0),
                    'response_time': result.get('response_time', 0),
                    'json_valid': result.get('json_valid', False),
                    'summary': result.get('summary', '').replace('\n', ' ').replace('\r', ' '),
                    'file_path': result.get('file_path', ''),
                    'timestamp': result.get('timestamp', 0),
                    'error': result.get('error', '')
                }

                # 토큰 사용량 추출
                usage = result.get('usage', {})
                if isinstance(usage, dict):
                    csv_row['total_tokens'] = usage.get('total_tokens', 0)
                    csv_row['prompt_tokens'] = usage.get('prompt_tokens', 0)
                    csv_row['completion_tokens'] = usage.get('completion_tokens', 0)
                else:
                    csv_row['total_tokens'] = 0
                    csv_row['prompt_tokens'] = 0
                    csv_row['completion_tokens'] = 0

                writer.writerow(csv_row)

    def print_summary(self):
        """요약 결과 출력"""
        if not self.results:
            print("❌ 실행된 벤치마크 결과가 없습니다.")
            return

        summary = self.results['summary']

        print("\n" + "=" * 60)
        print("📊 벤치마크 결과 요약")
        print("=" * 60)

        print(f"전체 테스트: {summary['total_tests']}")
        print(f"성공: {summary['successful_tests']}")
        print(f"성공률: {summary['success_rate']:.1%}")

        print(f"\n🏆 프로바이더별 성능:")
        for provider, stats in summary['by_provider'].items():
            print(f"  {provider}:")
            print(f"    성공률: {stats.get('success_rate', 0):.1%}")
            print(f"    평균 응답시간: {stats.get('avg_response_time', 0):.2f}초")
            print(f"    평균 신뢰도: {stats.get('avg_confidence', 0):.3f}")
            print(f"    평균 취약점 탐지: {stats.get('avg_vulnerabilities', 0):.1f}개")

        print(f"\n🎯 에이전트별 성공률:")
        for agent, stats in summary['by_agent'].items():
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            print(f"  {agent}: {success_rate:.1%} ({stats['successful']}/{stats['total']})")

def main():
    parser = argparse.ArgumentParser(description='AI 벤치마크 실행')
    parser.add_argument('--providers', nargs='+',
                       choices=['google', 'openai', 'xai', 'ollama'],
                       help='테스트할 프로바이더들')
    parser.add_argument('--agents', nargs='+',
                       choices=['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config'],
                       help='테스트할 에이전트들')
    parser.add_argument('--limit', type=int, help='에이전트당 테스트 파일 수 제한')
    parser.add_argument('--parallel', action='store_true', help='병렬 실행')
    parser.add_argument('--output', help='결과 파일명')

    args = parser.parse_args()

    runner = BenchmarkRunner()

    try:
        runner.run_benchmark(
            providers=args.providers,
            agents=args.agents,
            test_limit=args.limit,
            parallel=args.parallel
        )

        runner.print_summary()
        runner.save_results(args.output)

    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 벤치마크 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()