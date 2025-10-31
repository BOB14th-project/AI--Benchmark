import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns

sns.set_style("whitegrid")

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
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

def analyze_rag_impact(data):
    """Analyze RAG impact"""
    results = data['results']

    with_rag = []
    without_rag = []

    for result in results:
        metrics = calculate_metrics(result)
        if result['with_rag']:
            with_rag.append(metrics)
        else:
            without_rag.append(metrics)

    avg_with_rag = {
        'precision': np.mean([m['precision'] for m in with_rag]),
        'recall': np.mean([m['recall'] for m in with_rag]),
        'f1_score': np.mean([m['f1_score'] for m in with_rag])
    }

    avg_without_rag = {
        'precision': np.mean([m['precision'] for m in without_rag]),
        'recall': np.mean([m['recall'] for m in without_rag]),
        'f1_score': np.mean([m['f1_score'] for m in without_rag])
    }

    return avg_with_rag, avg_without_rag

def main():
    results_dir = Path('/Users/junsu/Projects/AI--Benchmark/results')

    models = {
        'GPT-4': 'gpt_test_3.json',
        'Gemini': 'gemini_test_3.json',
        'Llama': 'llama_test_3.json'
    }

    # Prepare data for visualization
    model_names = []
    precision_with = []
    precision_without = []
    recall_with = []
    recall_without = []
    f1_with = []
    f1_without = []

    for model_name, file_name in models.items():
        file_path = results_dir / file_name
        data = load_test_results(file_path)
        avg_with, avg_without = analyze_rag_impact(data)

        model_names.append(model_name)
        precision_with.append(avg_with['precision'])
        precision_without.append(avg_without['precision'])
        recall_with.append(avg_with['recall'])
        recall_without.append(avg_without['recall'])
        f1_with.append(avg_with['f1_score'])
        f1_without.append(avg_without['f1_score'])

    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Test 3: RAG Impact Comparison Across Models', fontsize=16, fontweight='bold')

    # 1. F1 Score Comparison
    ax = axes[0, 0]
    x = np.arange(len(model_names))
    width = 0.35

    bars1 = ax.bar(x - width/2, f1_without, width, label='Without RAG', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x + width/2, f1_with, width, label='With RAG', color='#4ECDC4', alpha=0.8)

    ax.set_ylabel('F1 Score', fontsize=12, fontweight='bold')
    ax.set_title('F1 Score: RAG vs No RAG', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=9)

    # 2. Precision Comparison
    ax = axes[0, 1]
    bars1 = ax.bar(x - width/2, precision_without, width, label='Without RAG', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x + width/2, precision_with, width, label='With RAG', color='#4ECDC4', alpha=0.8)

    ax.set_ylabel('Precision', fontsize=12, fontweight='bold')
    ax.set_title('Precision: RAG vs No RAG', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=9)

    # 3. Recall Comparison
    ax = axes[1, 0]
    bars1 = ax.bar(x - width/2, recall_without, width, label='Without RAG', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x + width/2, recall_with, width, label='With RAG', color='#4ECDC4', alpha=0.8)

    ax.set_ylabel('Recall', fontsize=12, fontweight='bold')
    ax.set_title('Recall: RAG vs No RAG', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=9)

    # 4. Improvement Percentage
    ax = axes[1, 1]
    f1_improvements = [(f1_with[i] - f1_without[i]) / f1_without[i] * 100 if f1_without[i] > 0 else 0
                       for i in range(len(model_names))]

    colors = ['#4ECDC4' if imp > 0 else '#FF6B6B' for imp in f1_improvements]
    bars = ax.bar(model_names, f1_improvements, color=colors, alpha=0.8)

    ax.set_ylabel('F1 Improvement (%)', fontsize=12, fontweight='bold')
    ax.set_title('F1 Score Improvement with RAG', fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:+.1f}%',
               ha='center', va='bottom' if height > 0 else 'top', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(results_dir / 'rag_comparison_test3_detailed.png', dpi=300, bbox_inches='tight')
    print(f"Visualization saved to: {results_dir / 'rag_comparison_test3_detailed.png'}")

    # Create a second figure for precision-recall trade-off
    fig2, ax = plt.subplots(figsize=(12, 8))

    for i, model in enumerate(model_names):
        # Plot without RAG
        ax.scatter(recall_without[i], precision_without[i], s=300, alpha=0.6,
                  color='#FF6B6B', marker='o', label=f'{model} (No RAG)' if i == 0 else '')
        # Plot with RAG
        ax.scatter(recall_with[i], precision_with[i], s=300, alpha=0.6,
                  color='#4ECDC4', marker='s', label=f'{model} (With RAG)' if i == 0 else '')

        # Draw arrow showing the change
        ax.annotate('', xy=(recall_with[i], precision_with[i]),
                   xytext=(recall_without[i], precision_without[i]),
                   arrowprops=dict(arrowstyle='->', lw=2, color='gray', alpha=0.5))

        # Add model labels
        ax.text(recall_without[i], precision_without[i] - 0.02, model,
               ha='center', va='top', fontsize=10, fontweight='bold')

    ax.set_xlabel('Recall', fontsize=14, fontweight='bold')
    ax.set_ylabel('Precision', fontsize=14, fontweight='bold')
    ax.set_title('Precision-Recall Trade-off: Impact of RAG (Test 3)', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12)

    # Add diagonal lines for F1 scores
    for f1_val in [0.2, 0.3, 0.4, 0.5]:
        recall_range = np.linspace(0.01, 0.99, 100)
        precision_line = (f1_val * recall_range) / (2 * recall_range - f1_val)
        precision_line = np.clip(precision_line, 0, 1)
        ax.plot(recall_range, precision_line, 'k--', alpha=0.2, linewidth=0.5)
        ax.text(0.95, (f1_val * 0.95) / (2 * 0.95 - f1_val), f'F1={f1_val}',
               fontsize=8, alpha=0.5, rotation=-45)

    plt.tight_layout()
    plt.savefig(results_dir / 'precision_recall_tradeoff_test3.png', dpi=300, bbox_inches='tight')
    print(f"Precision-Recall plot saved to: {results_dir / 'precision_recall_tradeoff_test3.png'}")

    plt.show()

if __name__ == '__main__':
    main()
