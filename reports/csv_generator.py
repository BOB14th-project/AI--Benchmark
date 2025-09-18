import csv
import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

class CSVReportGenerator:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def generate_summary_report(self, benchmark_results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_summary_{timestamp}.csv"

        output_path = self.results_dir / filename

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([
                'Provider',
                'Total Tests',
                'Successful Tests',
                'Success Rate (%)',
                'Avg Accuracy',
                'Avg Response Time (s)',
                'Avg JSON Stability',
                'Avg Completeness',
                'Agent Count'
            ])

            for provider, results in benchmark_results.items():
                if 'error' in results:
                    writer.writerow([
                        provider,
                        'ERROR',
                        results['error'],
                        '', '', '', '', '', ''
                    ])
                    continue

                summary = results.get('summary', {})
                writer.writerow([
                    provider,
                    summary.get('total_tests', 0),
                    summary.get('successful_tests', 0),
                    f"{summary.get('overall_success_rate', 0) * 100:.1f}",
                    f"{summary.get('overall_accuracy', 0):.3f}",
                    f"{summary.get('overall_response_time', 0):.3f}",
                    f"{summary.get('overall_json_stability', 0):.3f}",
                    f"{summary.get('overall_completeness', 0):.3f}",
                    summary.get('agent_count', 0)
                ])

        return str(output_path)

    def generate_detailed_report(self, benchmark_results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_detailed_{timestamp}.csv"

        output_path = self.results_dir / filename

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([
                'Provider',
                'Agent Type',
                'Test ID',
                'Success',
                'Accuracy Score',
                'Response Time (s)',
                'JSON Stability',
                'Completeness',
                'Model',
                'Error'
            ])

            for provider, provider_results in benchmark_results.items():
                if 'error' in provider_results:
                    writer.writerow([
                        provider,
                        'N/A',
                        'N/A',
                        'False',
                        '0',
                        '0',
                        '0',
                        '0',
                        'N/A',
                        provider_results['error']
                    ])
                    continue

                agent_results = provider_results.get('agents', {})
                for agent_type, agent_data in agent_results.items():
                    if 'error' in agent_data:
                        writer.writerow([
                            provider,
                            agent_type,
                            'N/A',
                            'False',
                            '0',
                            '0',
                            '0',
                            '0',
                            'N/A',
                            agent_data['error']
                        ])
                        continue

                    individual_results = agent_data.get('individual_results', [])
                    for result in individual_results:
                        writer.writerow([
                            provider,
                            agent_type,
                            result.get('test_id', 'unknown'),
                            result.get('success', False),
                            f"{result.get('accuracy_score', 0):.3f}",
                            f"{result.get('response_time', 0):.3f}",
                            f"{result.get('json_stability_score', 0):.3f}",
                            f"{result.get('completeness_score', 0):.3f}",
                            result.get('model', 'unknown'),
                            result.get('error', '')
                        ])

        return str(output_path)

    def generate_agent_comparison_report(self, benchmark_results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_comparison_{timestamp}.csv"

        output_path = self.results_dir / filename

        agents = set()
        for provider_results in benchmark_results.values():
            if 'agents' in provider_results:
                agents.update(provider_results['agents'].keys())

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            header = ['Agent Type', 'Metric']
            providers = list(benchmark_results.keys())
            header.extend(providers)
            writer.writerow(header)

            for agent in sorted(agents):
                metrics = ['Avg Accuracy', 'Avg Response Time', 'Avg JSON Stability', 'Avg Completeness', 'Success Rate']

                for metric in metrics:
                    row = [agent, metric]

                    for provider in providers:
                        provider_results = benchmark_results[provider]
                        if 'error' in provider_results:
                            row.append('ERROR')
                            continue

                        agent_data = provider_results.get('agents', {}).get(agent, {})
                        if 'error' in agent_data:
                            row.append('ERROR')
                            continue

                        aggregate = agent_data.get('aggregate_metrics', {})

                        if metric == 'Avg Accuracy':
                            value = aggregate.get('average_accuracy', 0)
                        elif metric == 'Avg Response Time':
                            value = aggregate.get('average_response_time', 0)
                        elif metric == 'Avg JSON Stability':
                            value = aggregate.get('average_json_stability', 0)
                        elif metric == 'Avg Completeness':
                            value = aggregate.get('average_completeness', 0)
                        elif metric == 'Success Rate':
                            value = aggregate.get('success_rate', 0)
                        else:
                            value = 0

                        if metric == 'Success Rate':
                            row.append(f"{value * 100:.1f}%")
                        else:
                            row.append(f"{value:.3f}")

                    writer.writerow(row)

        return str(output_path)

    def generate_performance_matrix(self, benchmark_results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_matrix_{timestamp}.csv"

        output_path = self.results_dir / filename

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(['Performance Matrix - Overall Scores'])
            writer.writerow([])

            writer.writerow(['Provider', 'Overall Score', 'Accuracy Rank', 'Speed Rank', 'Stability Rank', 'Completeness Rank'])

            provider_scores = []

            for provider, provider_results in benchmark_results.items():
                if 'error' in provider_results:
                    continue

                summary = provider_results.get('summary', {})
                overall_score = (
                    summary.get('overall_accuracy', 0) * 0.3 +
                    (1 - min(summary.get('overall_response_time', 10), 10) / 10) * 0.2 +
                    summary.get('overall_json_stability', 0) * 0.25 +
                    summary.get('overall_completeness', 0) * 0.25
                )

                provider_scores.append({
                    'provider': provider,
                    'overall_score': overall_score,
                    'accuracy': summary.get('overall_accuracy', 0),
                    'response_time': summary.get('overall_response_time', 0),
                    'json_stability': summary.get('overall_json_stability', 0),
                    'completeness': summary.get('overall_completeness', 0)
                })

            provider_scores.sort(key=lambda x: x['overall_score'], reverse=True)

            accuracy_ranks = sorted(provider_scores, key=lambda x: x['accuracy'], reverse=True)
            speed_ranks = sorted(provider_scores, key=lambda x: x['response_time'])
            stability_ranks = sorted(provider_scores, key=lambda x: x['json_stability'], reverse=True)
            completeness_ranks = sorted(provider_scores, key=lambda x: x['completeness'], reverse=True)

            def get_rank(provider, rank_list):
                for i, item in enumerate(rank_list):
                    if item['provider'] == provider:
                        return i + 1
                return len(rank_list)

            for score_data in provider_scores:
                provider = score_data['provider']
                writer.writerow([
                    provider,
                    f"{score_data['overall_score']:.3f}",
                    get_rank(provider, accuracy_ranks),
                    get_rank(provider, speed_ranks),
                    get_rank(provider, stability_ranks),
                    get_rank(provider, completeness_ranks)
                ])

        return str(output_path)

    def generate_all_reports(self, benchmark_results: Dict[str, Any]) -> List[str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        reports = []
        reports.append(self.generate_summary_report(benchmark_results, f"summary_{timestamp}.csv"))
        reports.append(self.generate_detailed_report(benchmark_results, f"detailed_{timestamp}.csv"))
        reports.append(self.generate_agent_comparison_report(benchmark_results, f"agent_comparison_{timestamp}.csv"))
        reports.append(self.generate_performance_matrix(benchmark_results, f"performance_matrix_{timestamp}.csv"))

        return reports