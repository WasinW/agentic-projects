# LLM Serving Self-Hosted — Deep Dive

> vLLM, TGI, llama.cpp, SGLang — pick the right inference engine
> ปี 2026: vLLM ครอง production, llama.cpp ครอง edge

---

## 1. ทำไมต้อง Self-Host

### When Self-Host Wins

✅ **High volume**: > 10M tokens/day (API expensive)
✅ **Privacy**: data cannot leave premises
✅ **Customization**: fine-tuned models
✅ **Latency**: LAN < internet
✅ **Compliance**: data residency requirements
✅ **Cost predictability**: fixed infra vs variable API

### When API Wins

✅ Speed to start (days vs months)
✅ Best models (frontier closed source)
✅ No infra burden
✅ Auto-scaling
✅ Low/medium volume

### Crossover Point

```
~10M tokens/day = approximate breakeven
Below: API cheaper after considering infra + ops
Above: self-host saves money
```

---

## 2. Inference Engines Landscape (2026)

| Engine | Best For | License |
|---|---|---|
| **vLLM** | Production, high-throughput multi-user | Apache 2.0 |
| **SGLang** | Production, complex generation | Apache 2.0 |
| **TGI** (Hugging Face) | Maintenance mode (use vLLM) | HFOIL |
| **llama.cpp** | Single-user, edge, no GPU | MIT |
| **Ollama** | Dev, prototyping, easy UX | MIT |
| **TensorRT-LLM** | NVIDIA-optimized, max perf | Apache 2.0 |
| **MLX** | Apple Silicon | MIT |
| **LMDeploy** | Asian models (Qwen) | Apache 2.0 |

### 2026 Reality

- **vLLM**: default for production
- **SGLang**: emerging competitor, ~30% faster on H100
- **TGI**: Hugging Face deprecated (Dec 2025)
- **llama.cpp**: best for edge/on-device
- **Ollama**: best dev experience (built on llama.cpp)

---

## 3. vLLM Deep Dive

### Why vLLM Dominates

#### PagedAttention (key innovation)
```
Traditional:
  Each request reserves max-length memory upfront
  Wasteful — most requests shorter

vLLM PagedAttention:
  KV cache in pages (like OS virtual memory)
  Allocate pages dynamically
  Share pages across requests with same prefix
  → 24x throughput improvement
```

#### Continuous Batching
```
Traditional batching:
  [req1] [req2] [req3] [req4]
  All wait for slowest in batch
  
Continuous batching:
  Each request joins/leaves batch as ready
  GPUs always busy
  → much higher throughput
```

### Setup

```bash
pip install vllm
```

### Quick Start

```bash
# Serve a model
vllm serve meta-llama/Llama-3-70B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.95
```

### Python API

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-70B-Instruct",
    tensor_parallel_size=4,  # use 4 GPUs
    dtype="bfloat16",
    gpu_memory_utilization=0.9,
    max_model_len=8192,
)

sampling = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
)

outputs = llm.generate(
    ["What is the capital of France?"],
    sampling
)
```

### OpenAI-Compatible API

```bash
# Server mode
vllm serve meta-llama/Llama-3-70B-Instruct \
    --host 0.0.0.0 --port 8000

# Client uses OpenAI SDK
import openai
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)
response = client.chat.completions.create(
    model="meta-llama/Llama-3-70B-Instruct",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### LoRA Adapter Support

```bash
# Serve base + multiple LoRA adapters
vllm serve meta-llama/Llama-3-8B-Instruct \
    --enable-lora \
    --lora-modules \
        finance=path/to/finance_lora \
        medical=path/to/medical_lora \
    --max-loras 2 \
    --max-lora-rank 64
```

```python
# Use specific adapter per request
response = client.chat.completions.create(
    model="finance",  # uses finance LoRA on top of Llama-3
    messages=[...]
)
```

### Quantization Support

```bash
# AWQ 4-bit (common)
vllm serve meta-llama/Llama-3-70B-AWQ \
    --quantization awq

# GPTQ
vllm serve TheBloke/Llama-3-70B-GPTQ \
    --quantization gptq

# FP8 (H100/H200)
vllm serve meta-llama/Llama-3-70B \
    --quantization fp8
```

### Performance Tuning

```bash
vllm serve model \
    --tensor-parallel-size 4 \
    --pipeline-parallel-size 1 \    # for very large models
    --max-num-seqs 256 \              # parallel requests
    --max-num-batched-tokens 8192 \   # batch size
    --gpu-memory-utilization 0.95 \   # use most VRAM
    --enable-prefix-caching \         # cache common prefixes
    --enable-chunked-prefill          # better mid-len throughput
```

### Hardware Requirements

| Model Size | Min Hardware | Recommended |
|---|---|---|
| 7B fp16 | 1× A10 (24GB) | 1× A100 |
| 7B AWQ-4bit | 1× T4 (16GB) | 1× A10 |
| 13B fp16 | 1× A100 (40GB) | 1× A100 80GB |
| 70B fp16 | 4× A100 80GB | 8× A100 |
| 70B AWQ-4bit | 1× A100 80GB | 1× H100 |
| 405B fp16 | 8× H100 | 16× H100 |

---

## 4. SGLang (Emerging Alternative)

### Why SGLang

- ~29% faster than vLLM on H100 batch inference
- Great structured generation support
- RadixAttention (better KV cache)

### Setup

```bash
pip install sglang[all]
```

### Server

```bash
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3-8B-Instruct \
    --port 30000
```

### Frontend Language

SGLang has unique frontend for complex prompts:

```python
import sglang as sgl

@sgl.function
def multi_turn_qa(s, question1, question2):
    s += sgl.system("You are a helpful assistant.")
    s += sgl.user(question1)
    s += sgl.assistant(sgl.gen("answer1", max_tokens=256))
    s += sgl.user(question2)
    s += sgl.assistant(sgl.gen("answer2", max_tokens=256))

state = multi_turn_qa.run(
    question1="What's 2+2?",
    question2="What's that times 10?"
)
print(state["answer1"], state["answer2"])
```

### When to Choose SGLang vs vLLM

```
vLLM: more mature, larger ecosystem, production-proven
SGLang: faster on H100, better structured generation, frontend language
2026 reality: try both, pick faster on your hardware
```

---

## 5. llama.cpp (Edge / Local)

### Why llama.cpp

- Pure C/C++, no dependencies
- Run on CPU only (slow but possible)
- Best on Apple Silicon (Metal)
- Edge devices (phones, Raspberry Pi)
- GGUF quantization (extreme: 1-bit)

### Setup

```bash
# Build
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
make -j

# Or via Ollama (recommended for users)
brew install ollama
```

### Run

```bash
# CLI inference
./llama-cli -m models/llama-3-8b.Q4_K_M.gguf \
    -p "What is the capital of France?" \
    -n 256

# Server mode (OpenAI compatible)
./llama-server -m model.gguf --port 8080
```

### Ollama (easier UX)

```bash
ollama pull llama3.1:8b
ollama run llama3.1:8b "Hello"

# API
curl http://localhost:11434/api/generate -d '{
    "model": "llama3.1:8b",
    "prompt": "Hello"
}'
```

### Quantization Levels (GGUF)

| Format | Bits | Quality | Size (8B) |
|---|---|---|---|
| F16 | 16 | 100% | 16 GB |
| Q8_0 | 8 | 99% | 8 GB |
| Q5_K_M | 5.5 | 98% | 5.5 GB |
| Q4_K_M | 4.5 | 95% | 4.7 GB |
| Q3_K_M | 3.5 | 88% | 4.0 GB |
| Q2_K | 2.6 | 75% | 3.0 GB |
| Q1_S | 1 | <60% | 2 GB |

**Best practice**: Q4_K_M is sweet spot (95% quality, fits memory)

### When llama.cpp

✅ Single user (no batching)
✅ Local development
✅ Edge devices
✅ Apple Silicon
✅ Privacy-critical (offline)

❌ Multi-user production (vLLM better)
❌ Batch inference (SGLang/vLLM faster)

---

## 6. Performance Benchmarks (2026 typical)

### Throughput (tokens/sec, Llama-3 8B, 100 concurrent users)

| Engine | Hardware | TPS |
|---|---|---|
| vLLM | A100 | 12,000 |
| SGLang | A100 | 14,000 |
| SGLang | H100 | 16,200 |
| TGI v3 | A100 | 8,000 |
| llama.cpp | CPU | 50 |
| llama.cpp | M2 Max | 80 |

### Latency (Time to First Token)

| Engine | TTFT (median) |
|---|---|
| vLLM | 50-100ms |
| llama.cpp single user | 100-200ms |
| llama.cpp queued | 1-5s (waiting) |

### Long Context Performance

```
TGI v3 wins on long context (200K+):
  13x faster than vLLM on long prompts
  But: TGI is in maintenance mode

vLLM v1+ catching up
```

---

## 7. Production Deployment

### Architecture: Single-Tenant Service

```
[Load Balancer]
       │
       ├─ vLLM instance 1 (4 GPUs)
       ├─ vLLM instance 2 (4 GPUs)
       └─ vLLM instance 3 (4 GPUs)
              ↓
       [Model weights on shared NFS]
```

### Architecture: Multi-Tenant (with LoRA)

```
[API Gateway]
       │
       ↓
[vLLM with --enable-lora]
       │
       └─ Base: Llama-3-70B
       └─ Adapters: 50+ LoRAs (loaded on demand)
       
Routes:
   tenant_a/finance → finance LoRA
   tenant_b/medical → medical LoRA
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama3-70b
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm
  template:
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        command: ["python", "-m", "vllm.entrypoints.openai.api_server"]
        args:
          - "--model=meta-llama/Llama-3-70B-Instruct"
          - "--tensor-parallel-size=4"
          - "--port=8000"
        resources:
          limits:
            nvidia.com/gpu: 4
            memory: 200Gi
```

### Auto-Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-llama3-70b
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: vllm_requests_per_second
      target:
        type: AverageValue
        averageValue: "10"
```

### Monitoring

```python
# vLLM exposes Prometheus metrics
# Key metrics:
- vllm:request_success_total
- vllm:request_latency_ms (p50, p95, p99)
- vllm:gpu_cache_usage_perc
- vllm:num_requests_running
- vllm:num_requests_waiting
- vllm:tokens_per_second
```

---

## 8. Cost Comparison

### Self-Host vs API (Llama 3 70B equivalent)

```
Self-Host (vLLM on 4× A100):
  Hardware: $25/hour (cloud) = $18K/month (24/7)
  Or: $200K capex + ops

API (Claude Sonnet for similar quality):
  $3 / 1M input + $15 / 1M output
  
Breakeven: ~5M output tokens/day
```

### Cost Optimization Self-Host

#### Batching
```
Single user: 1 GPU × 1 query/sec = 100 tokens/sec
Batched 100 users: 1 GPU × 100 queries = 10,000 tokens/sec
100x utilization!
```

#### Quantization
```
fp16: 70B = 140GB → 4× A100
AWQ-4bit: 70B = ~40GB → 1× A100 80GB
Cost: 4x reduction
Quality: ~3% loss (often acceptable)
```

#### Spot/Preemptible
```
On-demand: $5/GPU-hour
Spot:      $1.5/GPU-hour
70% savings if can tolerate interruption
```

#### Speculative Decoding
```
Use small "draft" model to predict tokens
Big model verifies (parallel)
2-3x speedup typical
```

```bash
vllm serve large_model \
    --speculative-draft-tensor-parallel-size 1 \
    --speculative-model small_model \
    --num-speculative-tokens 5
```

---

## 9. Specific Use Cases

### Use Case 1: Customer Support Bot (high volume)

```
Volume: 1M conversations/day, 5K tokens avg
= 5B tokens/day

API cost: $25K/month  (Sonnet)
Self-host: $20K/month (4× A100 + ops)

Choice: self-host (slight savings + privacy)
```

### Use Case 2: Internal Code Assistant

```
Volume: 100 developers × 50 queries/day × 2K tokens
= 10M tokens/day

API: $1500/month
Self-host: $18K/month

Choice: API (cheaper)
```

### Use Case 3: Document Processing Pipeline

```
Volume: 1M docs/day × 10K tokens
= 10B tokens/day input

API: prohibitive ($30K+/day)
Self-host required: ~$30K/month
```

### Use Case 4: Edge / On-Device

```
Privacy: data must stay on device
Volume: 1 user, intermittent

llama.cpp on user's machine
Q4_K_M quantized 8B model
Works on consumer GPU/Apple Silicon
```

---

## 10. Common Issues & Fixes

### Issue 1: OOM on Server Start
```
Cause: GPU memory not enough for model

Fix:
- Reduce max_model_len
- Use quantization (AWQ/GPTQ)
- Decrease gpu_memory_utilization (leave for activations)
- Use larger GPU
- Tensor parallel across more GPUs
```

### Issue 2: Slow Throughput
```
Cause: small batch size, underutilized GPU

Fix:
- Increase max_num_seqs
- Increase max_num_batched_tokens
- Enable continuous batching (default in vLLM)
- Check no waiting requests bottleneck
```

### Issue 3: High Latency for First Token
```
Cause: long prompt processing

Fix:
- Enable chunked prefill (vLLM)
- Smaller max_model_len
- Speculative decoding for short outputs
- Prefix caching for repeated prompts
```

### Issue 4: Memory Leak / Slow Degradation
```
Cause: cache fragmentation, GPU memory churn

Fix:
- Restart periodically (cron)
- Increase --max-num-seqs to fit in clean cache
- Update vLLM (frequent fixes)
```

### Issue 5: Model Loading Slow
```
First time: 5-30 minutes (download + load)

Fix:
- Pre-warm: load model in init container
- Use shared NFS for weights
- Use larger PVCs to cache models
```

---

## 11. Multi-Modal Serving

### Vision-Language Models

```bash
# vLLM supports VLMs
vllm serve llava-hf/llava-v1.6-mistral-7b-hf
```

```python
response = client.chat.completions.create(
    model="llava-hf/llava-v1.6-mistral-7b-hf",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": "..."}},
            {"type": "text", "text": "Describe this"}
        ]
    }]
)
```

### Audio (Whisper)

```bash
# Use specialized: faster-whisper or whisper-turbo
pip install faster-whisper

from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cuda")
segments, info = model.transcribe("audio.mp3")
```

### TTS

```bash
# Coqui TTS, MeloTTS, Bark
# Generally not in vLLM ecosystem
# Use specialized servers
```

---

## 12. Choosing Your Stack (2026 Decision)

### Decision Tree

```
Production multi-user, API-compatible?
  → vLLM (default)

H100 hardware + complex generation?
  → SGLang (faster on H100)

Single user, local development?
  → Ollama (built on llama.cpp)

Edge device / no GPU?
  → llama.cpp directly

Apple Silicon priority?
  → MLX or llama.cpp

Need TensorRT speedup, NVIDIA stack?
  → TensorRT-LLM (most complex setup)

Already on AWS Bedrock, GCP Vertex?
  → Use managed (less ops)
```

---

## 13. Cheat Sheet

### Q: "Self-host LLM ดีมั้ย?"
> "Breakeven ~10M tokens/day
> ต่ำกว่านั้น: API ถูกกว่า + ง่ายกว่า
> สูงกว่านั้น: self-host ประหยัด + ควบคุมได้
> ปี 2026: vLLM เป็น default production"

### Q: "vLLM vs SGLang?"
> "vLLM: more mature, default choice, ecosystem
> SGLang: ~30% faster on H100, better structured gen
> 2026 reality: try both, pick whichever faster on your hardware"

### Q: "Quantization ดีมั้ย?"
> "AWQ 4-bit: 95-97% quality, 4x memory reduction
> GPTQ 4-bit: similar
> FP8 (H100): 99% quality, 2x reduction
> Q4_K_M (GGUF): edge default
> Always quantize for production unless quality critical"

### Q: "Hardware เลือกอะไร?"
> "7B-13B: 1× A100 80GB or 1× H100
> 70B: 4× A100 (fp16) or 1× A100 (AWQ)
> 405B: 8× H100 minimum
> Edge/dev: M2/M3 Mac with llama.cpp"

### Q: "ทำไมไม่ใช้ TGI?"
> "Hugging Face deprecated TGI ในธันวาคม 2025
> Maintenance mode only
> Recommendation: vLLM หรือ SGLang"

---

## Sources

- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub](https://github.com/vllm-project/vllm)
- [SGLang Documentation](https://docs.sglang.ai/)
- [llama.cpp GitHub](https://github.com/ggml-org/llama.cpp)
- [Ollama](https://ollama.com/)
- [vLLM vs Ollama vs llama.cpp vs TGI 2026](https://www.aimadetools.com/blog/vllm-vs-ollama-vs-llamacpp-vs-tgi/)
- [Best LLM Inference Engines 2026: vLLM, TensorRT-LLM, TGI, SGLang](https://www.yottalabs.ai/post/best-llm-inference-engines-in-2026-vllm-tensorrt-llm-tgi-and-sglang-compared)
- [vLLM vs TGI: LLM Serving Benchmarks (2026)](https://www.buildmvpfast.com/blog/vllm-vs-tgi-llm-serving-benchmarks-2026)
- [LLM Inference Servers Compared](https://blog.premai.io/llm-inference-servers-compared-vllm-vs-tgi-vs-sglang-vs-triton-2026/)
- [vLLM or llama.cpp: Choosing the right engine - Red Hat](https://developers.redhat.com/articles/2025/09/30/vllm-or-llamacpp-choosing-right-llm-inference-engine-your-use-case)
