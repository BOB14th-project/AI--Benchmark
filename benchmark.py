import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from config.config_loader import ConfigLoader
from clients.client_factory import ClientFactory
from agents.agent_factory import AgentFactory
from utils.test_case_manager import TestCaseManager
from utils.metrics_calculator import MetricsCalculator

class LLMAnalysisBenchmark:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = ConfigLoader(config_path)
        self.test_manager = TestCaseManager(
            self.config.get_paths_config()['test_cases'],
            self.config.get_paths_config()['ground_truth']
        )
        self.metrics_calculator = MetricsCalculator()

        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('benchmark.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_benchmark(self,
                     providers: Optional[List[str]] = None,
                     agents: Optional[List[str]] = None,
                     max_workers: int = 4) -> Dict[str, Any]:

        if providers is None:
            providers = self.config.get_all_llm_providers()
        if agents is None:
            agents = self.config.get_all_agents()

        self.logger.info(f"Starting benchmark with providers: {providers}, agents: {agents}")

        all_results = {}

        for provider in providers:
            provider_config = self.config.get_llm_config(provider)
            if not provider_config.get('api_key') or provider_config['api_key'].startswith('your_'):
                self.logger.warning(f"Skipping {provider}: API key not configured")
                continue

            try:
                client = ClientFactory.create_client(provider, provider_config)
                provider_results = self._benchmark_provider(client, provider, agents, max_workers)
                all_results[provider] = provider_results
            except Exception as e:
                self.logger.error(f"Error benchmarking provider {provider}: {e}")
                all_results[provider] = {'error': str(e)}

        return all_results

    def _benchmark_provider(self, client, provider: str, agents: List[str], max_workers: int) -> Dict[str, Any]:
        provider_results = {'agents': {}, 'summary': {}}

        for agent_type in agents:
            self.logger.info(f"Benchmarking {provider} with {agent_type} agent")

            try:
                agent_config = self.config.get_agent_config(agent_type)
                agent = AgentFactory.create_agent(agent_type, agent_config)

                test_cases = self.test_manager.load_test_cases(agent_type)
                if not test_cases:
                    self.logger.warning(f"No test cases found for agent {agent_type}")
                    continue

                agent_results = self._run_agent_tests(client, agent, test_cases, max_workers)
                provider_results['agents'][agent_type] = agent_results

            except Exception as e:
                self.logger.error(f"Error benchmarking agent {agent_type}: {e}")
                provider_results['agents'][agent_type] = {'error': str(e)}

        provider_results['summary'] = self._calculate_provider_summary(provider_results['agents'])
        return provider_results

    def _run_agent_tests(self, client, agent, test_cases: List[Dict], max_workers: int) -> Dict[str, Any]:
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_test = {}

            for test_case in test_cases:
                future = executor.submit(self._run_single_test, client, agent, test_case)
                future_to_test[future] = test_case

            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.get(timeout=self.config.get_benchmark_config().get('timeout_seconds', 30))
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Test failed for {test_case.get('test_id', 'unknown')}: {e}")
                    results.append({
                        'test_id': test_case.get('test_id', 'unknown'),
                        'success': False,
                        'error': str(e),
                        'accuracy_score': 0.0,
                        'response_time': 0.0,
                        'json_stability_score': 0.0,
                        'completeness_score': 0.0
                    })

        aggregate_metrics = self.metrics_calculator.aggregate_metrics(results)

        return {
            'individual_results': results,
            'aggregate_metrics': aggregate_metrics,
            'total_tests': len(test_cases)
        }

    def _run_single_test(self, client, agent, test_case: Dict[str, Any]) -> Dict[str, Any]:
        test_id = test_case.get('test_id', 'unknown')

        if not agent.validate_input(test_case['input_data']):
            return {
                'test_id': test_id,
                'success': False,
                'error': 'Invalid input data for agent',
                'accuracy_score': 0.0,
                'response_time': 0.0,
                'json_stability_score': 0.0,
                'completeness_score': 0.0
            }

        prompt = agent.create_prompt(test_case['input_data'])

        llm_response = client.benchmark_request(prompt)

        if not llm_response['success']:
            return {
                'test_id': test_id,
                'success': False,
                'error': llm_response['error'],
                'accuracy_score': 0.0,
                'response_time': llm_response['response_time'],
                'json_stability_score': 0.0,
                'completeness_score': 0.0
            }

        agent_analysis = agent.extract_key_findings(llm_response['content'])

        ground_truth = self.test_manager.load_ground_truth(agent.__class__.__name__.replace('Agent', '').lower(), test_id)

        accuracy_score = 0.0
        if ground_truth:
            accuracy_score = self.metrics_calculator.calculate_accuracy(agent_analysis, ground_truth)

        json_stability_score = self.metrics_calculator.calculate_json_stability_score(agent_analysis)

        completeness_score = self.metrics_calculator.calculate_completeness_score(
            agent_analysis,
            test_case.get('expected_analysis_points', agent.get_analysis_points())
        )

        return {
            'test_id': test_id,
            'success': True,
            'accuracy_score': accuracy_score,
            'response_time': llm_response['response_time'],
            'json_stability_score': json_stability_score,
            'completeness_score': completeness_score,
            'agent_analysis': agent_analysis,
            'raw_response': llm_response['content'],
            'model': llm_response['model']
        }

    def _calculate_provider_summary(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        all_metrics = []

        for agent_type, results in agent_results.items():
            if 'error' not in results and 'aggregate_metrics' in results:
                all_metrics.append(results['aggregate_metrics'])

        if not all_metrics:
            return {}

        total_tests = sum(m.get('total_tests', 0) for m in all_metrics)
        successful_tests = sum(m.get('successful_tests', 0) for m in all_metrics)

        avg_accuracy = sum(m.get('average_accuracy', 0) for m in all_metrics) / len(all_metrics)
        avg_response_time = sum(m.get('average_response_time', 0) for m in all_metrics) / len(all_metrics)
        avg_json_stability = sum(m.get('average_json_stability', 0) for m in all_metrics) / len(all_metrics)
        avg_completeness = sum(m.get('average_completeness', 0) for m in all_metrics) / len(all_metrics)

        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'overall_success_rate': successful_tests / total_tests if total_tests > 0 else 0.0,
            'overall_accuracy': avg_accuracy,
            'overall_response_time': avg_response_time,
            'overall_json_stability': avg_json_stability,
            'overall_completeness': avg_completeness,
            'agent_count': len([r for r in agent_results.values() if 'error' not in r])
        }

    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        results_dir = Path(self.config.get_paths_config()['results'])
        results_dir.mkdir(exist_ok=True)

        output_path = results_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Results saved to {output_path}")
        return str(output_path)