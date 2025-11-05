# PQCllama vs Llama3.1 벤치마크 하드웨어 요구사항

## 📊 모델 사양

### PQCllama (HuggingFace)
- **기반 모델**: Llama 3 8B
- **파라미터 수**: ~8 billion
- **모델 크기**:
  - FP32: ~32GB
  - FP16: ~16GB
  - INT8: ~8GB
- **실행 방식**: Transformers + PyTorch (직접 로드)

### Llama3.1 8B (Ollama)
- **파라미터 수**: ~8 billion
- **모델 크기**: ~4.7GB (양자화됨)
- **실행 방식**: Ollama 서버 (최적화된 추론)

---

## 💻 하드웨어 시나리오별 요구사항

### 🏆 **시나리오 1: 최적 환경 (추천)**

**동시 실행 가능, 빠른 속도**

```
CPU:     Apple M2 Pro 이상 / Intel i9 / AMD Ryzen 9
RAM:     32GB 이상
GPU:     NVIDIA RTX 3090 (24GB VRAM) 이상
         또는 RTX 4090 (24GB VRAM)
         또는 A100 (40GB/80GB VRAM)
Storage: 50GB SSD 여유 공간
```

**예상 성능**:
- PQCllama 추론: ~3-5초/요청
- Llama3.1 추론: ~5-8초/요청
- 총 소요 시간 (456 테스트): ~2-3시간

**비용**:
- 클라우드 (AWS p3.2xlarge): ~$3.06/hour
- 로컬 워크스테이션: $2,000-4,000

---

### ✅ **시나리오 2: 권장 환경**

**순차 실행, 적당한 속도**

```
CPU:     Apple M1/M2 / Intel i7 / AMD Ryzen 7
RAM:     24GB 이상 (16GB도 가능하지만 스왑 발생)
GPU:     NVIDIA RTX 3060 (12GB VRAM) 이상
         또는 RTX 4060 Ti (16GB VRAM)
Storage: 50GB SSD 여유 공간
```

**예상 성능**:
- PQCllama 추론: ~8-12초/요청
- Llama3.1 추론: ~10-15초/요청
- 총 소요 시간 (456 테스트): ~4-6시간

**비용**:
- 클라우드 (AWS g4dn.xlarge): ~$0.526/hour
- 로컬 워크스테이션: $1,000-2,000

---

### ⚠️ **시나리오 3: 최소 환경**

**CPU만 사용, 매우 느림**

```
CPU:     Intel i5 이상 / Apple M1
RAM:     16GB 최소 (24GB 권장)
GPU:     없음 (CPU 추론)
Storage: 50GB SSD 여유 공간
```

**예상 성능**:
- PQCllama 추론: ~30-60초/요청
- Llama3.1 추론: ~20-40초/요청
- 총 소요 시간 (456 테스트): ~12-24시간

**비용**:
- 클라우드 (AWS t3.2xlarge): ~$0.33/hour
- 로컬 일반 PC: $500-1,000

---

## 🎮 현재 시스템 확인

현재 시스템 사양을 확인해보세요:

```bash
# macOS
system_profiler SPHardwareDataType
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}'

# NVIDIA GPU 확인
nvidia-smi

# Linux
lscpu
free -h
nvidia-smi
```

---

## 📊 상세 메모리 분석

### **동시 실행 시 (최악의 경우)**

```
PQCllama (FP16):           ~16GB VRAM/RAM
Llama3.1 (Ollama):         ~6GB RAM
시스템 오버헤드:            ~2GB RAM
Python 프로세스:           ~1GB RAM
-------------------------------------------
총 필요량:                 ~25GB RAM/VRAM
```

### **순차 실행 시 (권장)**

```
한 번에 하나씩:
- PQCllama만 로드:         ~16GB VRAM/RAM
- 완료 후 메모리 해제
- Llama3.1만 로드:         ~6GB RAM
-------------------------------------------
총 필요량:                 ~16GB RAM/VRAM (최대)
```

---

## 🚀 최적화 옵션

### **1. 양자화 (Quantization)**

메모리를 줄이기 위해 양자화 사용:

```python
# INT8 양자화 (메모리 50% 절약)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,  # 16GB → 8GB
    device_map="auto"
)

# INT4 양자화 (메모리 75% 절약)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,  # 16GB → 4GB
    device_map="auto"
)
```

**장점**: 메모리 크게 절약
**단점**: 정확도 약간 하락 (~1-3%)

### **2. CPU Offloading**

GPU 메모리 부족 시 일부를 CPU로:

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # 자동으로 GPU/CPU 분산
    offload_folder="offload",
    offload_state_dict=True
)
```

### **3. 배치 처리 대신 순차 처리**

현재 스크립트는 이미 순차 처리를 사용하므로 추가 최적화 불필요.

---

## 💰 클라우드 옵션 비교

### **AWS EC2**

| 인스턴스 타입 | GPU | VRAM | RAM | 가격/시간 | 권장도 |
|--------------|-----|------|-----|----------|--------|
| **p3.2xlarge** | V100 | 16GB | 61GB | $3.06 | ⭐⭐⭐⭐⭐ 최적 |
| **g5.xlarge** | A10G | 24GB | 16GB | $1.006 | ⭐⭐⭐⭐ 좋음 |
| **g4dn.xlarge** | T4 | 16GB | 16GB | $0.526 | ⭐⭐⭐ 괜찮음 |
| **t3.2xlarge** | 없음 | - | 32GB | $0.33 | ⭐⭐ CPU만 |

**예상 비용 (456 테스트)**:
- p3.2xlarge: ~$9-12 (3-4시간)
- g5.xlarge: ~$4-6 (4-6시간)
- g4dn.xlarge: ~$3-4 (6-8시간)
- t3.2xlarge: ~$6-8 (18-24시간)

### **Google Cloud (GCP)**

| 인스턴스 타입 | GPU | VRAM | 가격/시간 | 권장도 |
|--------------|-----|------|----------|--------|
| **n1-standard-8 + V100** | V100 | 16GB | $2.48 | ⭐⭐⭐⭐⭐ |
| **n1-standard-8 + T4** | T4 | 16GB | $0.95 | ⭐⭐⭐⭐ |

### **Azure**

| 인스턴스 타입 | GPU | VRAM | 가격/시간 | 권장도 |
|--------------|-----|------|----------|--------|
| **NC6s_v3** | V100 | 16GB | $3.06 | ⭐⭐⭐⭐⭐ |
| **NC4as_T4_v3** | T4 | 16GB | $0.526 | ⭐⭐⭐⭐ |

---

## 🍎 Apple Silicon (M1/M2/M3) 특수 사항

### **장점**
- **통합 메모리**: GPU와 RAM이 공유되어 효율적
- **Metal 최적화**: PyTorch MPS 백엔드로 가속
- **전력 효율**: 배터리로도 실행 가능

### **메모리 권장사항**

| Mac 모델 | 통합 메모리 | PQCllama | Llama3.1 | 동시 실행 | 권장도 |
|---------|-----------|----------|----------|----------|--------|
| **M3 Max 128GB** | 128GB | ✅ 빠름 | ✅ 빠름 | ✅ 가능 | ⭐⭐⭐⭐⭐ |
| **M2 Ultra 192GB** | 192GB | ✅ 매우 빠름 | ✅ 빠름 | ✅ 가능 | ⭐⭐⭐⭐⭐ |
| **M2 Pro 32GB** | 32GB | ✅ 보통 | ✅ 빠름 | ⚠️ 가능 | ⭐⭐⭐⭐ |
| **M1/M2 16GB** | 16GB | ⚠️ 느림 | ✅ 가능 | ❌ 불가 | ⭐⭐ |

**M1/M2 16GB에서 실행 팁**:
```python
# INT8 양자화 필수
load_in_8bit=True

# 또는 INT4
load_in_4bit=True

# 순차 실행만 가능
TEST_LIMIT = 50  # 작은 배치로 테스트
```

---

## 🎯 **당신의 상황에 맞는 추천**

### **시나리오별 가이드**

#### 1️⃣ **빠른 결과 필요 (당일 완료)**
→ **클라우드 GPU** (AWS p3.2xlarge)
- 비용: ~$10
- 시간: 3-4시간
- 설정: 30분

#### 2️⃣ **비용 절약 (로컬 실행)**
→ **Apple M2 Pro 32GB** 또는 **RTX 3060 12GB**
- 비용: $0 (이미 보유)
- 시간: 6-8시간
- 설정: 즉시

#### 3️⃣ **스펙이 낮음 (16GB RAM만)**
→ **양자화 + 순차 실행**
```python
TEST_LIMIT = 50      # 50개만 테스트
load_in_8bit=True    # INT8 양자화
```
- 비용: $0
- 시간: 4-6시간 (50개 기준)

#### 4️⃣ **가장 정확한 결과**
→ **GPU 클러스터 또는 고성능 워크스테이션**
- NVIDIA A100 80GB 추천
- 비용: ~$20 (클라우드)
- 시간: 1-2시간

---

## 🔧 현재 시스템 진단 스크립트

```python
# check_system.py
import torch
import psutil
import platform

print("="*60)
print("시스템 진단")
print("="*60)

# CPU
print(f"\n🖥️  CPU: {platform.processor()}")
print(f"   코어 수: {psutil.cpu_count()}")

# RAM
ram = psutil.virtual_memory()
print(f"\n💾 RAM: {ram.total / (1024**3):.1f}GB")
print(f"   사용 가능: {ram.available / (1024**3):.1f}GB")

# GPU
if torch.cuda.is_available():
    print(f"\n🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
    print(f"   CUDA 버전: {torch.version.cuda}")
elif torch.backends.mps.is_available():
    print(f"\n🍎 Apple Silicon GPU (MPS)")
    print(f"   통합 메모리: {ram.total / (1024**3):.1f}GB")
else:
    print(f"\n⚠️  GPU 없음 (CPU 추론만 가능)")

# 디스크
disk = psutil.disk_usage('/')
print(f"\n💿 디스크:")
print(f"   여유 공간: {disk.free / (1024**3):.1f}GB")

# 권장사항
print(f"\n{'='*60}")
print("권장사항:")
print("="*60)

if torch.cuda.is_available():
    vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if vram >= 24:
        print("✅ 최적 환경 - 동시 실행 가능")
    elif vram >= 16:
        print("✅ 권장 환경 - 순차 실행 권장")
    else:
        print("⚠️  VRAM 부족 - 양자화 필수")
elif torch.backends.mps.is_available():
    if ram.total / (1024**3) >= 32:
        print("✅ Apple Silicon - 순차 실행 가능")
    else:
        print("⚠️  메모리 부족 - 양자화 권장")
else:
    if ram.total / (1024**3) >= 24:
        print("⚠️  CPU만 사용 - 느린 실행")
    else:
        print("❌ 메모리 부족 - 업그레이드 필요")
```

실행:
```bash
python check_system.py
```

---

## 📝 요약

| 환경 | RAM | GPU | 예상 시간 | 비용 | 권장도 |
|-----|-----|-----|----------|------|--------|
| **클라우드 GPU (p3.2xlarge)** | 61GB | V100 16GB | 3-4h | ~$10 | ⭐⭐⭐⭐⭐ |
| **Apple M2 Pro 32GB** | 32GB | MPS | 6-8h | $0 | ⭐⭐⭐⭐ |
| **RTX 3060 12GB** | 24GB | RTX 3060 | 8-10h | $0 | ⭐⭐⭐⭐ |
| **16GB RAM + 양자화** | 16GB | 없음 | 18-24h | $0 | ⭐⭐ |

**최종 권장**:
- **예산 있음** → AWS p3.2xlarge (3시간, $10)
- **로컬 실행** → M2 Pro 32GB 또는 RTX 3060+ (6-10시간)
- **저사양** → INT8 양자화 + 50개 테스트 (4-6시간)
