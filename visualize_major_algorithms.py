import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.family'] = 'DejaVu Sans'

# Major algorithm categories
MAJOR_ALGORITHMS = {
    # Symmetric ciphers
    'AES': ['AES', 'AES-128', 'AES-192', 'AES-256', 'AES-GCM', 'AES-CBC', 'AES-CTR', 'AES-ECB'],
    'DES/3DES': ['DES', '3DES', 'Triple-DES', 'TripleDES', 'TDEA'],
    'RC4': ['RC4', 'ARCFOUR', 'ARC4'],
    'RC2': ['RC2'],
    'Blowfish': ['Blowfish'],
    'Twofish': ['Twofish'],
    'Camellia': ['Camellia'],
    'IDEA': ['IDEA'],
    'ChaCha20': ['ChaCha20', 'ChaCha'],

    # Korean algorithms
    'Korean Algorithms': ['SEED', 'HIGHT', 'ARIA', 'LEA', 'KCDSA', 'Korean ECDSA', 'KC-SEED'],

    # Asymmetric
    'RSA': ['RSA', 'RSA-1024', 'RSA-2048', 'RSA-4096', 'RSAES-PKCS', 'RSASSA-PSS'],
    'DSA': ['DSA', 'KCDSA'],
    'DH': ['Diffie-Hellman', 'DH', 'DHE', 'ECDH', 'ECDHE'],
    'ECC': ['ECDSA', 'ECC', 'Elliptic Curve', 'secp256k1', 'secp384r1', 'P-256'],
    'ElGamal': ['ElGamal', 'El Gamal'],

    # Hash functions
    'MD5': ['MD5'],
    'SHA-1': ['SHA-1', 'SHA1'],
    'SHA-2': ['SHA-256', 'SHA-384', 'SHA-512', 'SHA256', 'SHA384', 'SHA512', 'SHA-2'],
    'SHA-3': ['SHA-3', 'SHA3', 'Keccak'],

    # Password hashing
    'PBKDF2': ['PBKDF2', 'PBKDF1'],
    'bcrypt': ['bcrypt'],
    'scrypt': ['scrypt'],

    # Block cipher modes
    'CBC': ['CBC'],
    'ECB': ['ECB'],
    'CTR': ['CTR'],
    'GCM': ['GCM'],
}

def categorize_algorithm(alg_name):
    """Categorize algorithm into major groups"""
    alg_upper = alg_name.upper()

    for category, keywords in MAJOR_ALGORITHMS.items():
        for keyword in keywords:
            if keyword.upper() in alg_upper:
                return category

    return None  # Not a major algorithm

# Load results
models = {
    'GPT-4o': 'results/gpt_final.json',
    'Llama-3.1': 'results/llama_final.json',
    'Gemini-1.5': 'results/gemini_final.json'
}

print("Collecting major algorithm performance data...")
algorithm_performance = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
all_detected = defaultdict(int)

for model_name, file_path in models.items():
    print(f"Processing {model_name}...")
    with open(file_path, 'r') as f:
        data = json.load(f)

    results_list = data.get('results', [])

    for result in results_list:
        if 'raw_response' in result and 'detected_algorithms' in result['raw_response']:
            detected_algs = result['raw_response']['detected_algorithms']
            if detected_algs:
                for alg in detected_algs:
                    all_detected[alg] += 1
                    category = categorize_algorithm(alg)
                    if category:  # Only major algorithms
                        is_correct = result.get('true_positives', 0) > 0
                        algorithm_performance[category][model_name]['total'] += 1
                        if is_correct:
                            algorithm_performance[category][model_name]['correct'] += 1

# Calculate accuracy
accuracy_data = []
for algorithm, models_data in algorithm_performance.items():
    for model_name, stats in models_data.items():
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        accuracy_data.append({
            'Algorithm': algorithm,
            'Model': model_name,
            'Accuracy': accuracy,
            'Correct': stats['correct'],
            'Total': stats['total']
        })

df = pd.DataFrame(accuracy_data)

# Sort by total detections
algorithm_order = df.groupby('Algorithm')['Total'].sum().sort_values(ascending=False).index.tolist()

print(f"\n=== Major Algorithm Categories (Total: {len(algorithm_order)}) ===")
pivot_table = df.pivot_table(values='Accuracy', index='Algorithm', columns='Model', aggfunc='mean')
pivot_table = pivot_table.reindex(algorithm_order)
print(pivot_table.round(1))

print("\n=== Detection Counts ===")
for alg in algorithm_order:
    total = df[df['Algorithm'] == alg]['Total'].sum()
    print(f"{alg: <25} {total:>5} detections")

# Visualization 1: Heatmap with counts
fig, ax = plt.subplots(figsize=(12, 10))
pivot_table_reindexed = pivot_table.reindex(algorithm_order)

sns.heatmap(pivot_table_reindexed, annot=True, fmt='.0f', cmap='RdYlGn',
            vmin=0, vmax=100, cbar_kws={'label': 'Accuracy (%)'}, ax=ax,
            linewidths=0.5, linecolor='gray')

ax.set_title('Major Cryptographic Algorithms: Model Performance',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Model', fontsize=12, fontweight='bold')
ax.set_ylabel('Algorithm Category', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('results/major_algorithms_heatmap.png', dpi=300, bbox_inches='tight')
print("\nSaved: results/major_algorithms_heatmap.png")
plt.close()

# Visualization 2: Grouped bar chart
fig, ax = plt.subplots(figsize=(16, 8))
x = np.arange(len(algorithm_order))
width = 0.25
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, model in enumerate(['GPT-4o', 'Llama-3.1', 'Gemini-1.5']):
    model_data = df[df['Model'] == model]
    accuracies = []
    for alg in algorithm_order:
        alg_data = model_data[model_data['Algorithm'] == alg]
        if len(alg_data) > 0:
            accuracies.append(alg_data['Accuracy'].values[0])
        else:
            accuracies.append(0)

    bars = ax.bar(x + i * width, accuracies, width, label=model,
                  color=colors[i], alpha=0.8, edgecolor='black', linewidth=0.5)

ax.set_xlabel('Algorithm Category', fontsize=12, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Major Cryptographic Algorithms: Detection Accuracy by Model',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x + width)
ax.set_xticklabels(algorithm_order, rotation=45, ha='right', fontsize=10)
ax.legend(loc='lower right', fontsize=11)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_ylim(0, 105)
ax.axhline(y=50, color='red', linestyle='--', alpha=0.3, linewidth=1)
plt.tight_layout()
plt.savefig('results/major_algorithms_bars.png', dpi=300, bbox_inches='tight')
print("Saved: results/major_algorithms_bars.png")
plt.close()

# Visualization 3: Detection volume vs accuracy
fig, ax = plt.subplots(figsize=(14, 8))

for model_idx, model in enumerate(['GPT-4o', 'Llama-3.1', 'Gemini-1.5']):
    model_data = df[df['Model'] == model]
    x_vals = []
    y_vals = []
    sizes = []
    labels = []

    for alg in algorithm_order:
        alg_data = model_data[model_data['Algorithm'] == alg]
        if len(alg_data) > 0:
            x_vals.append(model_idx)
            y_vals.append(alg_data['Accuracy'].values[0])
            sizes.append(alg_data['Total'].values[0] * 10)
            labels.append(alg)

    scatter = ax.scatter(x_vals, y_vals, s=sizes, alpha=0.6,
                        c=colors[model_idx], label=model, edgecolors='black', linewidth=1)

    # Add labels for large bubbles
    for i, (x, y, size, label) in enumerate(zip(x_vals, y_vals, sizes, labels)):
        if size > 100:  # Only label large detections
            ax.annotate(label, (x, y), fontsize=8, ha='center', va='center')

ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['GPT-4o', 'Llama-3.1', 'Gemini-1.5'], fontsize=11)
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Algorithm Detection: Volume vs Accuracy\n(Bubble size = number of detections)',
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_ylim(-5, 105)
ax.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig('results/major_algorithms_bubble.png', dpi=300, bbox_inches='tight')
print("Saved: results/major_algorithms_bubble.png")
plt.close()

# Summary statistics
print("\n=== Summary by Algorithm Category ===")
for alg in algorithm_order:
    alg_data = df[df['Algorithm'] == alg]
    avg_acc = alg_data['Accuracy'].mean()
    total_det = alg_data['Total'].sum()
    print(f"\n{alg}:")
    print(f"  Average Accuracy: {avg_acc:.1f}%")
    print(f"  Total Detections: {total_det}")
    for _, row in alg_data.iterrows():
        print(f"    {row['Model']}: {row['Accuracy']:.1f}% ({row['Correct']}/{row['Total']})")

print("\n=== Overall Statistics ===")
print(f"Major algorithm categories: {len(algorithm_order)}")
print(f"Total unique algorithms detected: {len(all_detected)}")
print(f"Algorithms categorized as major: {sum(all_detected[alg] for alg in all_detected if categorize_algorithm(alg))}")

print("\nDone!")
