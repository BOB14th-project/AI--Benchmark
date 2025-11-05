import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict

# 결과 파일 로드
models = {
    'GPT-4o': 'results/gpt_final.json',
    'Llama-3.1': 'results/llama_final.json',
    'Gemini-1.5': 'results/gemini_final.json'
}

# 알고리즘별 성능 데이터 수집
algorithm_performance = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))

for model_name, file_path in models.items():
    print(f"Loading {model_name}...")
    with open(file_path, 'r') as f:
        data = json.load(f)

    # results 배열에서 데이터 추출
    if 'results' in data:
        results_list = data['results']
    else:
        results_list = []

    for result in results_list:
        # detected_algorithms에서 알고리즘 추출
        if 'raw_response' in result and 'detected_algorithms' in result['raw_response']:
            detected_algs = result['raw_response']['detected_algorithms']
            if detected_algs:
                for alg in detected_algs:
                    # true_positives가 있으면 정답으로 간주
                    is_correct = result.get('true_positives', 0) > 0

                    algorithm_performance[alg][model_name]['total'] += 1
                    if is_correct:
                        algorithm_performance[alg][model_name]['correct'] += 1

# 정확도 계산
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

# 알고리즘별로 정렬 (전체 평균 정확도 기준)
algorithm_order = df.groupby('Algorithm')['Accuracy'].mean().sort_values(ascending=False).index.tolist()

print("\n알고리즘별 모델 성능:")
print(df.pivot_table(values='Accuracy', index='Algorithm', columns='Model', aggfunc='mean').round(2))

# 시각화 1: 히트맵
plt.figure(figsize=(14, 10))
pivot_df = df.pivot_table(values='Accuracy', index='Algorithm', columns='Model', aggfunc='mean')
pivot_df = pivot_df.reindex(algorithm_order)

sns.heatmap(pivot_df, annot=True, fmt='.1f', cmap='RdYlGn',
            vmin=0, vmax=100, cbar_kws={'label': 'Accuracy (%)'})
plt.title('Model Performance by Encryption Algorithm\n(Accuracy %)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Model', fontsize=12, fontweight='bold')
plt.ylabel('Encryption Algorithm', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('results/algorithm_model_heatmap.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: results/algorithm_model_heatmap.png")

# 시각화 2: 그룹화된 막대 그래프
plt.figure(figsize=(16, 8))
df_sorted = df.copy()
df_sorted['Algorithm'] = pd.Categorical(df_sorted['Algorithm'], categories=algorithm_order, ordered=True)
df_sorted = df_sorted.sort_values('Algorithm')

x = np.arange(len(algorithm_order))
width = 0.25
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

fig, ax = plt.subplots(figsize=(16, 8))

for i, model in enumerate(['GPT-4o', 'Llama-3.1', 'Gemini-1.5']):
    model_data = df_sorted[df_sorted['Model'] == model]
    accuracies = [model_data[model_data['Algorithm'] == alg]['Accuracy'].values[0]
                  if len(model_data[model_data['Algorithm'] == alg]) > 0 else 0
                  for alg in algorithm_order]

    bars = ax.bar(x + i * width, accuracies, width, label=model, color=colors[i], alpha=0.8)

    # 막대 위에 정확도 표시
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

ax.set_xlabel('Encryption Algorithm', fontsize=12, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Model Performance Comparison by Encryption Algorithm', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x + width)
ax.set_xticklabels(algorithm_order, rotation=45, ha='right')
ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_ylim(0, 110)

plt.tight_layout()
plt.savefig('results/algorithm_performance_bars.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/algorithm_performance_bars.png")

# 시각화 3: 알고리즘별 성능 차이 (레이더 차트용 데이터가 많을 경우)
top_algorithms = algorithm_order[:8]  # 상위 8개 알고리즘만

if len(top_algorithms) >= 3:
    fig = plt.figure(figsize=(14, 6))

    for idx, model in enumerate(['GPT-4o', 'Llama-3.1', 'Gemini-1.5'], 1):
        ax = plt.subplot(1, 3, idx, projection='polar')

        model_data = df[df['Model'] == model]
        values = [model_data[model_data['Algorithm'] == alg]['Accuracy'].values[0]
                 if len(model_data[model_data['Algorithm'] == alg]) > 0 else 0
                 for alg in top_algorithms]

        angles = np.linspace(0, 2 * np.pi, len(top_algorithms), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx-1])
        ax.fill(angles, values, alpha=0.25, color=colors[idx-1])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(top_algorithms, size=8)
        ax.set_ylim(0, 100)
        ax.set_title(model, fontsize=12, fontweight='bold', pad=20)
        ax.grid(True)

    plt.suptitle('Top 8 Algorithms - Model Performance Comparison',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('results/algorithm_radar_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/algorithm_radar_comparison.png")

# 시각화 4: 성공/실패 카운트
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, model in enumerate(['GPT-4o', 'Llama-3.1', 'Gemini-1.5']):
    model_data = df[df['Model'] == model].sort_values('Accuracy', ascending=True)

    ax = axes[idx]
    y_pos = np.arange(len(model_data))

    correct = model_data['Correct'].values
    total = model_data['Total'].values
    failed = total - correct

    bars1 = ax.barh(y_pos, correct, label='Correct', color='#2ecc71', alpha=0.8)
    bars2 = ax.barh(y_pos, failed, left=correct, label='Failed', color='#e74c3c', alpha=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(model_data['Algorithm'], fontsize=9)
    ax.set_xlabel('Number of Tests', fontsize=10, fontweight='bold')
    ax.set_title(f'{model}', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # 퍼센트 표시
    for i, (c, t) in enumerate(zip(correct, total)):
        if t > 0:
            pct = c / t * 100
            ax.text(t + 0.5, i, f'{pct:.0f}%', va='center', fontsize=8)

plt.suptitle('Correct vs Failed Tests by Algorithm and Model',
             fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('results/algorithm_correct_failed.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/algorithm_correct_failed.png")

# 통계 요약 저장
summary = df.groupby('Algorithm').agg({
    'Accuracy': ['mean', 'std'],
    'Total': 'sum'
}).round(2)

summary.columns = ['Mean_Accuracy', 'Std_Accuracy', 'Total_Tests']
summary = summary.sort_values('Mean_Accuracy', ascending=False)

print("\n알고리즘별 통계 요약:")
print(summary)

summary.to_csv('results/algorithm_performance_summary.csv')
print("\n✓ Saved: results/algorithm_performance_summary.csv")

# 모델별 최고/최저 성능 알고리즘
print("\n각 모델별 최고/최저 성능 알고리즘:")
for model in ['GPT-4o', 'Llama-3.1', 'Gemini-1.5']:
    model_df = df[df['Model'] == model].sort_values('Accuracy', ascending=False)
    best = model_df.iloc[0]
    worst = model_df.iloc[-1]
    print(f"\n{model}:")
    print(f"  최고: {best['Algorithm']} ({best['Accuracy']:.1f}%)")
    print(f"  최저: {worst['Algorithm']} ({worst['Accuracy']:.1f}%)")

plt.show()
