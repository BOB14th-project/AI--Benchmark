#!/usr/bin/env python3
"""
F1 점수 데이터 확인 스크립트
"""

import json

with open('benchmark_results_2.json', 'r') as f:
    data = json.load(f)

# F1 점수 확인
model_f1 = {}
for result in data.get('detailed_results', []):
    model = result.get('model', 'unknown')
    metrics = result.get('metrics', {})
    f1 = metrics.get('f1_score')

    if f1 is not None and model != 'unknown':
        if model not in model_f1:
            model_f1[model] = []
        model_f1[model].append(f1)

# 모델별 평균 F1 출력
for model, scores in sorted(model_f1.items()):
    avg_f1 = sum(scores) / len(scores) if scores else 0
    print(f'{model}: avg F1 = {avg_f1:.4f}, count = {len(scores)}')
