#!/usr/bin/env python3
"""
RAG 효과 측정 벤치마크

같은 기본 모델로 RAG 유무에 따른 성능 차이를 비교합니다:
- PQC Inspector (RAG 포함) vs 기본 모델 (RAG 없음)
"""

import os
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from clients.pqc_inspector_client import PQCInspectorClient
from clients.ollama_client import OllamaClient
from clients.google_client import GoogleClient
from agents.agent_factory import AgentFactory
from utils.test_case_manager import TestCaseManager
from config.config_loader import ConfigLoader


class RAGEffectBenchmark:
    """
    RAG 효과 측정 벤치마크

    비교 모델:
    1. llama3:8b (PQC Inspector + RAG) vs llama3:8b (순수)
    2. gemini-2.0-flash-exp (PQC Inspector + RAG) vs gemini-2.0-flash-exp (순수)
    """

    def __init__(self, pqc_base_url: str = "http://localhost:8000",
                 ollama_base_url: str = "http://localhost:11434"):
        self.pqc_base_url = pqc_base_url
        self.ollama_base_url = ollama_base_url

        # ConfigLoader 초기화
        self.config_loader = ConfigLoader()

        # 테스트 케이스 매니저
        self.test_manager = TestCaseManager(
            test_cases_dir="data/test_cases",
            ground_truth_dir="data/ground_truth",
            test_files_dir="data/test_files"
        )

        # 결과 저장
        self.results = []

        # 테스트할 모델 목록
        self.test_models = []

    def setup_test_models(self, models: List[str] = None):
        """테스트할 모델 설정"""
        if models:
            self.test_models = models
        else:
            # 기본 모델들
            self.test_models = [
                "llama3:8b",
                "gemini-2.0-flash-exp"
            ]

        print(f"📋 테스트 모델: {self.test_models}")

    def restart_ai_server_with_model(self, model: str, agent_type: str) -> bool:
        """
        AI-Server의 에이전트 모델을 변경하고 재시작

        주의: 실제로는 .env 파일을 수정하고 서버를 재시작해야 합니다.
        이 메서드는 자동화된 방법을 제공합니다.
        """
        print(f"\n🔄 AI-Server 설정 변경: {agent_type} → {model}")

        # .env 파일 경로
        env_file = Path("../AI-Server/.env")

        if not env_file.exists():
            print(f"❌ .env 파일을 찾을 수 없습니다: {env_file}")
            return False

        # 에이전트 타입에 따른 환경 변수 이름
        env_var_map = {
            'source_code': 'SOURCE_CODE_MODEL',
            'assembly_binary': 'BINARY_MODEL',
            'logs_config': 'LOG_CONF_MODEL'
        }

        if agent_type not in env_var_map:
            print(f"❌ 잘못된 에이전트 타입: {agent_type}")
            return False

        env_var_name = env_var_map[agent_type]

        # .env 파일 읽기
        with open(env_file, 'r') as f:
            lines = f.readlines()

        # 해당 변수 찾아서 수정
        modified = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{env_var_name}="):
                new_lines.append(f"{env_var_name}={model}\n")
                modified = True
            else:
                new_lines.append(line)

        if not modified:
            # 변수가 없으면 추가
            new_lines.append(f"\n{env_var_name}={model}\n")

        # .env 파일 쓰기
        with open(env_file, 'w') as f:
            f.writelines(new_lines)

        print(f"✅ .env 파일 업데이트: {env_var_name}={model}")
        print(f"⚠️  수동으로 AI-Server를 재시작해주세요!")
        print(f"   cd AI-Server && python main.py")

        # 사용자에게 재시작 확인 요청
        input(f"\n🔄 AI-Server를 재시작한 후 Enter를 눌러주세요...")

        return True

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
            else:
                print(f"❌ PQC Inspector 서버 접속 불가: {self.pqc_base_url}")
                return False
        except Exception as e:
            print(f"❌ PQC Inspector 확인 실패: {e}")
            return False

        # Ollama 확인 (llama3:8b 모델 사용시)
        if any("llama" in m or ":" in m for m in self.test_models):
            try:
                ollama_client = OllamaClient(base_url=self.ollama_base_url)
                available_models = ollama_client.list_available_models()
                print(f"✅ Ollama 서버 실행 중: {self.ollama_base_url}")
                print(f"   사용 가능한 모델: {available_models}")
            except Exception as e:
                print(f"❌ Ollama 확인 실패: {e}")
                return False

        print("=" * 80)
        return True

    def run_benchmark(self, limit_per_agent: int = None, agent_filter: List[str] = None,
                      auto_restart: bool = False):
        """
        RAG 효과 측정 벤치마크 실행

        Args:
            limit_per_agent: 에이전트당 테스트 파일 수 제한
            agent_filter: 테스트할 에이전트 선택
            auto_restart: AI-Server 자동 재시작 여부
        """
        if not self.check_servers():
            print("\n❌ 서버 확인 실패. 벤치마크를 종료합니다.")
            return

        print("\n" + "=" * 80)
        print("🚀 RAG 효과 측정 벤치마크 시작")
        print("=" * 80)

        # 에이전트 타입
        agent_types = ['source_code', 'assembly_binary', 'logs_config']
        if agent_filter:
            agent_types = [a for a in agent_types if a in agent_filter]

        # 각 모델에 대해 테스트
        for model in self.test_models:
            print(f"\n{'='*80}")
            print(f"📊 모델: {model}")
            print(f"{'='*80}")

            for agent_type in agent_types:
                # 테스트 케이스 로드
                test_cases = self.test_manager.load_test_cases(agent_type)
                if limit_per_agent:
                    test_cases = test_cases[:limit_per_agent]

                print(f"\n📁 {agent_type}: {len(test_cases)}개 테스트")

                # AI-Server 모델 변경 (자동 재시작 모드)
                if auto_restart:
                    self.restart_ai_server_with_model(model, agent_type)

                for idx, test_case in enumerate(test_cases, 1):
                    file_name = test_case.get('file_name') or Path(test_case.get('file_path', 'unknown')).name
                    print(f"\n--- 테스트 {idx}/{len(test_cases)}: {file_name} ---")

                    # 1. PQC Inspector (RAG 포함) 테스트
                    rag_result = self.test_with_rag(model, agent_type, test_case)
                    if rag_result:
                        self.results.append(rag_result)
                        print(f"✅ {model} + RAG: TP={rag_result.get('true_positives', 0)}, "
                              f"FP={rag_result.get('false_positives', 0)}, "
                              f"FN={rag_result.get('false_negatives', 0)}, "
                              f"시간={rag_result.get('response_time', 0):.2f}초")

                    # 2. 기본 모델 (RAG 없음) 테스트
                    base_result = self.test_without_rag(model, agent_type, test_case)
                    if base_result:
                        self.results.append(base_result)
                        print(f"✅ {model} (순수): TP={base_result.get('true_positives', 0)}, "
                              f"FP={base_result.get('false_positives', 0)}, "
                              f"FN={base_result.get('false_negatives', 0)}, "
                              f"시간={base_result.get('response_time', 0):.2f}초")

        print("\n" + "=" * 80)
        print(f"📊 벤치마크 완료: 총 {len(self.results)} 테스트")
        print("=" * 80)

    def test_with_rag(self, model: str, agent_type: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """PQC Inspector (RAG 포함) 테스트"""
        try:
            # 클라이언트 생성
            client = PQCInspectorClient(
                model=agent_type,
                base_url=self.pqc_base_url
            )

            # 파일 경로
            file_path = test_case.get('file_path', '')
            if not Path(file_path).exists():
                print(f"⚠️  파일 없음: {file_path}")
                # 파일 없음도 에러로 처리
                return {
                    'base_model': model,
                    'with_rag': True,
                    'agent_type': agent_type,
                    'test_id': test_case.get('test_id'),
                    'file_name': test_case.get('file_name') or Path(test_case.get('file_path', 'unknown')).name,
                    'response_time': 0,
                    'json_valid': False,
                    'true_positives': 0,
                    'false_positives': 0,
                    'false_negatives': 0,
                    'error': 'file not found',
                    'raw_response': {}
                }

            # 분석 실행
            prompt = f"FILE_PATH:{file_path}"
            result = client.benchmark_request(prompt)

            if not result.get('success'):
                error_msg = result.get('error', 'unknown error')
                print(f"❌ RAG 테스트 실패: {error_msg}")

                # 에러 케이스는 결과에 포함하되, F1 계산에서 제외하기 위해 플래그 추가
                return {
                    'base_model': model,
                    'with_rag': True,
                    'agent_type': agent_type,
                    'test_id': test_case.get('test_id'),
                    'file_name': test_case.get('file_name') or Path(test_case.get('file_path', 'unknown')).name,
                    'response_time': 0,
                    'json_valid': False,
                    'true_positives': 0,
                    'false_positives': 0,
                    'false_negatives': 0,
                    'error': error_msg,  # 에러 플래그
                    'raw_response': {}
                }

            # 응답 파싱
            response_content = result.get('content', '{}')
            try:
                analysis_result = json.loads(response_content)
            except json.JSONDecodeError:
                analysis_result = {}

            # Ground truth 로드
            test_id = test_case.get('test_id')
            ground_truth = self.test_manager.load_ground_truth(agent_type, test_id)

            # RAG 응답을 표준 형식으로 변환
            if 'detected_algorithms' in analysis_result:
                # PQC Inspector 간단한 형식 → analysis_results 형식 변환
                detected_algs = analysis_result.get('detected_algorithms', [])
                algorithms_text = ', '.join(detected_algs)

                # 각 알고리즘을 적절한 카테고리에 매핑
                analysis_points = {}
                for alg in detected_algs:
                    alg_lower = alg.lower()
                    if 'rsa' in alg_lower:
                        analysis_points['quantum_vulnerable_rsa_implementations_and_usage_patterns'] = f"DETECTED: {alg}"
                    if 'ecc' in alg_lower or 'ecdsa' in alg_lower or 'ecdh' in alg_lower:
                        analysis_points['elliptic_curve_cryptography_ecc_ecdsa_ecdh_implementations'] = f"DETECTED: {alg}"
                    if 'dsa' in alg_lower or 'dh' in alg_lower:
                        analysis_points['discrete_logarithm_based_algorithms_dsa_dh_elgamal'] = f"DETECTED: {alg}"
                    if any(k in alg_lower for k in ['seed', 'aria', 'hight', 'lea', 'kcdsa']):
                        analysis_points['korean_domestic_algorithms_seed_aria_hight_lea_kcdsa_ec_kcdsa_has_160_lsh'] = f"DETECTED: {alg}"

                # 나머지는 NOT DETECTED로 채움
                all_points = [
                    'quantum_vulnerable_rsa_implementations_and_usage_patterns',
                    'elliptic_curve_cryptography_ecc_ecdsa_ecdh_implementations',
                    'discrete_logarithm_based_algorithms_dsa_dh_elgamal',
                    'korean_domestic_algorithms_seed_aria_hight_lea_kcdsa_ec_kcdsa_has_160_lsh',
                    'symmetric_ciphers_vulnerable_to_grover\'s_algorithm_aes_128_3des_des_rc4',
                    'weak_hash_functions_md5_sha_1_sha_256_with_reduced_security'
                ]

                for point in all_points:
                    if point not in analysis_points:
                        analysis_points[point] = "NOT DETECTED"

                standardized_response = {
                    'valid_json': True,
                    'analysis_results': analysis_points,
                    'confidence_score': analysis_result.get('confidence_score', 0.0)
                }
            else:
                # 이미 analysis_results 형식
                standardized_response = {
                    'valid_json': True,
                    'analysis_results': analysis_result
                }

            # 메트릭 계산 - Ground truth와 실제 비교
            if ground_truth and 'expected_findings' in ground_truth:
                expected_algs = set()
                vulnerable_algs = ground_truth['expected_findings'].get('vulnerable_algorithms_detected', [])
                expected_algs = set([alg.lower() for alg in vulnerable_algs])

                # 탐지된 알고리즘 추출 및 정규화
                detected_algs_raw = set()
                if 'detected_algorithms' in analysis_result:
                    detected_algs_raw = set([alg.lower() for alg in analysis_result['detected_algorithms']])

                # 예상 알고리즘과 매칭 (변형 고려)
                matched_expected = set()  # 매칭된 expected 알고리즘
                for detected in detected_algs_raw:
                    for expected in expected_algs:
                        # 알고리즘 변형 매칭
                        if expected == detected:
                            matched_expected.add(expected)
                            break
                        elif expected == 'ecc' and detected in ['ecdsa', 'ecdh', 'ecc']:
                            matched_expected.add(expected)
                            break
                        elif expected == 'rsa' and 'rsa' in detected:
                            matched_expected.add(expected)
                            break
                        elif expected == 'dsa' and detected in ['dsa', 'ecdsa']:
                            matched_expected.add(expected)
                            break
                        elif expected == 'aes' and 'aes' in detected:
                            matched_expected.add(expected)
                            break
                        elif expected == 'md5' and 'md5' in detected:
                            matched_expected.add(expected)
                            break

                # TP, FP, FN 계산
                true_positives = len(matched_expected)
                false_positives = len(detected_algs_raw) - true_positives
                false_negatives = len(expected_algs) - true_positives

                # 개별 메트릭은 저장하지 않음 (전체 합산 후 계산)
                metrics = {
                    'true_positives': true_positives,
                    'false_positives': false_positives,
                    'false_negatives': false_negatives
                }
            else:
                metrics = {
                    'true_positives': 0,
                    'false_positives': 0,
                    'false_negatives': 0
                }

            return {
                'base_model': model,
                'with_rag': True,
                'agent_type': agent_type,
                'test_id': test_case.get('test_id'),
                'file_name': test_case.get('file_name') or Path(test_case.get('file_path', 'unknown')).name,
                'response_time': result.get('response_time', 0),
                'json_valid': result.get('json_valid', False),
                **metrics,
                'raw_response': analysis_result
            }

        except Exception as e:
            print(f"❌ RAG 테스트 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def test_without_rag(self, model: str, agent_type: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """기본 모델 (RAG 없음) 테스트"""
        try:
            # 모델에 따라 클라이언트 선택
            if ":" in model:  # Ollama 모델
                client = OllamaClient(
                    model=model,
                    base_url=self.ollama_base_url
                )
            elif model.startswith("gemini-"):
                config = self.config_loader.get_llm_config('google')
                client = GoogleClient(
                    api_key=config['api_key'],
                    model=model,
                    base_url=config.get('base_url', '')
                )
            else:
                print(f"⚠️  지원하지 않는 모델: {model}")
                return None

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
                error_msg = result.get('error', 'unknown error')
                print(f"❌ 기본 모델 테스트 실패 (safety issue): {error_msg}")

                # 에러 케이스는 결과에 포함하되, F1 계산에서 제외하기 위해 플래그 추가
                return {
                    'base_model': model,
                    'with_rag': False,
                    'agent_type': agent_type,
                    'test_id': test_case.get('test_id'),
                    'file_name': test_case.get('file_name') or Path(test_case.get('file_path', 'unknown')).name,
                    'response_time': 0,
                    'json_valid': False,
                    'true_positives': 0,
                    'false_positives': 0,
                    'false_negatives': 0,
                    'error': error_msg,  # 에러 플래그
                    'raw_response': {}
                }

            # 응답 파싱
            response_content = result.get('content', '')
            try:
                if '{' in response_content and '}' in response_content:
                    json_start = response_content.find('{')
                    json_end = response_content.rfind('}') + 1
                    json_text = response_content[json_start:json_end]
                    analysis_result = json.loads(json_text)
                else:
                    analysis_result = {}
            except json.JSONDecodeError:
                analysis_result = {}

            # Ground truth 로드
            test_id = test_case.get('test_id')
            ground_truth = self.test_manager.load_ground_truth(agent_type, test_id)

            # 응답을 표준 형식으로 변환
            standardized_response = {
                'valid_json': True,
                'analysis_results': analysis_result
            }

            # 메트릭 계산 - Ground truth와 실제 비교
            if ground_truth and 'expected_findings' in ground_truth:
                expected_algs = set()
                vulnerable_algs = ground_truth['expected_findings'].get('vulnerable_algorithms_detected', [])
                expected_algs = set([alg.lower() for alg in vulnerable_algs])

                # 탐지된 알고리즘 추출 (analysis_results에서)
                matched_expected = set()
                total_detected_count = 0
                if 'analysis_results' in analysis_result:
                    # analysis_results에서 "DETECTED:" 포함된 항목만 확인
                    analysis_results = analysis_result['analysis_results']
                    if isinstance(analysis_results, dict):
                        for key, value in analysis_results.items():
                            value_str = str(value).lower()
                            # "NOT DETECTED" 제외, "DETECTED:" 포함만
                            if 'detected:' in value_str and 'not detected' not in value_str:
                                total_detected_count += 1
                                # 예상 알고리즘과 매칭
                                for alg in expected_algs:
                                    # 알고리즘 변형도 고려 (ECC = ECDSA, ECDH 등)
                                    alg_variants = [alg]
                                    if alg == 'ecc':
                                        alg_variants.extend(['ecdsa', 'ecdh', 'elliptic'])
                                    elif alg == 'rsa':
                                        alg_variants.extend(['rsa'])
                                    elif alg == 'dsa':
                                        alg_variants.extend(['dsa'])
                                    elif alg == 'aes':
                                        alg_variants.extend(['aes'])
                                    elif alg == 'md5':
                                        alg_variants.extend(['md5'])

                                    if any(variant in value_str or variant in key.lower() for variant in alg_variants):
                                        matched_expected.add(alg)
                                        break

                # TP, FP, FN 계산
                true_positives = len(matched_expected)
                false_positives = total_detected_count - true_positives
                false_negatives = len(expected_algs) - true_positives

                # 개별 메트릭은 저장하지 않음 (전체 합산 후 계산)
                metrics = {
                    'true_positives': true_positives,
                    'false_positives': false_positives,
                    'false_negatives': false_negatives
                }
            else:
                metrics = {
                    'true_positives': 0,
                    'false_positives': 0,
                    'false_negatives': 0
                }

            return {
                'base_model': model,
                'with_rag': False,
                'agent_type': agent_type,
                'test_id': test_case.get('test_id'),
                'file_name': test_case.get('file_name') or Path(test_case.get('file_path', 'unknown')).name,
                'response_time': result.get('response_time', 0),
                'json_valid': result.get('json_valid', False),
                **metrics,
                'raw_response': analysis_result
            }

        except Exception as e:
            print(f"❌ 기본 모델 테스트 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_results(self, output_file: str = None):
        """결과 저장"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"rag_effect_comparison_{timestamp}.json"

        output_path = Path("results") / output_file
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'benchmark_info': {
                    'timestamp': datetime.now().isoformat(),
                    'test_models': self.test_models,
                    'pqc_base_url': self.pqc_base_url,
                    'ollama_base_url': self.ollama_base_url,
                    'total_tests': len(self.results)
                },
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 결과 저장됨: {output_path}")
        return output_path

    def print_summary(self):
        """결과 요약 출력 - RAG 효과 중심 (전체 TP/FP/FN 합산 방식)"""
        if not self.results:
            print("\n⚠️  결과 없음")
            return

        print("\n" + "=" * 80)
        print("📊 RAG 효과 측정 결과 요약")
        print("=" * 80)

        def calc_avg(results, key):
            vals = [r.get(key, 0) for r in results if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0

        def calc_metrics_from_sum(results):
            """전체 TP, FP, FN 합산 후 메트릭 계산 (에러 케이스 제외)"""
            # 'error' 플래그가 없는 케이스만 필터링
            valid_results = [r for r in results if 'error' not in r]

            total_tp = sum(r.get('true_positives', 0) for r in valid_results)
            total_fp = sum(r.get('false_positives', 0) for r in valid_results)
            total_fn = sum(r.get('false_negatives', 0) for r in valid_results)

            precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
            recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            return {
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'tp': total_tp,
                'fp': total_fp,
                'fn': total_fn,
                'valid_count': len(valid_results),
                'error_count': len(results) - len(valid_results)
            }

        # 모델별로 집계
        for model in self.test_models:
            print(f"\n🔬 모델: {model}")
            print("=" * 80)

            rag_results = [r for r in self.results if r['base_model'] == model and r['with_rag']]
            no_rag_results = [r for r in self.results if r['base_model'] == model and not r['with_rag']]

            # 전체 TP/FP/FN 합산 후 메트릭 계산
            rag_metrics = calc_metrics_from_sum(rag_results)
            no_rag_metrics = calc_metrics_from_sum(no_rag_results)

            improvement = ((rag_metrics['f1_score'] - no_rag_metrics['f1_score']) / no_rag_metrics['f1_score'] * 100) if no_rag_metrics['f1_score'] > 0 else 0

            print(f"\n📈 전체 결과 (TP/FP/FN 합산 방식, 에러 케이스 제외):")
            print(f"   RAG 포함:  F1={rag_metrics['f1_score']:.3f}, Precision={rag_metrics['precision']:.3f}, "
                  f"Recall={rag_metrics['recall']:.3f}, TP={rag_metrics['tp']}, FP={rag_metrics['fp']}, FN={rag_metrics['fn']}, "
                  f"시간={calc_avg(rag_results, 'response_time'):.2f}초 "
                  f"(성공: {rag_metrics['valid_count']}, 에러: {rag_metrics['error_count']})")
            print(f"   RAG 없음:  F1={no_rag_metrics['f1_score']:.3f}, Precision={no_rag_metrics['precision']:.3f}, "
                  f"Recall={no_rag_metrics['recall']:.3f}, TP={no_rag_metrics['tp']}, FP={no_rag_metrics['fp']}, FN={no_rag_metrics['fn']}, "
                  f"시간={calc_avg(no_rag_results, 'response_time'):.2f}초 "
                  f"(성공: {no_rag_metrics['valid_count']}, 에러: {no_rag_metrics['error_count']})")
            print(f"   🎯 RAG 효과: F1 Score {improvement:+.1f}% 향상")

            # 에이전트별 집계
            agent_types = set(r['agent_type'] for r in self.results if r['base_model'] == model)
            print(f"\n📋 에이전트별 RAG 효과:")
            for agent_type in sorted(agent_types):
                rag_agent = [r for r in rag_results if r['agent_type'] == agent_type]
                no_rag_agent = [r for r in no_rag_results if r['agent_type'] == agent_type]

                rag_agent_metrics = calc_metrics_from_sum(rag_agent)
                no_rag_agent_metrics = calc_metrics_from_sum(no_rag_agent)
                agent_improvement = ((rag_agent_metrics['f1_score'] - no_rag_agent_metrics['f1_score']) / no_rag_agent_metrics['f1_score'] * 100) if no_rag_agent_metrics['f1_score'] > 0 else 0

                print(f"   {agent_type:20s}: RAG F1={rag_agent_metrics['f1_score']:.3f} "
                      f"(TP={rag_agent_metrics['tp']}, FP={rag_agent_metrics['fp']}, FN={rag_agent_metrics['fn']}, 에러={rag_agent_metrics['error_count']}), "
                      f"순수 F1={no_rag_agent_metrics['f1_score']:.3f} "
                      f"(TP={no_rag_agent_metrics['tp']}, FP={no_rag_agent_metrics['fp']}, FN={no_rag_agent_metrics['fn']}, 에러={no_rag_agent_metrics['error_count']}), "
                      f"효과={agent_improvement:+.1f}%")

        print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="RAG 효과 측정 벤치마크: 같은 모델로 RAG 유무 비교"
    )
    parser.add_argument(
        '--models',
        nargs='+',
        default=['llama3:8b', 'gemini-2.0-flash-exp'],
        help='테스트할 모델 (기본: llama3:8b gemini-2.0-flash-exp)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='에이전트당 테스트 파일 수 제한'
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
    parser.add_argument(
        '--auto-restart',
        action='store_true',
        help='AI-Server 자동 재시작 (실험적)'
    )

    args = parser.parse_args()

    # 벤치마크 실행
    benchmark = RAGEffectBenchmark(
        pqc_base_url=args.pqc_url,
        ollama_base_url=args.ollama_url
    )

    benchmark.setup_test_models(args.models)

    benchmark.run_benchmark(
        limit_per_agent=args.limit,
        agent_filter=args.agents,
        auto_restart=args.auto_restart
    )

    # 결과 출력 및 저장
    benchmark.print_summary()
    benchmark.save_results(args.output)


if __name__ == "__main__":
    main()
