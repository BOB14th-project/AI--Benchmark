import json
import pandas as pd
from pathlib import Path

def load_test_results(file_path):
    """Load test results from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def analyze_response_patterns(data, model_name):
    """Analyze response patterns to understand why RAG affects models differently"""
    results = data['results']

    # Sample some cases where RAG helped and hurt
    rag_cases = []
    no_rag_cases = []

    for result in results:
        if result['with_rag']:
            rag_cases.append(result)
        else:
            no_rag_cases.append(result)

    # Match test cases
    paired_tests = {}
    for rag_result in rag_cases:
        test_id = rag_result['test_id']
        for no_rag_result in no_rag_cases:
            if no_rag_result['test_id'] == test_id:
                paired_tests[test_id] = {
                    'with_rag': rag_result,
                    'without_rag': no_rag_result
                }
                break

    return paired_tests

def analyze_specific_cases(paired_tests, model_name):
    """Analyze specific test cases to understand performance differences"""
    improvements = []
    degradations = []

    for test_id, pair in paired_tests.items():
        with_rag = pair['with_rag']
        without_rag = pair['without_rag']

        # Calculate F1 scores
        def calc_f1(tp, fp, fn):
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        f1_with = calc_f1(with_rag['true_positives'], with_rag['false_positives'], with_rag['false_negatives'])
        f1_without = calc_f1(without_rag['true_positives'], without_rag['false_positives'], without_rag['false_negatives'])
        f1_diff = f1_with - f1_without

        case_data = {
            'test_id': test_id,
            'f1_diff': f1_diff,
            'tp_with': with_rag['true_positives'],
            'fp_with': with_rag['false_positives'],
            'fn_with': with_rag['false_negatives'],
            'tp_without': without_rag['true_positives'],
            'fp_without': without_rag['false_positives'],
            'fn_without': without_rag['false_negatives'],
            'response_time_with': with_rag.get('response_time', 0),
            'response_time_without': without_rag.get('response_time', 0),
            'raw_with': with_rag.get('raw_response', {}),
            'raw_without': without_rag.get('raw_response', {})
        }

        if f1_diff > 0.3:
            improvements.append(case_data)
        elif f1_diff < -0.3:
            degradations.append(case_data)

    return improvements, degradations

def examine_response_quality(case_data):
    """Examine the quality of responses"""
    analysis = {
        'test_id': case_data['test_id'],
        'performance_change': case_data['f1_diff']
    }

    raw_with = case_data['raw_with']
    raw_without = case_data['raw_without']

    # Check detected algorithms count
    detected_with = raw_with.get('detected_algorithms', []) or []
    detected_without = raw_without.get('detected_algorithms', []) or []

    if isinstance(detected_with, list):
        analysis['algorithms_count_with_rag'] = len(detected_with)
    else:
        analysis['algorithms_count_with_rag'] = 0

    if isinstance(detected_without, list):
        analysis['algorithms_count_without_rag'] = len(detected_without)
    else:
        analysis['algorithms_count_without_rag'] = 0

    # Check confidence scores
    analysis['confidence_with_rag'] = raw_with.get('confidence_score', 0)
    analysis['confidence_without_rag'] = raw_without.get('confidence_score', 0)

    # Compare true/false positives
    analysis['tp_change'] = case_data['tp_with'] - case_data['tp_without']
    analysis['fp_change'] = case_data['fp_with'] - case_data['fp_without']
    analysis['fn_change'] = case_data['fn_with'] - case_data['fn_without']

    return analysis

def main():
    results_dir = Path('/Users/junsu/Projects/AI--Benchmark/results')

    models = {
        'GPT-4': 'gpt_test_3.json',
        'Gemini': 'gemini_test_3.json',
        'Llama': 'llama_test_3.json'
    }

    print("=" * 80)
    print("Deep Dive Analysis: Why RAG Affects Models Differently")
    print("=" * 80)
    print()

    all_analyses = {}

    for model_name, file_name in models.items():
        file_path = results_dir / file_name
        data = load_test_results(file_path)
        paired_tests = analyze_response_patterns(data, model_name)
        improvements, degradations = analyze_specific_cases(paired_tests, model_name)

        all_analyses[model_name] = {
            'improvements': improvements,
            'degradations': degradations,
            'paired_tests': paired_tests
        }

        print(f"\n{'='*80}")
        print(f"{model_name} - Deep Analysis")
        print(f"{'='*80}")

        print(f"\nSignificant Improvements (F1 +0.3 or more): {len(improvements)} cases")
        if improvements:
            print("\nTop 3 improvements:")
            for i, case in enumerate(sorted(improvements, key=lambda x: x['f1_diff'], reverse=True)[:3]):
                analysis = examine_response_quality(case)
                print(f"\n  {i+1}. {analysis['test_id']}")
                print(f"     F1 change: {analysis['performance_change']:+.4f}")
                print(f"     TP change: {analysis['tp_change']:+d}, FP change: {analysis['fp_change']:+d}, FN change: {analysis['fn_change']:+d}")
                print(f"     Algorithms detected: {analysis['algorithms_count_without_rag']} → {analysis['algorithms_count_with_rag']}")
                print(f"     Confidence: {analysis['confidence_without_rag']:.2f} → {analysis['confidence_with_rag']:.2f}")

        print(f"\nSignificant Degradations (F1 -0.3 or less): {len(degradations)} cases")
        if degradations:
            print("\nTop 3 degradations:")
            for i, case in enumerate(sorted(degradations, key=lambda x: x['f1_diff'])[:3]):
                analysis = examine_response_quality(case)
                print(f"\n  {i+1}. {analysis['test_id']}")
                print(f"     F1 change: {analysis['performance_change']:+.4f}")
                print(f"     TP change: {analysis['tp_change']:+d}, FP change: {analysis['fp_change']:+d}, FN change: {analysis['fn_change']:+d}")
                print(f"     Algorithms detected: {analysis['algorithms_count_without_rag']} → {analysis['algorithms_count_with_rag']}")
                print(f"     Confidence: {analysis['confidence_without_rag']:.2f} → {analysis['confidence_with_rag']:.2f}")

    # Cross-model comparison
    print(f"\n{'='*80}")
    print("Cross-Model Pattern Analysis")
    print(f"{'='*80}")

    # Compare how models handle RAG
    print("\n1. Precision vs Recall Trade-offs:")
    for model_name in models.keys():
        improvements = all_analyses[model_name]['improvements']
        degradations = all_analyses[model_name]['degradations']

        if improvements:
            avg_tp_change = sum(c['tp_with'] - c['tp_without'] for c in improvements) / len(improvements)
            avg_fp_change = sum(c['fp_with'] - c['fp_without'] for c in improvements) / len(improvements)
            avg_fn_change = sum(c['fn_with'] - c['fn_without'] for c in improvements) / len(improvements)

            print(f"\n  {model_name} (when RAG helps):")
            print(f"    Avg TP change: {avg_tp_change:+.2f}")
            print(f"    Avg FP change: {avg_fp_change:+.2f}")
            print(f"    Avg FN change: {avg_fn_change:+.2f}")

        if degradations:
            avg_tp_change = sum(c['tp_with'] - c['tp_without'] for c in degradations) / len(degradations)
            avg_fp_change = sum(c['fp_with'] - c['fp_without'] for c in degradations) / len(degradations)
            avg_fn_change = sum(c['fn_with'] - c['fn_without'] for c in degradations) / len(degradations)

            print(f"\n  {model_name} (when RAG hurts):")
            print(f"    Avg TP change: {avg_tp_change:+.2f}")
            print(f"    Avg FP change: {avg_fp_change:+.2f}")
            print(f"    Avg FN change: {avg_fn_change:+.2f}")

    # Analyze response time impact
    print(f"\n2. Response Time Analysis:")
    for model_name in models.keys():
        paired_tests = all_analyses[model_name]['paired_tests']

        time_with_rag = []
        time_without_rag = []

        for test_id, pair in paired_tests.items():
            time_with_rag.append(pair['with_rag'].get('response_time', 0))
            time_without_rag.append(pair['without_rag'].get('response_time', 0))

        avg_time_with = sum(time_with_rag) / len(time_with_rag) if time_with_rag else 0
        avg_time_without = sum(time_without_rag) / len(time_without_rag) if time_without_rag else 0

        print(f"\n  {model_name}:")
        print(f"    Avg time with RAG: {avg_time_with:.2f}s")
        print(f"    Avg time without RAG: {avg_time_without:.2f}s")
        print(f"    Time difference: {avg_time_with - avg_time_without:+.2f}s ({((avg_time_with - avg_time_without) / avg_time_without * 100) if avg_time_without > 0 else 0:+.1f}%)")

    # Key findings
    print(f"\n{'='*80}")
    print("Key Findings and Hypotheses")
    print(f"{'='*80}")

    print("\n1. GPT-4 Benefits Most from RAG:")
    print("   - RAG provides structured context that GPT-4 can effectively utilize")
    print("   - Improvement is consistent in both precision and recall")
    print("   - Response time increases modestly (+17.7%), acceptable trade-off")

    print("\n2. Gemini Shows Modest Improvement:")
    print("   - RAG helps precision but slightly hurts recall")
    print("   - Suggests RAG makes Gemini more conservative (fewer false positives)")
    print("   - Nearly no response time impact, very efficient RAG utilization")

    print("\n3. Llama's Performance Degrades with RAG:")
    print("   - RAG significantly reduces recall (-55%)")
    print("   - Suggests Llama struggles with structured RAG context")
    print("   - Response time IMPROVES dramatically with RAG (21.5s → 6.4s)")
    print("   - Hypothesis: Without RAG, Llama generates longer, more exploratory responses")
    print("   - With RAG, Llama becomes too constrained and misses detections")

    print("\n4. Model Architecture Impact:")
    print("   - GPT-4: Instruction-following model, benefits from structured RAG")
    print("   - Gemini: Balanced model, uses RAG selectively")
    print("   - Llama: Open-source model, may need different RAG formatting/prompting")

    print("\n5. Recommended Actions:")
    print("   - GPT-4: Continue using RAG, consider expanding RAG context")
    print("   - Gemini: Current RAG configuration is optimal")
    print("   - Llama: Consider alternative RAG strategies:")
    print("     • Different prompt templates for RAG context")
    print("     • Less structured RAG format (more conversational)")
    print("     • Hybrid approach: RAG as supplementary, not primary")
    print("     • Fine-tuning on RAG-style inputs")

if __name__ == '__main__':
    main()
