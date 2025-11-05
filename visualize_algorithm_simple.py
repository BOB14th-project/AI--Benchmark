import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

plt.rcParams['font.family'] = 'DejaVu Sans'

# Load results
models = {
    'GPT-4o': 'results/gpt_final.json',
    'Llama-3.1': 'results/llama_final.json',
    'Gemini-1.5': 'results/gemini_final.json'
}

print("Collecting algorithm performance data...")
algorithm_performance = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))

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
                    is_correct = result.get('true_positives', 0) > 0
                    algorithm_performance[alg][model_name]['total'] += 1
                    if is_correct:
                        algorithm_performance[alg][model_name]['correct'] += 1

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

# Sort by average accuracy
algorithm_order = df.groupby('Algorithm')['Accuracy'].mean().sort_values(ascending=False).index.tolist()
top_algorithms = algorithm_order[:15]  # Top 15 algorithms

print("\n=== Top 15 Algorithms by Average Accuracy ===")
top_df = df[df['Algorithm'].isin(top_algorithms)]
pivot_table = top_df.pivot_table(values='Accuracy', index='Algorithm', columns='Model', aggfunc='mean')
pivot_table = pivot_table.reindex(top_algorithms)
print(pivot_table.round(1))

# Visualization 1: Heatmap
fig, ax = plt.subplots(figsize=(10, 12))
sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn',
            vmin=0, vmax=100, cbar_kws={'label': 'Accuracy (%)'}, ax=ax)
ax.set_title('Top 15 Algorithms: Model Performance Heatmap', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Model', fontsize=11, fontweight='bold')
ax.set_ylabel('Algorithm', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('results/algorithm_heatmap.png', dpi=300, bbox_inches='tight')
print("\nSaved: results/algorithm_heatmap.png")
plt.close()

# Visualization 2: Grouped bar chart
fig, ax = plt.subplots(figsize=(14, 8))
x = np.arange(len(top_algorithms))
width = 0.25
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, model in enumerate(['GPT-4o', 'Llama-3.1', 'Gemini-1.5']):
    model_data = top_df[top_df['Model'] == model]
    accuracies = []
    for alg in top_algorithms:
        alg_data = model_data[model_data['Algorithm'] == alg]
        if len(alg_data) > 0:
            accuracies.append(alg_data['Accuracy'].values[0])
        else:
            accuracies.append(0)

    bars = ax.bar(x + i * width, accuracies, width, label=model, color=colors[i], alpha=0.8)

ax.set_xlabel('Algorithm', fontsize=11, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax.set_title('Top 15 Algorithms: Model Performance Comparison', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x + width)
ax.set_xticklabels(top_algorithms, rotation=45, ha='right')
ax.legend(loc='upper right')
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_ylim(0, 105)
plt.tight_layout()
plt.savefig('results/algorithm_bars.png', dpi=300, bbox_inches='tight')
print("Saved: results/algorithm_bars.png")
plt.close()

# Summary statistics
print("\n=== Model Best/Worst Algorithms ===")
for model in ['GPT-4o', 'Llama-3.1', 'Gemini-1.5']:
    model_df = df[df['Model'] == model].sort_values('Accuracy', ascending=False)
    if len(model_df) > 0:
        best = model_df.iloc[0]
        worst = model_df.iloc[-1]
        print(f"\n{model}:")
        print(f"  Best:  {best['Algorithm']: <30} {best['Accuracy']:.1f}% ({best['Correct']}/{best['Total']})")
        print(f"  Worst: {worst['Algorithm']: <30} {worst['Accuracy']:.1f}% ({worst['Correct']}/{worst['Total']})")

print("\n=== Overall Statistics ===")
print(f"Total unique algorithms detected: {len(algorithm_order)}")
print(f"Algorithms with 100% accuracy by at least one model: {len(df[df['Accuracy'] == 100]['Algorithm'].unique())}")

print("\nDone!")
