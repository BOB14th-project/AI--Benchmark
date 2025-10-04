#!/bin/bash
# 에이전트별 모델 성능 빠른 분석 스크립트

echo "🔍 AI 벤치마크 - 에이전트별 최적 모델 분석"
echo "============================================="
echo ""

# 결과 파일 확인
if [ ! -f "benchmark_results.json" ]; then
    echo "❌ benchmark_results.json 파일이 없습니다."
    exit 1
fi

# 1. 요약 정보 출력
echo "📊 에이전트별 최고 성능 모델 요약"
echo "----------------------------------------"
python visualize_agent_performance.py benchmark_results.json --summary --min-tests 20

# 2. 모든 그래프 생성
echo ""
echo "📈 그래프 생성 중..."
python visualize_agent_performance.py benchmark_results.json \
    --heatmap \
    --bar \
    --ranking \
    --comprehensive \
    --min-tests 20 2>/dev/null

echo ""
echo "✅ 완료! 생성된 파일:"
ls -lh agent_*.png comprehensive_*.png 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'

echo ""
echo "📖 자세한 가이드: VISUALIZATION_GUIDE.md 참고"
