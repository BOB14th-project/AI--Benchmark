import json
import pandas as pd
from collections import defaultdict
import numpy as np

# Major algorithm categories
MAJOR_ALGORITHMS = {
    'AES': ['AES', 'AES-128', 'AES-192', 'AES-256', 'AES-GCM', 'AES-CBC', 'AES-CTR', 'AES-ECB'],
    'DES/3DES': ['DES', '3DES', 'Triple-DES', 'TripleDES', 'TDEA'],
    'RC4': ['RC4', 'ARCFOUR', 'ARC4'],
    'RC2': ['RC2'],
    'Blowfish': ['Blowfish'],
    'Twofish': ['Twofish'],
    'Camellia': ['Camellia'],
    'IDEA': ['IDEA'],
    'ChaCha20': ['ChaCha20', 'ChaCha'],
    'Korean Algorithms': ['SEED', 'HIGHT', 'ARIA', 'LEA', 'KCDSA', 'Korean ECDSA', 'KC-SEED'],
    'RSA': ['RSA', 'RSA-1024', 'RSA-2048', 'RSA-4096', 'RSAES-PKCS', 'RSASSA-PSS'],
    'DSA': ['DSA', 'KCDSA'],
    'DH': ['Diffie-Hellman', 'DH', 'DHE', 'ECDH', 'ECDHE'],
    'ECC': ['ECDSA', 'ECC', 'Elliptic Curve', 'secp256k1', 'secp384r1', 'P-256'],
    'ElGamal': ['ElGamal', 'El Gamal'],
    'MD5': ['MD5'],
    'SHA-1': ['SHA-1', 'SHA1'],
    'SHA-2': ['SHA-256', 'SHA-384', 'SHA-512', 'SHA256', 'SHA384', 'SHA512', 'SHA-2'],
    'SHA-3': ['SHA-3', 'SHA3', 'Keccak'],
    'PBKDF2': ['PBKDF2', 'PBKDF1'],
    'bcrypt': ['bcrypt'],
    'scrypt': ['scrypt'],
    'CBC': ['CBC'],
    'ECB': ['ECB'],
    'CTR': ['CTR'],
    'GCM': ['GCM'],
}

def categorize_algorithm(alg_name):
    alg_upper = alg_name.upper()
    for category, keywords in MAJOR_ALGORITHMS.items():
        for keyword in keywords:
            if keyword.upper() in alg_upper:
                return category
    return None

# Load results
models = {
    'GPT-4o': 'results/gpt_final.json',
    'Llama-3.1': 'results/llama_final.json',
    'Gemini-1.5': 'results/gemini_final.json'
}

print("="*80)
print("DETAILED MODEL CHARACTERISTICS ANALYSIS")
print("="*80)

model_stats = {}

for model_name, file_path in models.items():
    with open(file_path, 'r') as f:
        data = json.load(f)

    results_list = data.get('results', [])

    # Collect statistics
    stats = {
        'total_tests': len(results_list),
        'total_detections': 0,
        'correct_detections': 0,
        'false_positives': 0,
        'false_negatives': 0,
        'avg_response_time': [],
        'algorithms': defaultdict(lambda: {'correct': 0, 'total': 0}),
        'agent_types': defaultdict(lambda: {'correct': 0, 'total': 0}),
        'with_rag': {'correct': 0, 'total': 0},
        'without_rag': {'correct': 0, 'total': 0},
        'confidence_scores': [],
    }

    for result in results_list:
        # Response time
        if 'response_time' in result:
            stats['avg_response_time'].append(result['response_time'])

        # TP, FP, FN
        tp = result.get('true_positives', 0)
        fp = result.get('false_positives', 0)
        fn = result.get('false_negatives', 0)

        stats['correct_detections'] += tp
        stats['false_positives'] += fp
        stats['false_negatives'] += fn

        # RAG usage
        with_rag = result.get('with_rag', False)
        is_correct = tp > 0

        if with_rag:
            stats['with_rag']['total'] += 1
            if is_correct:
                stats['with_rag']['correct'] += 1
        else:
            stats['without_rag']['total'] += 1
            if is_correct:
                stats['without_rag']['correct'] += 1

        # Agent types
        agent_type = result.get('agent_type', 'unknown')
        stats['agent_types'][agent_type]['total'] += 1
        if is_correct:
            stats['agent_types'][agent_type]['correct'] += 1

        # Algorithm performance
        if 'raw_response' in result and 'detected_algorithms' in result['raw_response']:
            detected_algs = result['raw_response']['detected_algorithms']
            if detected_algs:
                stats['total_detections'] += len(detected_algs)
                for alg in detected_algs:
                    category = categorize_algorithm(alg)
                    if category:
                        stats['algorithms'][category]['total'] += 1
                        if is_correct:
                            stats['algorithms'][category]['correct'] += 1

        # Confidence scores
        if 'raw_response' in result and isinstance(result['raw_response'], dict):
            conf = result['raw_response'].get('confidence_score')
            if conf is not None:
                stats['confidence_scores'].append(float(conf))

    model_stats[model_name] = stats

# Print detailed analysis
for model_name, stats in model_stats.items():
    print(f"\n{'='*80}")
    print(f"MODEL: {model_name}")
    print(f"{'='*80}")

    # Overall metrics
    print(f"\n📊 OVERALL PERFORMANCE")
    print(f"  Total Tests:           {stats['total_tests']:>6}")
    print(f"  Total Detections:      {stats['total_detections']:>6}")
    print(f"  Correct Detections:    {stats['correct_detections']:>6} (TP)")
    print(f"  False Positives:       {stats['false_positives']:>6} (FP)")
    print(f"  False Negatives:       {stats['false_negatives']:>6} (FN)")

    # Precision and Recall
    precision = stats['correct_detections'] / (stats['correct_detections'] + stats['false_positives']) * 100 if (stats['correct_detections'] + stats['false_positives']) > 0 else 0
    recall = stats['correct_detections'] / (stats['correct_detections'] + stats['false_negatives']) * 100 if (stats['correct_detections'] + stats['false_negatives']) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\n  Precision:             {precision:>6.2f}%")
    print(f"  Recall:                {recall:>6.2f}%")
    print(f"  F1-Score:              {f1:>6.2f}%")

    # Response time
    if stats['avg_response_time']:
        avg_time = np.mean(stats['avg_response_time'])
        median_time = np.median(stats['avg_response_time'])
        min_time = np.min(stats['avg_response_time'])
        max_time = np.max(stats['avg_response_time'])

        print(f"\n⏱️  RESPONSE TIME")
        print(f"  Average:               {avg_time:>6.2f}s")
        print(f"  Median:                {median_time:>6.2f}s")
        print(f"  Min:                   {min_time:>6.2f}s")
        print(f"  Max:                   {max_time:>6.2f}s")

    # Confidence scores
    if stats['confidence_scores']:
        avg_conf = np.mean(stats['confidence_scores'])
        median_conf = np.median(stats['confidence_scores'])

        print(f"\n🎯 CONFIDENCE SCORES")
        print(f"  Average:               {avg_conf:>6.2f}")
        print(f"  Median:                {median_conf:>6.2f}")

    # RAG performance
    print(f"\n🔍 RAG USAGE IMPACT")
    if stats['with_rag']['total'] > 0:
        rag_acc = stats['with_rag']['correct'] / stats['with_rag']['total'] * 100
        print(f"  With RAG:    {stats['with_rag']['correct']:>4}/{stats['with_rag']['total']:<4} = {rag_acc:>6.2f}%")
    else:
        print(f"  With RAG:    No data")

    if stats['without_rag']['total'] > 0:
        no_rag_acc = stats['without_rag']['correct'] / stats['without_rag']['total'] * 100
        print(f"  Without RAG: {stats['without_rag']['correct']:>4}/{stats['without_rag']['total']:<4} = {no_rag_acc:>6.2f}%")
    else:
        print(f"  Without RAG: No data")

    if stats['with_rag']['total'] > 0 and stats['without_rag']['total'] > 0:
        impact = rag_acc - no_rag_acc
        print(f"  RAG Impact:            {impact:>+6.2f}%")

    # Agent type performance
    print(f"\n🤖 AGENT TYPE PERFORMANCE")
    for agent_type, agent_stats in sorted(stats['agent_types'].items(), key=lambda x: x[1]['total'], reverse=True):
        if agent_stats['total'] > 0:
            acc = agent_stats['correct'] / agent_stats['total'] * 100
            print(f"  {agent_type:<20} {agent_stats['correct']:>4}/{agent_stats['total']:<4} = {acc:>6.2f}%")

    # Algorithm strengths (top 5)
    print(f"\n✅ TOP 5 ALGORITHM STRENGTHS")
    alg_accs = []
    for alg, alg_stats in stats['algorithms'].items():
        if alg_stats['total'] >= 5:  # At least 5 detections
            acc = alg_stats['correct'] / alg_stats['total'] * 100
            alg_accs.append((alg, acc, alg_stats['correct'], alg_stats['total']))

    alg_accs.sort(key=lambda x: x[1], reverse=True)
    for i, (alg, acc, correct, total) in enumerate(alg_accs[:5], 1):
        print(f"  {i}. {alg:<20} {correct:>3}/{total:<3} = {acc:>6.2f}%")

    # Algorithm weaknesses (bottom 5)
    print(f"\n❌ TOP 5 ALGORITHM WEAKNESSES")
    for i, (alg, acc, correct, total) in enumerate(alg_accs[-5:][::-1], 1):
        print(f"  {i}. {alg:<20} {correct:>3}/{total:<3} = {acc:>6.2f}%")

# Comparative analysis
print(f"\n{'='*80}")
print("COMPARATIVE ANALYSIS")
print(f"{'='*80}")

print(f"\n📊 PRECISION COMPARISON")
for model_name, stats in model_stats.items():
    precision = stats['correct_detections'] / (stats['correct_detections'] + stats['false_positives']) * 100 if (stats['correct_detections'] + stats['false_positives']) > 0 else 0
    print(f"  {model_name:<15} {precision:>6.2f}%")

print(f"\n📊 RECALL COMPARISON")
for model_name, stats in model_stats.items():
    recall = stats['correct_detections'] / (stats['correct_detections'] + stats['false_negatives']) * 100 if (stats['correct_detections'] + stats['false_negatives']) > 0 else 0
    print(f"  {model_name:<15} {recall:>6.2f}%")

print(f"\n⏱️  SPEED COMPARISON (Average Response Time)")
for model_name, stats in model_stats.items():
    if stats['avg_response_time']:
        avg_time = np.mean(stats['avg_response_time'])
        print(f"  {model_name:<15} {avg_time:>6.2f}s")

print(f"\n🎯 CONFIDENCE COMPARISON (Average)")
for model_name, stats in model_stats.items():
    if stats['confidence_scores']:
        avg_conf = np.mean(stats['confidence_scores'])
        print(f"  {model_name:<15} {avg_conf:>6.2f}")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}\n")
