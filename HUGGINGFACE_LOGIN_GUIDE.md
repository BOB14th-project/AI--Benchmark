# HuggingFace 로그인 가이드

## 🚨 문제: Llama 3.1은 Gated Model입니다

PQCllama는 Meta의 Llama 3.1-8B-Instruct 모델 위에 LoRA 어댑터를 올린 모델입니다.
Llama 3.1은 **gated model**로, 접근하려면:
1. HuggingFace 계정 필요
2. Meta AI 라이센스 동의 필요
3. 인증 토큰으로 로그인 필요

---

## 📝 단계별 설정 방법

### 1단계: HuggingFace 계정 생성 (없는 경우)

https://huggingface.co/join 방문하여 가입

### 2단계: Llama 3.1 접근 권한 요청

1. https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct 방문
2. "Request Access" 버튼 클릭
3. Meta AI License 동의
4. 몇 분 내로 자동 승인됨 (보통 즉시)

### 3단계: HuggingFace 토큰 생성

1. https://huggingface.co/settings/tokens 방문
2. "New token" 클릭
3. Token 이름: "pqc-benchmark" (임의)
4. Type: **Read** (write 권한 불필요)
5. "Generate token" 클릭
6. 생성된 토큰 복사 (hf_xxxxxxxxxxxxx...)

### 4단계: 로그인

#### 방법 A: CLI로 로그인 (권장)

```bash
huggingface-cli login
```

토큰 입력: `hf_xxxxxxxxxxxxx...` (붙여넣기)

#### 방법 B: 환경 변수로 설정

```bash
export HF_TOKEN="hf_xxxxxxxxxxxxx..."
```

또는 Python 코드에서:

```python
from huggingface_hub import login
login(token="hf_xxxxxxxxxxxxx...")
```

#### 방법 C: 토큰 파일로 저장

```bash
mkdir -p ~/.huggingface
echo "hf_xxxxxxxxxxxxx..." > ~/.huggingface/token
```

---

## ✅ 로그인 확인

```bash
huggingface-cli whoami
```

성공하면 계정 정보가 표시됩니다.

---

## 🔄 다시 setup 실행

로그인 후:

```bash
python setup_pqcllama.py
```

이제 Llama 3.1 모델을 다운로드할 수 있습니다!

---

## 📦 전체 다운로드 크기

- Llama 3.1 8B Instruct: ~16GB
- PQCllama LoRA Adapter: ~500MB
- **총: ~16.5GB**

Apple M2 24GB 시스템에서는 충분합니다!

---

## ⚠️ 주의사항

1. **인터넷 연결**: 안정적인 연결 필요 (16GB 다운로드)
2. **디스크 공간**: 최소 20GB 여유 공간 확보
3. **시간**: 첫 다운로드는 10-30분 소요 (인터넷 속도에 따라)
4. **캐시**: 한 번 다운로드하면 `./models/pqcllama`에 저장되어 재사용

---

## 🆘 문제 해결

### "401 Unauthorized" 오류

→ 로그인이 안 됐거나 Llama 3.1 접근 권한이 없음
→ 위 단계 2, 3, 4 다시 확인

### "Connection timeout" 오류

→ 인터넷 연결 확인
→ VPN 사용 중이면 일시적으로 끄기

### "No space left on device"

→ 디스크 공간 확보 (최소 20GB)
→ 다른 디렉토리를 cache_dir로 지정

```python
cache_dir = "/path/to/large/disk/pqcllama"
```

---

## 🚀 빠른 시작 (요약)

```bash
# 1. 로그인
huggingface-cli login
# 토큰 입력: hf_xxxxxxxxxxxxx...

# 2. Llama 3.1 접근 권한 요청
# https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
# "Request Access" 클릭

# 3. Setup 실행
python setup_pqcllama.py

# 4. 벤치마크 실행
python benchmark_pqcllama_vs_llama3.py
```

---

## 📞 추가 도움

- HuggingFace 문서: https://huggingface.co/docs/hub/security-tokens
- Llama 3.1 모델 페이지: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
