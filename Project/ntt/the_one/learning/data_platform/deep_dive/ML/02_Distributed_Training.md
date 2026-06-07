# Distributed Training — Deep Dive

> DDP, FSDP, ZeRO, Pipeline Parallelism — train models that don't fit on one GPU
> 2026 reality: PyTorch FSDP คือ default สำหรับ 7B-70B models

---

## 1. ทำไมต้อง Distributed Training

### Single GPU Limits

```
RTX 4090 (24 GB):  fit 7B model fp16 minimal
A100 (80 GB):      fit 30B model fp16
H100 (80 GB):      fit 30B model fp16 (faster)

But: 70B model? 405B model? Need multiple GPUs!
```

### 3 Reasons to Distribute

1. **Model too big**: doesn't fit in one GPU memory
2. **Data too much**: training takes too long
3. **Faster experimentation**: parallel hyperparameter search

---

## 2. Parallelism Strategies — 4 Types

### Type 1: Data Parallelism (DP / DDP)

```
Same model on each GPU
Different data per GPU
   ↓
Forward pass independent
   ↓
Combine gradients (all-reduce)
   ↓
Update weights (synchronized)
```

```
GPU 0: Model copy + batch[0:32]
GPU 1: Model copy + batch[32:64]
GPU 2: Model copy + batch[64:96]
GPU 3: Model copy + batch[96:128]
```

**Use case**: Model fits on 1 GPU, want to scale data
**Limit**: still need full model on each GPU

### Type 2: Tensor Parallelism (TP)

```
Split weight matrices across GPUs

Linear(d_in=1000, d_out=1000):
  GPU 0: half of W (shape 1000 × 500)
  GPU 1: other half (shape 1000 × 500)
  Combine output via all-gather
```

**Use case**: Layer too big for one GPU
**Limit**: communication-heavy, latency

### Type 3: Pipeline Parallelism (PP)

```
Split model into stages, each on different GPU

GPU 0: layers 1-10
GPU 1: layers 11-20
GPU 2: layers 21-30
GPU 3: layers 31-40

Like assembly line:
  Mini-batch 1: GPU 0 → GPU 1 → GPU 2 → GPU 3
  Mini-batch 2:         GPU 0 → GPU 1 → GPU 2 → GPU 3
```

**Use case**: Very deep models
**Limit**: bubble overhead (idle time)

### Type 4: ZeRO / Sharded Parallelism

```
Like DDP but shard model state across GPUs:
  GPU 0 owns parameters 0-25%
  GPU 1 owns parameters 25-50%
  ...

When needed: gather parameters → use → release
```

**Use case**: Model too big for DDP, simpler than TP+PP
**Most common in 2026**

---

## 3. ZeRO Stages

### ZeRO Stage 1: Optimizer State Sharding

```
Each GPU stores:
  Full model parameters (replicated)
  Full gradients (replicated)
  1/N of optimizer state (sharded)

Memory savings: ~4x on optimizer state
```

### ZeRO Stage 2: + Gradient Sharding

```
Each GPU stores:
  Full model parameters (replicated)
  1/N of gradients (sharded)
  1/N of optimizer state (sharded)

Memory savings: ~8x
```

### ZeRO Stage 3: + Parameter Sharding

```
Each GPU stores:
  1/N of parameters (sharded)
  1/N of gradients (sharded)
  1/N of optimizer state (sharded)

Memory savings: ~Nx (linear with GPU count)
```

### ZeRO-Infinity (offloading)

```
ZeRO-3 + offload to CPU/NVMe

Storage hierarchy:
  GPU memory (fastest)
  CPU memory (medium)
  NVMe SSD (slow but huge)

Can train 1T+ models on small clusters
```

---

## 4. PyTorch FSDP (Fully Sharded Data Parallel)

### What is FSDP

PyTorch native equivalent to ZeRO Stage 3

### Setup

```python
import torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.wrap import (
    transformer_auto_wrap_policy,
)
import functools

# Initialize distributed
torch.distributed.init_process_group("nccl")

# Auto-wrap transformer layers
auto_wrap_policy = functools.partial(
    transformer_auto_wrap_policy,
    transformer_layer_cls={LlamaDecoderLayer},
)

# Wrap model
model = LlamaForCausalLM(...).to(device)
model = FSDP(
    model,
    auto_wrap_policy=auto_wrap_policy,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # ZeRO-3
    mixed_precision=MixedPrecision(
        param_dtype=torch.bfloat16,
        reduce_dtype=torch.bfloat16,
        buffer_dtype=torch.bfloat16,
    ),
    device_id=torch.cuda.current_device(),
)
```

### Sharding Strategies

```python
# FULL_SHARD = ZeRO-3 (most memory efficient)
ShardingStrategy.FULL_SHARD

# SHARD_GRAD_OP = ZeRO-2 (faster, less savings)
ShardingStrategy.SHARD_GRAD_OP

# NO_SHARD = pure DDP (replicated)
ShardingStrategy.NO_SHARD

# HYBRID_SHARD = shard within node, replicate across nodes
ShardingStrategy.HYBRID_SHARD
```

### Mixed Precision

```python
# bfloat16 (recommended on H100/A100)
mp = MixedPrecision(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.bfloat16,
    buffer_dtype=torch.bfloat16,
)

# fp16 with grad scaling (older GPUs)
# Need GradScaler manually
```

### Activation Checkpointing

```python
from torch.distributed.algorithms._checkpoint.checkpoint_wrapper import (
    checkpoint_wrapper,
    CheckpointImpl,
)

# Wrap each transformer layer
non_reentrant_wrapper = functools.partial(
    checkpoint_wrapper,
    checkpoint_impl=CheckpointImpl.NO_REENTRANT,
)

apply_activation_checkpointing(
    model,
    checkpoint_wrapper_fn=non_reentrant_wrapper,
    check_fn=lambda submodule: isinstance(submodule, LlamaDecoderLayer),
)
```

**Trade-off**: 30% slower, but 50% memory savings

### Saving / Loading

```python
# Save (rank 0 only, gathered)
from torch.distributed.fsdp import FullStateDictConfig, StateDictType

save_policy = FullStateDictConfig(offload_to_cpu=True, rank0_only=True)
with FSDP.state_dict_type(model, StateDictType.FULL_STATE_DICT, save_policy):
    state_dict = model.state_dict()
    if rank == 0:
        torch.save(state_dict, "checkpoint.pt")

# Load (sharded loading from full checkpoint)
state_dict = torch.load("checkpoint.pt")
with FSDP.state_dict_type(model, StateDictType.FULL_STATE_DICT):
    model.load_state_dict(state_dict)
```

---

## 5. DeepSpeed (Microsoft)

### Why DeepSpeed

- Pioneered ZeRO
- ZeRO-Infinity (offload to CPU/NVMe)
- More features than FSDP
- More complex to set up

### Setup

```python
import deepspeed

# Config file
ds_config = {
    "train_batch_size": 32,
    "train_micro_batch_size_per_gpu": 4,
    "gradient_accumulation_steps": 2,
    "fp16": {"enabled": True},
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu", "pin_memory": True},
        "offload_param": {"device": "cpu", "pin_memory": True},
        "stage3_prefetch_bucket_size": 5e7,
        "stage3_max_live_parameters": 1e9,
    },
    "gradient_clipping": 1.0,
}

# Wrap
model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    config=ds_config,
    model_parameters=model.parameters()
)

# Train
for batch in dataloader:
    loss = model_engine(batch)
    model_engine.backward(loss)
    model_engine.step()
```

### When to use DeepSpeed vs FSDP

| Need | Tool |
|---|---|
| Standard 7B-70B fine-tune | **FSDP** (simpler) |
| Need CPU/NVMe offloading | **DeepSpeed** ZeRO-Infinity |
| Models > 100B | **DeepSpeed** + offload |
| Want PyTorch native | **FSDP** |
| Want most features | **DeepSpeed** |
| Production at scale | Both work; pick team familiarity |

---

## 6. Distributed Training Frameworks

### Hugging Face Accelerate

Simplest abstraction over FSDP/DeepSpeed:

```python
from accelerate import Accelerator

accelerator = Accelerator(
    mixed_precision="bf16",
    fsdp_plugin=FullyShardedDataParallelPlugin(...)
)

model, optimizer, dataloader = accelerator.prepare(
    model, optimizer, dataloader
)

for batch in dataloader:
    loss = model(batch)
    accelerator.backward(loss)
    optimizer.step()
```

```bash
# Launch
accelerate launch --config_file fsdp_config.yaml train.py
```

### PyTorch Lightning

```python
import pytorch_lightning as pl

trainer = pl.Trainer(
    accelerator="gpu",
    devices=8,
    strategy="fsdp",  # or "deepspeed_stage_3"
    precision="bf16-mixed",
)
trainer.fit(model, train_dataloader, val_dataloader)
```

### Ray Train (for clusters)

```python
from ray.train.torch import TorchTrainer
from ray.train import ScalingConfig

trainer = TorchTrainer(
    train_loop_per_worker=train_func,
    scaling_config=ScalingConfig(
        num_workers=8,
        use_gpu=True,
        resources_per_worker={"GPU": 1}
    )
)
result = trainer.fit()
```

---

## 7. Practical Setup: Multi-GPU Training

### Single Node, Multi-GPU

```bash
# 8 GPUs on one machine
torchrun --nproc_per_node=8 train.py

# Or with accelerate
accelerate launch --num_processes=8 train.py
```

### Multi-Node, Multi-GPU

```bash
# Master node (rank 0)
torchrun \
    --nnodes=4 \
    --nproc_per_node=8 \
    --rdzv_backend=c10d \
    --rdzv_endpoint=master_ip:29500 \
    train.py

# Worker nodes
torchrun \
    --nnodes=4 \
    --nproc_per_node=8 \
    --rdzv_backend=c10d \
    --rdzv_endpoint=master_ip:29500 \
    train.py
```

### SLURM Cluster

```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-node=8

srun torchrun \
    --nnodes=$SLURM_JOB_NUM_NODES \
    --nproc_per_node=$SLURM_GPUS_PER_NODE \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$SLURM_LAUNCH_NODE_IPADDR:29500 \
    train.py
```

### Cloud (Kubernetes + Kubeflow)

```yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: llama-finetune
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      template:
        spec:
          containers:
            - name: pytorch
              image: pytorch:2.5
              resources:
                limits:
                  nvidia.com/gpu: 8
    Worker:
      replicas: 3
      template:
        spec:
          containers:
            - name: pytorch
              image: pytorch:2.5
              resources:
                limits:
                  nvidia.com/gpu: 8
```

---

## 8. Memory Budget Calculation

### Components per Parameter

For each parameter (during training):
```
Parameter:    fp16/bf16 = 2 bytes
                fp32 = 4 bytes
Gradient:    same as parameter
Optimizer state (Adam):
  fp32 m:    4 bytes
  fp32 v:    4 bytes
  fp32 master copy: 4 bytes (mixed precision)
Total:       2 + 2 + 12 = 16 bytes per param (Adam mixed precision)
```

### Example: Llama-7B

```
7B parameters × 16 bytes = 112 GB just for training state
+ activations (depends on batch size)
+ buffers
= ~140-200 GB needed

Single A100 80GB: NOT ENOUGH
8× A100 with FSDP: 
  140 / 8 = 17.5 GB per GPU (fits comfortably with batch + activations)
```

### Memory Optimization

```
Mixed precision (bf16):       2x savings on params + grads
Optimizer offload (CPU):      ~12 bytes/param freed
Param offload (CPU/NVMe):     ~2 bytes/param freed
Activation checkpointing:     50%+ activation memory savings
Gradient accumulation:        smaller batch per step (less activations)
```

---

## 9. Troubleshooting Distributed Training

### Issue 1: NCCL Timeout
```
Error: Connection failure / NCCL timeout

Causes:
  - Network issues between nodes
  - Different software versions
  - Firewall blocking ports

Fix:
  - Check NCCL_DEBUG=INFO
  - Verify nccl-tests
  - Same PyTorch + CUDA versions across nodes
  - Open required ports (29500 typical)
```

### Issue 2: Hanging at start
```
Cause: Process discovery failing

Fix:
  Use rdzv_backend=c10d with shared endpoint
  Or use static IP/port not DNS
```

### Issue 3: OOM despite FSDP
```
Causes:
  - Activation memory not sharded
  - Batch size too large
  - Optimizer state not offloaded

Fix:
  - Enable activation checkpointing
  - Reduce micro-batch + use grad accumulation
  - DeepSpeed offload optimizer to CPU
```

### Issue 4: Slow training (worse than single GPU x N)
```
Causes:
  - Network bandwidth bottleneck
  - Communication overhead
  - Stragglers (one slow GPU)

Fix:
  - Use NVLink between GPUs
  - InfiniBand between nodes
  - Increase bucket size for grad reduction
  - Profile with PyTorch profiler
```

### Issue 5: NaN/Inf during training
```
Causes:
  - bf16 better than fp16 for stability
  - Gradient explosion
  - Bad initialization

Fix:
  - Use bf16 instead of fp16
  - Add gradient clipping (max_grad_norm=1.0)
  - Lower learning rate
  - Check loss spikes early in training
```

---

## 10. Performance Optimization

### Profiling

```python
# PyTorch profiler
from torch.profiler import profile, record_function, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True,
) as prof:
    for batch in dataloader:
        train_step(batch)

print(prof.key_averages().table(sort_by="cuda_time_total"))
prof.export_chrome_trace("trace.json")
```

### Common Bottlenecks

#### Compute-bound (GPU 100% utilization)
- Model architecture limit
- Bigger model or better algorithm needed

#### Memory-bound (GPU memory full)
- Activation checkpointing
- Smaller model
- Better quantization

#### Communication-bound (idle GPUs while syncing)
- Larger batch (more compute per sync)
- Faster interconnect (NVLink, InfiniBand)
- Different parallelism strategy
- Reduce gradient sync frequency

#### I/O-bound (waiting on data)
- Data loader workers (`num_workers > 0`)
- Pin memory (`pin_memory=True`)
- Cache data in RAM
- Prefetch batches

---

## 11. Mixed Precision Training

### Why Mixed Precision

- 2x memory savings (bf16 vs fp32)
- 2-4x speed on Tensor Cores
- Slight accuracy concerns (mostly safe)

### bf16 vs fp16

| | bf16 | fp16 |
|---|---|---|
| Range | Same as fp32 | Smaller |
| Precision | Lower mantissa | Higher mantissa |
| Stability | Very stable | Can NaN |
| Hardware | A100, H100, RTX 30/40 | All modern GPUs |
| Recommendation | **Use this** | Legacy |

### Implementation

```python
# Native PyTorch
with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
    output = model(input)
    loss = criterion(output, target)

# FP16 needs grad scaler (bf16 doesn't)
scaler = torch.cuda.amp.GradScaler()
loss.backward()
scaler.step(optimizer)
scaler.update()

# bf16 (no scaler needed)
loss.backward()
optimizer.step()
```

---

## 12. 8-bit and 4-bit Training

### 8-bit Optimizer (bitsandbytes)

```python
import bitsandbytes as bnb

# Replace Adam with 8-bit Adam
optimizer = bnb.optim.AdamW8bit(
    model.parameters(),
    lr=2e-5,
    weight_decay=0.01,
)
```

Saves ~75% on optimizer state memory

### 4-bit Quantization (QLoRA)

(Detailed in `../AI/01_Fine_Tuning_Deep.md`)

```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b",
    quantization_config=bnb_config,
)

# Now train with LoRA on top of 4-bit base
```

---

## 13. Cheat Sheet

### Q: "FSDP vs DeepSpeed?"
> "FSDP: PyTorch native, simpler, good for 7B-70B
> DeepSpeed: more features (ZeRO-Infinity for >100B with offload)
> 2026 default: FSDP for most cases"

### Q: "Memory budget สำหรับ training Llama-7B?"
> "16 bytes/param × 7B = 112 GB just state
> + activations (batch dependent)
> Need: 8× A100 80GB minimum with FSDP
> Or: 4× with optimizer offload"

### Q: "Activation checkpointing เปิดเมื่อไหร่?"
> "เปิดเสมอสำหรับ models > 1B
> Trade-off: 30% slower, 50% memory savings
> Worth it almost always — without it, OOM"

### Q: "bf16 vs fp16?"
> "bf16 ทุกครั้งที่ฮาร์ดแวร์รองรับ (A100, H100, RTX 30/40)
> Same range as fp32 = stable, no GradScaler needed
> fp16 only on older GPUs (V100, T4)"

### Q: "Why training slow despite 8 GPUs?"
> "Common: communication overhead
> 1. Profile to find bottleneck
> 2. Increase batch (more compute / sync)
> 3. NVLink/InfiniBand
> 4. Activation checkpointing
> 5. Mixed precision"

---

## Sources

- [Introducing PyTorch FSDP](https://pytorch.org/blog/introducing-pytorch-fully-sharded-data-parallel-api/)
- [DeepSpeed vs PyTorch FSDP: Which Distributed Training Framework in 2026?](https://vrlatech.com/deepspeed-vs-pytorch-fsdp-which-distributed-training-framework-in-2026/)
- [Everything about Distributed Training and Efficient Finetuning](https://sumanthrh.com/post/distributed-and-efficient-finetuning/)
- [FSDP vs DeepSpeed (Hugging Face)](https://huggingface.co/docs/accelerate/en/concept_guides/fsdp_and_deepspeed)
- [DeepSpeed Documentation](https://www.deepspeed.ai/training/)
- [PyTorch Lightning Model Parallel](https://lightning.ai/docs/pytorch/stable/advanced/model_parallel.html)
