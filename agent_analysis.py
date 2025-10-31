import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_test_results(file_path):
    """Load test results from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_metrics(result):
    """Calculate precision, recall, and F1 score from results"""
    tp = result['true_positives']
    fp = result['false_positives']
    fn = result['false_negatives']

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn
    }

def analyze_by_agent(data, model_name):
    """Analyze results grouped by agent type"""
    results = data['results']

    # Group by agent_type and with_rag
    agent_stats = defaultdict(lambda: {'with_rag': [], 'without_rag': []})

    for result in results:
        agent_type = result.get('agent_type', 'unknown')
        metrics = calculate_metrics(result)
        metrics['response_time'] = result.get('response_time', 0)
        metrics['test_id'] = result.get('test_id', '')

        if result['with_rag']:
            agent_stats[agent_type]['with_rag'].append(metrics)
        else:
            agent_stats[agent_type]['without_rag'].append(metrics)

    # Calculate averages for each agent type
    agent_summary = {}
    for agent_type, data in agent_stats.items():
        with_rag_df = pd.DataFrame(data['with_rag'])
        without_rag_df = pd.DataFrame(data['without_rag'])

        agent_summary[agent_type] = {
            'with_rag': {
                'count': len(with_rag_df),
                'avg_precision': with_rag_df['precision'].mean() if len(with_rag_df) > 0 else 0,
                'avg_recall': with_rag_df['recall'].mean() if len(with_rag_df) > 0 else 0,
                'avg_f1': with_rag_df['f1_score'].mean() if len(with_rag_df) > 0 else 0,
                'avg_response_time': with_rag_df['response_time'].mean() if len(with_rag_df) > 0 else 0,
                'total_tp': with_rag_df['tp'].sum() if len(with_rag_df) > 0 else 0,
                'total_fp': with_rag_df['fp'].sum() if len(with_rag_df) > 0 else 0,
                'total_fn': with_rag_df['fn'].sum() if len(with_rag_df) > 0 else 0
            },
            'without_rag': {
                'count': len(without_rag_df),
                'avg_precision': without_rag_df['precision'].mean() if len(without_rag_df) > 0 else 0,
                'avg_recall': without_rag_df['recall'].mean() if len(without_rag_df) > 0 else 0,
                'avg_f1': without_rag_df['f1_score'].mean() if len(without_rag_df) > 0 else 0,
                'avg_response_time': without_rag_df['response_time'].mean() if len(without_rag_df) > 0 else 0,
                'total_tp': without_rag_df['tp'].sum() if len(without_rag_df) > 0 else 0,
                'total_fp': without_rag_df['fp'].sum() if len(without_rag_df) > 0 else 0,
                'total_fn': without_rag_df['fn'].sum() if len(without_rag_df) > 0 else 0
            }
        }

        # Calculate improvement
        with_f1 = agent_summary[agent_type]['with_rag']['avg_f1']
        without_f1 = agent_summary[agent_type]['without_rag']['avg_f1']
        agent_summary[agent_type]['f1_improvement'] = ((with_f1 - without_f1) / without_f1 * 100) if without_f1 > 0 else 0

    return agent_summary

def main():
    results_dir = Path('/Users/junsu/Projects/AI--Benchmark/results')

    models = {
        'GPT-4': 'gpt_test_3.json',
        'Gemini': 'gemini_test_3.json',
        'Llama': 'llama_test_3.json'
    }

    all_agent_analyses = {}

    print("=" * 80)
    print("Agent-Level RAG Impact Analysis (Test 3)")
    print("=" * 80)
    print()

    # Analyze each model
    for model_name, file_name in models.items():
        file_path = results_dir / file_name
        data = load_test_results(file_path)
        agent_summary = analyze_by_agent(data, model_name)
        all_agent_analyses[model_name] = agent_summary

        print(f"\n{'='*80}")
        print(f"{model_name} - Agent-Level Analysis")
        print(f"{'='*80}")

        for agent_type, stats in sorted(agent_summary.items()):
            print(f"\n{agent_type.upper().replace('_', ' ')}:")
            print(f"  Test Count: {stats['with_rag']['count']} (with RAG), {stats['without_rag']['count']} (without RAG)")

            print(f"\n  With RAG:")
            print(f"    Precision: {stats['with_rag']['avg_precision']:.4f}")
            print(f"    Recall:    {stats['with_rag']['avg_recall']:.4f}")
            print(f"    F1 Score:  {stats['with_rag']['avg_f1']:.4f}")
            print(f"    Avg Response Time: {stats['with_rag']['avg_response_time']:.2f}s")
            print(f"    Total: TP={stats['with_rag']['total_tp']}, FP={stats['with_rag']['total_fp']}, FN={stats['with_rag']['total_fn']}")

            print(f"\n  Without RAG:")
            print(f"    Precision: {stats['without_rag']['avg_precision']:.4f}")
            print(f"    Recall:    {stats['without_rag']['avg_recall']:.4f}")
            print(f"    F1 Score:  {stats['without_rag']['avg_f1']:.4f}")
            print(f"    Avg Response Time: {stats['without_rag']['avg_response_time']:.2f}s")
            print(f"    Total: TP={stats['without_rag']['total_tp']}, FP={stats['without_rag']['total_fp']}, FN={stats['without_rag']['total_fn']}")

            print(f"\n  RAG Impact: F1 {stats['f1_improvement']:+.2f}%")

    # Cross-model, cross-agent comparison
    print(f"\n{'='*80}")
    print("Cross-Model, Cross-Agent Comparison")
    print(f"{'='*80}")

    # Get all unique agent types
    all_agent_types = set()
    for model_analyses in all_agent_analyses.values():
        all_agent_types.update(model_analyses.keys())

    for agent_type in sorted(all_agent_types):
        print(f"\n{agent_type.upper().replace('_', ' ')}:")
        print(f"  {'Model':<12} {'F1 w/o RAG':<12} {'F1 w/ RAG':<12} {'Improvement':<15} {'Best Metric'}")
        print(f"  {'-'*70}")

        for model_name in models.keys():
            if agent_type in all_agent_analyses[model_name]:
                stats = all_agent_analyses[model_name][agent_type]
                f1_without = stats['without_rag']['avg_f1']
                f1_with = stats['with_rag']['avg_f1']
                improvement = stats['f1_improvement']

                # Determine what improved most
                prec_imp = ((stats['with_rag']['avg_precision'] - stats['without_rag']['avg_precision']) /
                           stats['without_rag']['avg_precision'] * 100) if stats['without_rag']['avg_precision'] > 0 else 0
                rec_imp = ((stats['with_rag']['avg_recall'] - stats['without_rag']['avg_recall']) /
                          stats['without_rag']['avg_recall'] * 100) if stats['without_rag']['avg_recall'] > 0 else 0

                if abs(prec_imp) > abs(rec_imp):
                    best_metric = f"Precision ({prec_imp:+.1f}%)"
                else:
                    best_metric = f"Recall ({rec_imp:+.1f}%)"

                print(f"  {model_name:<12} {f1_without:<12.4f} {f1_with:<12.4f} {improvement:>+6.2f}%{'':<8} {best_metric}")
            else:
                print(f"  {model_name:<12} {'N/A':<12} {'N/A':<12} {'N/A':<15} {'N/A'}")

    # Key insights by agent type
    print(f"\n{'='*80}")
    print("Key Insights by Agent Type")
    print(f"{'='*80}")

    for agent_type in sorted(all_agent_types):
        print(f"\n{agent_type.upper().replace('_', ' ')}:")

        improvements = []
        for model_name in models.keys():
            if agent_type in all_agent_analyses[model_name]:
                improvement = all_agent_analyses[model_name][agent_type]['f1_improvement']
                improvements.append((model_name, improvement))

        if improvements:
            improvements.sort(key=lambda x: x[1], reverse=True)
            best_model = improvements[0]
            worst_model = improvements[-1]

            print(f"  Best performing model: {best_model[0]} ({best_model[1]:+.2f}% F1)")
            print(f"  Worst performing model: {worst_model[0]} ({worst_model[1]:+.2f}% F1)")

            avg_improvement = sum(imp for _, imp in improvements) / len(improvements)
            print(f"  Average RAG impact: {avg_improvement:+.2f}% F1")

            if avg_improvement > 20:
                print(f"  → This agent type benefits SIGNIFICANTLY from RAG across all models")
            elif avg_improvement > 5:
                print(f"  → This agent type shows MODERATE benefit from RAG")
            elif avg_improvement > -5:
                print(f"  → RAG has MIXED effects on this agent type")
            else:
                print(f"  → RAG DEGRADES performance for this agent type")

if __name__ == '__main__':
    main()
