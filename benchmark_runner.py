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
        """사용 가능한 모델들을 조회 (config에서 동적으로 로드)"""
        models = {}

        # API 기반 프로바이더들 (google, openai, xai)
        for provider in ['google', 'openai', 'xai']:
            try:
                provider_config = self.config_loader.get_llm_config(provider)
                model_value = provider_config.get('model')

                # 모델이 리스트인 경우
                if isinstance(model_value, list):
                    models[provider] = model_value
                # 모델이 문자열인 경우
                elif isinstance(model_value, str):
                    models[provider] = [model_value]
                else:
                    models[provider] = []

                if models[provider]:
                    print(f"✅ {provider} 모델: {models[provider]}")
            except Exception as e:
                models[provider] = []
                print(f"❌ {provider} 설정 로드 실패: {e}")

        # Ollama 모델 가용성 확인
        try:
            # 먼저 config에서 설정 읽기
            ollama_config = self.config_loader.get_llm_config('ollama')
            configured_models = ollama_config.get('model', [])

            if isinstance(configured_models, str):
                configured_models = [configured_models]

            # Base URL 가져오기
            base_url = ollama_config.get('base_url', 'http://localhost:11434')

            # Ollama 클라이언트로 서버 체크
            ollama_client = OllamaClient(base_url=base_url)
            available_ollama = ollama_client.list_available_models()

            if available_ollama:
                # 사용 가능한 모델만 필터링
                models['ollama'] = [m for m in configured_models if m in available_ollama]
                print(f"✅ Ollama 사용 가능한 모델: {models['ollama']}")

                if not models['ollama']:
                    print(f"⚠️  설정된 모델 {configured_models}이 Ollama에 없습니다.")
                    print(f"   사용 가능: {available_ollama}")
            else:
                models['ollama'] = []
                print("❌ Ollama 서버가 실행되지 않거나 모델이 없습니다.")
        except Exception as e:
            models['ollama'] = []
            print(f"❌ Ollama 확인 실패: {e}")
            import traceback
            traceback.print_exc()

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
            print(f"    🔧 Debug: {provider}/{model} 테스트 시작")
            # 클라이언트 생성
            if provider == 'ollama':
                client = ClientFactory.create_client(provider, {
                    'api_key': 'not_required',
                    'model': model,
                    'base_url': 'http://localhost:11434'
                })
            else:
                llm_config = self.config_loader.get_llm_config(provider, model_name=model)
                client = ClientFactory.create_client(provider, llm_config)

            # 에이전트 생성
            print(f"    🔧 Debug: 에이전트 생성 중...")
            agent = AgentFactory.create_agent(agent_type)
            print(f"    🔧 Debug: 에이전트 생성 완료")

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
            print(f"    🔧 Debug: API 호출 시작...")
            max_tokens = 1500 if provider == 'ollama' else 2000
            if 'qwen3' in model:
                max_tokens = 1000  # Qwen3은 더 짧은 토큰으로 설정
            response = client.benchmark_request(prompt, max_tokens)
            print(f"    🔧 Debug: API 호출 완료, success={response.get('success', 'unknown')}")

            if not response['success']:
                print(f"    ⚠️  API 호출 실패 ({provider}/{model}): {response['error']}")
                return {
                    'error': response['error'],
                    'test_id': test_case.get('test_id', 'unknown'),
                    'response_time': response['response_time']
                }

            # 결과 파싱
            print(f"    🔧 Debug: 결과 파싱 시작...")
            findings = agent.extract_key_findings(response['content'])
            print(f"    🔧 Debug: 파싱 완료, valid_json={findings.get('valid_json', 'unknown')}")
            if not findings.get('valid_json', False) and 'qwen3' in model:
                print(f"    🔧 Debug Qwen3 응답: {response['content'][:500]}...")

            # 실제 양자 취약 알고리즘 수 계산
            print(f"    🔧 Debug: 양자 취약 알고리즘 추출 시작...")
            detected_quantum_vulnerable_algorithms = []
            if findings['valid_json']:
                analysis_results = findings['analysis_results']

                # 각 분석 결과에서 실제 양자 취약 알고리즘 추출
                for category, result in analysis_results.items():
                    if result and result.lower() not in ['none', 'not detected', 'no', '', 'not present', 'no implementations']:
                        # 알고리즘 이름 추출 (새로운 형식에 맞게)
                        import re
                        result_lower = result.lower()

                        # "DETECTED:" 형식으로 응답하는 경우만 처리
                        if result_lower.startswith('detected:'):
                            # "DETECTED: RSA" → "RSA" 추출
                            detected_algo = result.split(':', 1)[1].strip()
                            detected_quantum_vulnerable_algorithms.append(detected_algo.upper())
                        else:
                            # 기존 방식도 유지 (하위 호환성)
                            # 부정적 표현 체크
                            negative_indicators = ['does not contain', 'not contain', 'no implementation', 'not found', 'absent', 'missing', 'not present', 'free from', 'not detected']
                            has_negative_indicator = any(indicator in result_lower for indicator in negative_indicators)

                            if has_negative_indicator:
                                continue  # 부정적 응답은 건너뛰기

                            # 주요 양자 취약 알고리즘들 체크 (우선순위 순으로 정렬)
                            quantum_vulnerable_algos = [
                                # 길이가 긴 것부터 체크하여 중복 방지
                                ('diffie-hellman', 'DH'), ('ecdsa', 'ECDSA'), ('ecdh', 'ECDH'),
                                ('aes-128', 'AES-128'), ('3des', '3DES'), ('sha-1', 'SHA-1'),
                                ('has-160', 'HAS-160'), ('kcdsa', 'KCDSA'), ('a5/1', 'A5/1'),
                                ('misty1', 'MISTY1'), ('twofish', 'Twofish'), ('blowfish', 'Blowfish'),
                                ('skipjack', 'Skipjack'), ('elgamal', 'ElGamal'), ('trivium', 'Trivium'),
                                ('whirlpool', 'Whirlpool'), ('tiger', 'Tiger'), ('cast', 'CAST'),
                                ('idea', 'IDEA'), ('rsa', 'RSA'), ('ecc', 'ECC'), ('dsa', 'DSA'),
                                ('dh', 'DH'), ('aes', 'AES'), ('des', 'DES'), ('rc4', 'RC4'),
                                ('md5', 'MD5'), ('sha1', 'SHA-1'), ('seed', 'SEED'), ('aria', 'ARIA'),
                                ('hight', 'HIGHT'), ('lea', 'LEA'), ('lsh', 'LSH'), ('a5', 'A5')
                            ]

                            # 명확한 탐지 표현이 있는 경우만 카운팅
                            positive_indicators = ['detected', 'found', 'implementation', 'algorithm', 'cipher', 'present', 'identified', 'system', 'used', 'exists', 'contains']
                            has_positive_indicator = any(indicator in result_lower for indicator in positive_indicators)

                            if has_positive_indicator:
                                for algo_pattern, display_name in quantum_vulnerable_algos:
                                    # 정확한 단어 매칭 (경계 포함)
                                    if re.search(r'\b' + re.escape(algo_pattern) + r'\b', result_lower):
                                        if display_name not in detected_quantum_vulnerable_algorithms:
                                            detected_quantum_vulnerable_algorithms.append(display_name)
                                            break  # 첫 번째 매치만 사용

            detected_quantum_vulnerable_count = len(detected_quantum_vulnerable_algorithms)

            # Success 평가: Ground truth와 비교하여 정확도 계산
            success = False
            accuracy_score = 0.0

            if findings['valid_json']:
                # Ground truth 로드
                ground_truth = self._load_ground_truth(test_case, agent_type)
                if ground_truth:
                    try:
                        from utils.metrics_calculator import MetricsCalculator
                        accuracy_score = MetricsCalculator.calculate_accuracy(findings, ground_truth)
                        print(f"    🔧 Debug: 정확도 계산 완료: {accuracy_score:.3f}")
                        # 60% 이상 정확도면 성공으로 간주
                        success = accuracy_score >= 0.6
                    except Exception as metric_error:
                        print(f"    ❌ 정확도 계산 실패: {metric_error}")
                        accuracy_score = 0.0
                        success = False
                else:
                    # Ground truth가 없으면 실패로 처리 (정답을 알 수 없으므로)
                    print(f"    ⚠️  Ground truth가 없어서 성공 여부를 판단할 수 없습니다.")
                    success = False
            else:
                success = False

            print(f"    🔧 Debug: 결과 구성 시작...")
            result = {
                'test_id': test_case.get('test_id', 'unknown'),
                'provider': provider,
                'model': model,
                'agent_type': agent_type,
                'success': success,
                'accuracy_score': accuracy_score,
                'valid_json': findings.get('valid_json', False),
                'confidence_score': findings.get('confidence_score', 0.0),
                'detected_quantum_vulnerable_count': detected_quantum_vulnerable_count,
                'detected_algorithms': detected_quantum_vulnerable_algorithms,
                'response_time': response.get('response_time', 0.0),
                'json_valid': response.get('json_valid', False),
                'summary': findings.get('summary', ''),
                'analysis_results': findings.get('analysis_results', {}),
                'usage': response.get('usage', {}),
                'file_path': test_case.get('file_path', ''),
                'raw_response': findings.get('raw_response', response.get('content', '')),
                'timestamp': time.time()
            }
            print(f"    🔧 Debug: 결과 구성 완료")
            return result

        except Exception as e:
            import traceback
            error_details = f"{str(e)} | Traceback: {traceback.format_exc()}"
            print(f"    ⚠️  예외 발생 ({provider}/{model}): {error_details}")

            return {
                'test_id': test_case.get('test_id', 'unknown'),
                'provider': provider,
                'model': model,
                'agent_type': agent_type,
                'success': False,
                'error': str(e),  # 사용자에게는 간단한 에러만 표시
                'error_details': error_details,  # 상세 정보는 별도 필드
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
            providers = ['ollama', 'google', 'openai', 'xai']
        if agents is None:
            agents = ['source_code', 'assembly_binary', 'logs_config']

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
        backup_interval = 10  # 10개 테스트마다 백업

        for i, (provider, model, agent_type, test_case) in enumerate(test_combinations, 1):
            print(f"\n📋 테스트 {i}/{len(test_combinations)}: {provider}/{model}/{agent_type}")
            print(f"    파일: {test_case.get('test_id', 'unknown')}")

            result = self.run_single_test(provider, model, agent_type, test_case)
            results.append(result)

            if result.get('success'):
                print(f"    ✅ 완료 ({result['response_time']:.2f}초)")
                if result['valid_json']:
                    print(f"    🎯 신뢰도: {result['confidence_score']:.3f}")
                    vuln_count = result['detected_quantum_vulnerable_count']
                    if vuln_count > 0:
                        # 탐지된 알고리즘 이름들 표시
                        detected_algos = result.get('detected_algorithms', [])
                        if detected_algos:
                            algos_str = ', '.join(detected_algos[:4])  # 최대 3개만 표시
                            if len(detected_algos) > 3:
                                algos_str += f" 외 {len(detected_algos)-3}개"
                            print(f"    🔍 탐지된 양자 취약 알고리즘: {algos_str}")
                        else:
                            print(f"    🔍 양자 취약 알고리즘: {vuln_count}개")
                    else:
                        print(f"    🔍 양자 취약 알고리즘: 없음")
            else:
                if 'accuracy_score' in result:
                    print(f"    ❌ 실패: 정확도 {result['accuracy_score']:.1%} < 60% 임계값")
                else:
                    print(f"    ❌ 실패: {result.get('error', 'Unknown error')}")

            # 주기적 백업 (Google Drive)
            if i % backup_interval == 0:
                self._backup_intermediate_results(results, i, len(test_combinations))

            # API 제한 방지를 위한 딜레이
            if provider != 'ollama' and i < len(test_combinations):
                time.sleep(1)

        return results

    def _backup_intermediate_results(self, results: List[Dict[str, Any]], current: int, total: int):
        """중간 결과 백업 (Google Drive)"""
        gdrive_dir = os.environ.get('GDRIVE_RESULTS_DIR')
        if not gdrive_dir or not os.path.exists(gdrive_dir):
            return

        try:
            timestamp = int(time.time())
            backup_filename = f"backup_progress_{current}of{total}_{timestamp}.json"
            backup_path = os.path.join(gdrive_dir, backup_filename)

            backup_data = {
                'progress': f"{current}/{total}",
                'timestamp': timestamp,
                'completed_tests': current,
                'total_tests': total,
                'results': results
            }

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            print(f"    💾 중간 백업 완료: {backup_filename}")
        except Exception as e:
            print(f"    ⚠️  중간 백업 실패: {e}")

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
            provider = result.get('provider', 'unknown')
            agent = result.get('agent_type', 'unknown')
            model = result.get('model', 'unknown')

            # 프로바이더별
            if provider not in summary['by_provider']:
                summary['by_provider'][provider] = {
                    'total': 0, 'successful': 0, 'avg_response_time': 0,
                    'avg_confidence': 0, 'avg_quantum_vulnerable': 0
                }

            p_stats = summary['by_provider'][provider]
            p_stats['total'] += 1
            if result.get('success'):
                p_stats['successful'] += 1
                p_stats['avg_response_time'] += result.get('response_time', 0)
                p_stats['avg_confidence'] += result.get('confidence_score', 0)
                p_stats['avg_quantum_vulnerable'] += result.get('detected_quantum_vulnerable_count', 0)

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
                stats['avg_quantum_vulnerable'] /= stats['successful']
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
        json_filepath = Path(json_filename)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # CSV 저장
        csv_filepath = Path(csv_filename)
        self._save_csv_results(csv_filepath)

        print(f"💾 결과가 저장되었습니다:")
        print(f"   JSON: {json_filepath}")
        print(f"   CSV: {csv_filepath}")

        # Google Drive 자동 백업 (환경 변수가 설정된 경우)
        gdrive_dir = os.environ.get('GDRIVE_RESULTS_DIR')
        if gdrive_dir and os.path.exists(gdrive_dir):
            try:
                import shutil
                gdrive_json = os.path.join(gdrive_dir, json_filename)
                gdrive_csv = os.path.join(gdrive_dir, csv_filename)

                shutil.copy2(json_filepath, gdrive_json)
                shutil.copy2(csv_filepath, gdrive_csv)

                print(f"☁️  Google Drive 백업 완료:")
                print(f"   JSON: {gdrive_json}")
                print(f"   CSV: {gdrive_csv}")
            except Exception as e:
                print(f"⚠️  Google Drive 백업 실패: {e}")

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
            'valid_json', 'confidence_score', 'detected_quantum_vulnerable_count',
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
                    'detected_quantum_vulnerable_count': result.get('detected_quantum_vulnerable_count', 0),
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

        print(f"\n🏆 모델별 성능:")
        for model, stats in summary['by_model'].items():
            print(f"  {model}:")
            print(f"    성공률: {stats.get('success_rate', 0):.1%}")
            print(f"    평균 응답시간: {stats.get('avg_response_time', 0):.2f}초")
            print(f"    평균 신뢰도: {stats.get('avg_confidence', 0):.3f}")
            print(f"    평균 양자 취약 알고리즘 탐지: {stats.get('avg_quantum_vulnerable', 0):.1f}개")

        print(f"\n🎯 에이전트별 성공률:")
        for agent, stats in summary['by_agent'].items():
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            print(f"  {agent}: {success_rate:.1%} ({stats['successful']}/{stats['total']})")

    def _load_ground_truth(self, test_case: Dict[str, Any], agent_type: str = None) -> Dict[str, Any]:
        """테스트 케이스에 대한 ground truth 로드"""
        try:
            test_id = test_case.get('test_id', '')
            # agent_type 매개변수가 전달되면 사용, 아니면 test_case에서 추출
            if agent_type is None:
                agent_type = test_case.get('type', 'source_code')

            # Ground truth 파일 경로 생성
            ground_truth_path = f"data/ground_truth/{agent_type}/{test_id}.json"

            print(f"    🔧 Debug: Ground truth 경로 시도: {ground_truth_path}")

            if os.path.exists(ground_truth_path):
                with open(ground_truth_path, 'r', encoding='utf-8') as f:
                    ground_truth = json.load(f)
                    print(f"    🔧 Debug: Ground truth 로드 성공: {ground_truth}")
                    return ground_truth
            else:
                print(f"    ⚠️  Ground truth 파일 없음: {ground_truth_path}")
        except Exception as e:
            print(f"    ❌ Ground truth 로드 실패: {e}")

        return None

def main():
    parser = argparse.ArgumentParser(description='AI 벤치마크 실행')
    parser.add_argument('--providers', nargs='+',
                       choices=['google', 'openai', 'xai', 'ollama'],
                       help='테스트할 프로바이더들')
    parser.add_argument('--agents', nargs='+',
                       choices=['source_code', 'assembly_binary', 'logs_config'],
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