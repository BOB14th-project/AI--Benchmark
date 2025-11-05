"""
현재 시스템 진단 및 벤치마크 실행 가능 여부 확인
"""
import torch
import psutil
import platform
import shutil

print("="*80)
print("PQCllama 벤치마크 시스템 진단")
print("="*80)

# CPU
print(f"\n🖥️  CPU")
print(f"   프로세서: {platform.processor()}")
print(f"   물리 코어: {psutil.cpu_count(logical=False)}")
print(f"   논리 코어: {psutil.cpu_count(logical=True)}")

# RAM
ram = psutil.virtual_memory()
print(f"\n💾 메모리")
print(f"   총 RAM: {ram.total / (1024**3):.1f}GB")
print(f"   사용 중: {ram.used / (1024**3):.1f}GB")
print(f"   사용 가능: {ram.available / (1024**3):.1f}GB")
print(f"   사용률: {ram.percent}%")

# GPU
gpu_type = None
if torch.cuda.is_available():
    gpu_type = "NVIDIA"
    print(f"\n🎮 GPU (NVIDIA)")
    for i in range(torch.cuda.device_count()):
        print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"   VRAM: {props.total_memory / (1024**3):.1f}GB")
        print(f"   Compute Capability: {props.major}.{props.minor}")
    print(f"   CUDA 버전: {torch.version.cuda}")
    print(f"   cuDNN 버전: {torch.backends.cudnn.version()}")
elif torch.backends.mps.is_available():
    gpu_type = "Apple"
    print(f"\n🍎 Apple Silicon GPU (Metal)")
    print(f"   MPS 사용 가능: ✅")
    print(f"   통합 메모리: {ram.total / (1024**3):.1f}GB")
else:
    gpu_type = None
    print(f"\n⚠️  GPU 없음")
    print(f"   CPU 추론만 가능")

# 디스크
disk = psutil.disk_usage('/')
print(f"\n💿 저장공간")
print(f"   총 용량: {disk.total / (1024**3):.1f}GB")
print(f"   사용 중: {disk.used / (1024**3):.1f}GB")
print(f"   여유 공간: {disk.free / (1024**3):.1f}GB")
print(f"   사용률: {disk.percent}%")

# Python 환경
print(f"\n🐍 Python 환경")
print(f"   Python 버전: {platform.python_version()}")
print(f"   PyTorch 버전: {torch.__version__}")

# 패키지 확인
try:
    import transformers
    print(f"   Transformers: {transformers.__version__}")
except ImportError:
    print(f"   Transformers: ❌ 설치 필요")

try:
    import accelerate
    print(f"   Accelerate: {accelerate.__version__}")
except ImportError:
    print(f"   Accelerate: ⚠️  설치 권장")

# 벤치마크 예측
print(f"\n{'='*80}")
print("벤치마크 실행 가능 여부 분석")
print("="*80)

can_run = True
recommendations = []

# RAM 체크
ram_gb = ram.total / (1024**3)
if ram_gb >= 32:
    print(f"\n✅ RAM: {ram_gb:.1f}GB - 충분함")
elif ram_gb >= 24:
    print(f"\n⚠️  RAM: {ram_gb:.1f}GB - 양자화 권장")
    recommendations.append("INT8 양자화 사용 (load_in_8bit=True)")
elif ram_gb >= 16:
    print(f"\n⚠️  RAM: {ram_gb:.1f}GB - 양자화 필수, 테스트 수 제한")
    recommendations.append("INT4 양자화 필수 (load_in_4bit=True)")
    recommendations.append("TEST_LIMIT = 50 (테스트 수 제한)")
else:
    print(f"\n❌ RAM: {ram_gb:.1f}GB - 부족함 (최소 16GB 필요)")
    can_run = False

# GPU/VRAM 체크
if gpu_type == "NVIDIA":
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if vram_gb >= 24:
        print(f"✅ VRAM: {vram_gb:.1f}GB - 최적 (동시 실행 가능)")
        speed = "빠름 (~3-5초/요청)"
    elif vram_gb >= 16:
        print(f"✅ VRAM: {vram_gb:.1f}GB - 충분 (순차 실행 권장)")
        speed = "보통 (~5-8초/요청)"
    elif vram_gb >= 12:
        print(f"⚠️  VRAM: {vram_gb:.1f}GB - 양자화 권장")
        recommendations.append("INT8 양자화로 VRAM 절약")
        speed = "느림 (~8-12초/요청)"
    else:
        print(f"⚠️  VRAM: {vram_gb:.1f}GB - CPU 사용 권장")
        recommendations.append("CPU 추론으로 전환 고려")
        speed = "매우 느림 (~20-40초/요청)"

elif gpu_type == "Apple":
    if ram_gb >= 32:
        print(f"✅ Apple Silicon: 통합 메모리 {ram_gb:.1f}GB - 충분")
        speed = "보통 (~8-12초/요청)"
    elif ram_gb >= 24:
        print(f"⚠️  Apple Silicon: 통합 메모리 {ram_gb:.1f}GB - 양자화 권장")
        recommendations.append("INT8 양자화 권장")
        speed = "느림 (~12-20초/요청)"
    else:
        print(f"⚠️  Apple Silicon: 통합 메모리 {ram_gb:.1f}GB - 양자화 필수")
        recommendations.append("INT4 양자화 필수")
        recommendations.append("테스트 수 제한")
        speed = "매우 느림 (~20-40초/요청)"

else:  # CPU only
    print(f"⚠️  GPU 없음 - CPU 추론만 가능")
    speed = "매우 느림 (~30-60초/요청)"
    recommendations.append("가능하면 GPU 환경 사용 권장")
    recommendations.append("TEST_LIMIT = 10-20 (매우 작은 테스트만)")

# 디스크 체크
disk_free_gb = disk.free / (1024**3)
if disk_free_gb >= 50:
    print(f"✅ 디스크: {disk_free_gb:.1f}GB 여유 - 충분함")
elif disk_free_gb >= 30:
    print(f"⚠️  디스크: {disk_free_gb:.1f}GB 여유 - 최소 요구사항")
else:
    print(f"❌ 디스크: {disk_free_gb:.1f}GB 여유 - 부족함 (최소 30GB 필요)")
    can_run = False
    recommendations.append("디스크 공간 확보 필요")

# 예상 시간
print(f"\n{'='*80}")
print("예상 벤치마크 성능")
print("="*80)
print(f"\n⏱️  속도: {speed}")

if can_run:
    if speed == "빠름 (~3-5초/요청)":
        total_time = "3-4시간"
    elif speed == "보통 (~5-8초/요청)" or speed == "보통 (~8-12초/요청)":
        total_time = "6-8시간"
    elif speed == "느림 (~8-12초/요청)" or speed == "느림 (~12-20초/요청)":
        total_time = "8-12시간"
    else:
        total_time = "18-24시간"

    print(f"⏰ 전체 테스트 시간 (456개): 약 {total_time}")
    print(f"⏰ 50개 테스트 시간: 약 {total_time.split('-')[0].split('시간')[0]}시간 / 9")

# 최종 권장사항
print(f"\n{'='*80}")
if can_run:
    print("✅ 벤치마크 실행 가능")
else:
    print("❌ 현재 시스템으로는 실행 불가능")

if recommendations:
    print("\n💡 권장사항:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

print(f"\n{'='*80}")
print("권장 설정")
print("="*80)

# 구체적인 설정 제안
if gpu_type == "NVIDIA":
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if vram_gb >= 16 and ram_gb >= 24:
        print("\n🎯 권장 설정: 표준 실행")
        print("""
# benchmark_pqcllama_vs_llama3.py 설정
TEST_LIMIT = None  # 전체 테스트
torch_dtype=torch.float16
device_map="auto"
""")
    else:
        print("\n🎯 권장 설정: 양자화 실행")
        print("""
# benchmark_pqcllama_vs_llama3.py 설정
TEST_LIMIT = 50  # 테스트 수 제한
load_in_8bit=True  # INT8 양자화
device_map="auto"
""")

elif gpu_type == "Apple":
    if ram_gb >= 32:
        print("\n🎯 권장 설정: Apple Silicon 표준")
        print("""
# benchmark_pqcllama_vs_llama3.py 설정
TEST_LIMIT = None  # 전체 테스트
torch_dtype=torch.float16
device_map="mps"
""")
    else:
        print("\n🎯 권장 설정: Apple Silicon 양자화")
        print("""
# benchmark_pqcllama_vs_llama3.py 설정
TEST_LIMIT = 50  # 테스트 수 제한
load_in_8bit=True  # INT8 양자화
device_map="mps"
""")

else:  # CPU
    print("\n🎯 권장 설정: CPU 최적화")
    print("""
# benchmark_pqcllama_vs_llama3.py 설정
TEST_LIMIT = 10  # 매우 작은 테스트만
load_in_4bit=True  # INT4 양자화
device_map="cpu"

⚠️  경고: CPU 추론은 매우 느립니다!
    클라우드 GPU 사용을 강력히 권장합니다.
""")

print(f"\n{'='*80}")
print("다음 단계")
print("="*80)

if can_run:
    print("""
1. PQCllama 다운로드:
   python setup_pqcllama.py

2. 벤치마크 실행:
   python benchmark_pqcllama_vs_llama3.py

3. 결과 확인:
   results/ 디렉토리에서 JSON 파일 확인
""")
else:
    print("""
현재 시스템으로는 실행이 어렵습니다.

대안:
1. 클라우드 GPU 사용 (AWS, GCP, Azure)
2. RAM/VRAM 업그레이드
3. 더 작은 모델로 테스트 (예: 3B 모델)
""")

print("="*80)
