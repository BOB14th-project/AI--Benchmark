import json
import pandas as pd
import numpy as np
from pathlib import Path

def load_test_results(file_path):
    """Load test results from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_metrics(results):
    """Calculate precision, recall, and F1 score from results"""
    tp = results['true_positives']
    fp = results['false_positives']
    fn = results['false_negatives']

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

def analyze_rag_impact(data, model_name):
    """Analyze RAG impact for a specific model"""
    results = data['results']

    with_rag = []
    without_rag = []

    for result in results:
        metrics = calculate_metrics(result)
        metrics['test_id'] = result['test_id']
        metrics['response_time'] = result.get('response_time', 0)

        if result['with_rag']:
            with_rag.append(metrics)
        else:
            without_rag.append(metrics)

    df_with_rag = pd.DataFrame(with_rag)
    df_without_rag = pd.DataFrame(without_rag)

    # Calculate average metrics
    avg_with_rag = {
        'precision': df_with_rag['precision'].mean(),
        'recall': df_with_rag['recall'].mean(),
        'f1_score': df_with_rag['f1_score'].mean(),
        'avg_response_time': df_with_rag['response_time'].mean(),
        'total_tp': df_with_rag['true_positives'].sum(),
        'total_fp': df_with_rag['false_positives'].sum(),
        'total_fn': df_with_rag['false_negatives'].sum()
    }

    avg_without_rag = {
        'precision': df_without_rag['precision'].mean(),
        'recall': df_without_rag['recall'].mean(),
        'f1_score': df_without_rag['f1_score'].mean(),
        'avg_response_time': df_without_rag['response_time'].mean(),
        'total_tp': df_without_rag['true_positives'].sum(),
        'total_fp': df_without_rag['false_positives'].sum(),
        'total_fn': df_without_rag['false_negatives'].sum()
    }

    # Calculate improvement
    improvement = {
        'precision_improvement': ((avg_with_rag['precision'] - avg_without_rag['precision']) / avg_without_rag['precision'] * 100) if avg_without_rag['precision'] > 0 else 0,
        'recall_improvement': ((avg_with_rag['recall'] - avg_without_rag['recall']) / avg_without_rag['recall'] * 100) if avg_without_rag['recall'] > 0 else 0,
        'f1_improvement': ((avg_with_rag['f1_score'] - avg_without_rag['f1_score']) / avg_without_rag['f1_score'] * 100) if avg_without_rag['f1_score'] > 0 else 0
    }

    return {
        'model': model_name,
        'with_rag': avg_with_rag,
        'without_rag': avg_without_rag,
        'improvement': improvement,
        'detailed_with_rag': df_with_rag,
        'detailed_without_rag': df_without_rag
    }

def compare_rag_effectiveness(results_dict):
    """Compare RAG effectiveness across models"""
    comparison = []

    for model, analysis in results_dict.items():
        comparison.append({
            'model': model,
            'f1_with_rag': analysis['with_rag']['f1_score'],
            'f1_without_rag': analysis['without_rag']['f1_score'],
            'f1_improvement': analysis['improvement']['f1_improvement'],
            'precision_with_rag': analysis['with_rag']['precision'],
            'precision_without_rag': analysis['without_rag']['precision'],
            'precision_improvement': analysis['improvement']['precision_improvement'],
            'recall_with_rag': analysis['with_rag']['recall'],
            'recall_without_rag': analysis['without_rag']['recall'],
            'recall_improvement': analysis['improvement']['recall_improvement'],
            'avg_response_time_with_rag': analysis['with_rag']['avg_response_time'],
            'avg_response_time_without_rag': analysis['without_rag']['avg_response_time']
        })

    return pd.DataFrame(comparison)

def find_performance_patterns(results_dict):
    """Find patterns in performance differences"""
    patterns = {}

    for model, analysis in results_dict.items():
        df_with = analysis['detailed_with_rag']
        df_without = analysis['detailed_without_rag']

        # Merge on test_id
        merged = pd.merge(df_with, df_without, on='test_id', suffixes=('_with_rag', '_without_rag'))

        # Calculate per-test improvement
        merged['f1_diff'] = merged['f1_score_with_rag'] - merged['f1_score_without_rag']
        merged['precision_diff'] = merged['precision_with_rag'] - merged['precision_without_rag']
        merged['recall_diff'] = merged['recall_with_rag'] - merged['recall_without_rag']

        # Find tests where RAG helped most
        helped_most = merged.nlargest(5, 'f1_diff')[['test_id', 'f1_diff', 'precision_diff', 'recall_diff']]

        # Find tests where RAG hurt performance
        hurt_most = merged.nsmallest(5, 'f1_diff')[['test_id', 'f1_diff', 'precision_diff', 'recall_diff']]

        # Count improvements vs degradations
        improved = (merged['f1_diff'] > 0).sum()
        degraded = (merged['f1_diff'] < 0).sum()
        unchanged = (merged['f1_diff'] == 0).sum()

        patterns[model] = {
            'helped_most': helped_most,
            'hurt_most': hurt_most,
            'improved_count': improved,
            'degraded_count': degraded,
            'unchanged_count': unchanged,
            'total_tests': len(merged)
        }

    return patterns

def main():
    results_dir = Path('/Users/junsu/Projects/AI--Benchmark/results')

    # Load test_3 results
    models = {
        'GPT-4': 'gpt_test_3.json',
        'Gemini': 'gemini_test_3.json',
        'Llama': 'llama_test_3.json'
    }

    results_dict = {}

    print("=" * 80)
    print("Test 3 RAG Impact Analysis")
    print("=" * 80)
    print()

    for model_name, file_name in models.items():
        file_path = results_dir / file_name
        data = load_test_results(file_path)
        analysis = analyze_rag_impact(data, model_name)
        results_dict[model_name] = analysis

        print(f"\n{'='*80}")
        print(f"{model_name} Analysis")
        print(f"{'='*80}")
        print(f"\nWith RAG:")
        print(f"  Precision: {analysis['with_rag']['precision']:.4f}")
        print(f"  Recall:    {analysis['with_rag']['recall']:.4f}")
        print(f"  F1 Score:  {analysis['with_rag']['f1_score']:.4f}")
        print(f"  Avg Response Time: {analysis['with_rag']['avg_response_time']:.2f}s")
        print(f"  Total TP: {analysis['with_rag']['total_tp']}, FP: {analysis['with_rag']['total_fp']}, FN: {analysis['with_rag']['total_fn']}")

        print(f"\nWithout RAG:")
        print(f"  Precision: {analysis['without_rag']['precision']:.4f}")
        print(f"  Recall:    {analysis['without_rag']['recall']:.4f}")
        print(f"  F1 Score:  {analysis['without_rag']['f1_score']:.4f}")
        print(f"  Avg Response Time: {analysis['without_rag']['avg_response_time']:.2f}s")
        print(f"  Total TP: {analysis['without_rag']['total_tp']}, FP: {analysis['without_rag']['total_fp']}, FN: {analysis['without_rag']['total_fn']}")

        print(f"\nImprovement:")
        print(f"  Precision: {analysis['improvement']['precision_improvement']:+.2f}%")
        print(f"  Recall:    {analysis['improvement']['recall_improvement']:+.2f}%")
        print(f"  F1 Score:  {analysis['improvement']['f1_improvement']:+.2f}%")

    # Cross-model comparison
    print(f"\n{'='*80}")
    print("Cross-Model RAG Effectiveness Comparison")
    print(f"{'='*80}")
    comparison_df = compare_rag_effectiveness(results_dict)
    print("\n", comparison_df.to_string(index=False))

    # Performance patterns
    print(f"\n{'='*80}")
    print("Performance Patterns Analysis")
    print(f"{'='*80}")
    patterns = find_performance_patterns(results_dict)

    for model, pattern in patterns.items():
        print(f"\n{model}:")
        print(f"  Tests improved by RAG: {pattern['improved_count']}/{pattern['total_tests']} ({pattern['improved_count']/pattern['total_tests']*100:.1f}%)")
        print(f"  Tests degraded by RAG: {pattern['degraded_count']}/{pattern['total_tests']} ({pattern['degraded_count']/pattern['total_tests']*100:.1f}%)")
        print(f"  Tests unchanged: {pattern['unchanged_count']}/{pattern['total_tests']}")

        print(f"\n  Top 5 tests where RAG helped most:")
        for idx, row in pattern['helped_most'].iterrows():
            print(f"    - {row['test_id']}: F1 +{row['f1_diff']:.4f}")

        print(f"\n  Top 5 tests where RAG hurt performance:")
        for idx, row in pattern['hurt_most'].iterrows():
            print(f"    - {row['test_id']}: F1 {row['f1_diff']:.4f}")

    # Key insights
    print(f"\n{'='*80}")
    print("Key Insights")
    print(f"{'='*80}")

    # Which model benefited most from RAG?
    best_improvement = comparison_df.loc[comparison_df['f1_improvement'].idxmax()]
    worst_improvement = comparison_df.loc[comparison_df['f1_improvement'].idxmin()]

    print(f"\nRAG Effectiveness by Model:")
    print(f"  Most improved by RAG: {best_improvement['model']} ({best_improvement['f1_improvement']:+.2f}% F1)")
    print(f"  Least improved by RAG: {worst_improvement['model']} ({worst_improvement['f1_improvement']:+.2f}% F1)")

    # Analyze why different models respond differently to RAG
    print(f"\nPossible Reasons for Different RAG Effects:")
    print()

    for model in results_dict.keys():
        with_rag_f1 = results_dict[model]['with_rag']['f1_score']
        without_rag_f1 = results_dict[model]['without_rag']['f1_score']
        improvement = results_dict[model]['improvement']['f1_improvement']

        # Check baseline performance
        if without_rag_f1 > 0.7:
            print(f"  {model}: High baseline performance (F1={without_rag_f1:.4f}) may limit RAG benefit")
        elif without_rag_f1 < 0.5:
            print(f"  {model}: Low baseline performance (F1={without_rag_f1:.4f}) shows room for RAG improvement")

        # Check precision vs recall trade-off
        precision_imp = results_dict[model]['improvement']['precision_improvement']
        recall_imp = results_dict[model]['improvement']['recall_improvement']

        if abs(precision_imp) > abs(recall_imp) * 2:
            print(f"  {model}: RAG primarily affects precision ({precision_imp:+.2f}% vs recall {recall_imp:+.2f}%)")
        elif abs(recall_imp) > abs(precision_imp) * 2:
            print(f"  {model}: RAG primarily affects recall ({recall_imp:+.2f}% vs precision {precision_imp:+.2f}%)")

        # Check consistency
        pattern = patterns[model]
        consistency_ratio = pattern['improved_count'] / pattern['total_tests']
        if consistency_ratio > 0.7:
            print(f"  {model}: RAG helps consistently across {consistency_ratio*100:.1f}% of tests")
        elif consistency_ratio < 0.5:
            print(f"  {model}: RAG effect is inconsistent (helps in only {consistency_ratio*100:.1f}% of tests)")

if __name__ == '__main__':
    main()
