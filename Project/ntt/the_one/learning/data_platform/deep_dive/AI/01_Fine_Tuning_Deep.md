# Fine-Tuning LLMs — Deep Dive

> LoRA, QLoRA, DoRA, DPO, RLHF, ORPO — รู้จักและเลือกใช้ให้ถูก
> ปี 2026 ของจริง: PEFT methods ครอง mainstream, full fine-tune หายาก

---

## 1. ทำไมต้อง Fine-Tune

### When Fine-Tune > Prompting

```
Fine-tune ดีกว่า prompting เมื่อ:
✓ Need consistent style (corporate tone, format)
✓ Domain knowledge ที่ RAG ไม่พอ
✓ Smaller model with task-specific quality
✓ Production cost (smaller model = cheaper)
✓ Tens of thousands of examples available
```

### When Prompting > Fine-Tune

```
Prompting ดีกว่าเมื่อ:
✓ Few examples (< 100)
✓ Knowledge changes frequently
✓ Need flexibility (can change behavior via prompt)
✓ Don't have training infra
✓ Frontier model already does well
```

### The Hierarchy of Adaptation (cheap → expensive)

```
1. Prompt engineering           (zero training)
2. Few-shot examples           (zero training)
3. RAG                          (zero training, just retrieval)
4. Prompt tuning                (small adapters trained)
5. LoRA / QLoRA                 (parameter-efficient)
6. Full fine-tuning             (all parameters)
7. Pre-training from scratch    (rare, $$$$)
```

---

## 2. Full Fine-Tuning (the baseline)

### What it Does

Update **all** parameters of the model on your data

### Cost

For 7B model:
```
Memory: ~16 bytes/param × 7B = 112 GB just for state
Hardware: 8× A100 80GB (FSDP)
Time: 1 epoch on 50K examples = ~6-12 hours
Cost: ~$1000-3000 for one fine-tune run
```

For 70B model:
```
Memory: 1.1 TB state
Hardware: 32× A100 minimum
Time: days
Cost: $10K+ per run
```

### When to Full Fine-Tune

- Substantial training data (>100K examples)
- Need maximum quality
- Have budget + infra
- Will use this model in production for years

### Implementation (Hugging Face)

```python
from transformers import AutoModelForCausalLM, Trainer, TrainingArguments

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    torch_dtype=torch.bfloat16,
)

args = TrainingArguments(
    output_dir="./model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    bf16=True,
    fsdp="full_shard auto_wrap",
    fsdp_transformer_layer_cls_to_wrap="LlamaDecoderLayer",
    save_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)
trainer.train()
```

---

## 3. LoRA (Low-Rank Adaptation) — Most Popular PEFT

### Core Idea

Don't update all weights. Train **small low-rank matrices** that modify weights.

```
Original layer:    W (4096 × 4096) — frozen
New addition:      A × B  
                   A: 4096 × r (r=16, small)
                   B: r × 4096
                   
Effective weight:  W + (A × B) × scaling
                   
Parameters trained: 4096 × 16 + 16 × 4096 = 131K
                    vs 4096 × 4096 = 16M
                    → 99% reduction
```

### Implementation (PEFT library)

```python
from peft import LoraConfig, get_peft_model, TaskType

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    torch_dtype=torch.bfloat16
)

lora_config = LoraConfig(
    r=16,                          # rank
    lora_alpha=16,                 # scaling factor
    target_modules=[               # which layers to adapt
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()
# trainable params: ~10M / 7B = 0.14% trainable

# Train normally
trainer = Trainer(model=model, ...)
trainer.train()

# Save (only adapter — small file)
model.save_pretrained("./lora_adapters")
# ~50 MB instead of 14 GB
```

### Key Hyperparameters

```python
r = 16          # rank: 4-64 typical, higher = more capacity
                # 8: lighter
                # 16: balanced
                # 32-64: more complex tasks

alpha = 16      # scaling: usually = r or 2r
                # actual scale = alpha / r

dropout = 0.05  # regularization

target_modules = "all-linear"  # 2026 default — hit all linear layers
```

### Inference

```python
# Option 1: Load adapter on top of base
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
model = PeftModel.from_pretrained(base, "./lora_adapters")

# Option 2: Merge for production (no adapter overhead)
model = model.merge_and_unload()
model.save_pretrained("./merged_model")
# Now it's a standalone model
```

### Pros & Cons

✅ 99% less memory needed
✅ Fast training (less compute)
✅ Tiny adapter file (easy to share)
✅ Multiple adapters per base model
✅ Zero inference latency (when merged)

❌ Lower quality than full fine-tune (~5% gap)
❌ Tuning r and target_modules takes experiments

---

## 4. QLoRA (Quantized LoRA)

### What QLoRA Adds

LoRA + 4-bit quantization of base model

```
Standard LoRA:  base_model fp16/bf16  + LoRA adapters bf16
QLoRA:          base_model 4-bit NF4  + LoRA adapters bf16
```

### Memory Savings

```
Llama-2-70B:
  fp16:        140 GB
  LoRA fp16:   ~140 GB (base same)
  QLoRA 4-bit: ~46 GB (4x smaller!)

Now fits on:
  Single A100 80GB!
  Or even RTX 4090 24GB for 7B-13B
```

### Implementation

```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",         # NF4 = NormalFloat 4-bit
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,    # double quantization (more memory savings)
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b",
    quantization_config=bnb_config,
    device_map="auto",
)

# Apply LoRA on top
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(...)
model = get_peft_model(model, lora_config)
```

### Quality Trade-off

QLoRA achieves **80-90% of full fine-tune quality** at 1/30th the cost

### When to Use QLoRA

✅ **Default for fine-tuning ปี 2026**
✅ Limited GPU memory
✅ Quick experiments
✅ 70B+ models on single GPU

---

## 5. DoRA (Weight-Decomposed LoRA, 2024+)

### What DoRA Adds

Decompose weight update into:
- **Magnitude** (how much to change)
- **Direction** (which way to change)

```
LoRA:    ΔW = α × A × B
DoRA:    W' = m * (W + αAB) / ||W + αAB||
         m: learned magnitude
         direction: normalized
```

### Why Better

LoRA tends to change magnitude more than direction
DoRA separates → better convergence on complex tasks

### Implementation

```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    use_dora=True,  # ← just turn on
    target_modules="all-linear",
    task_type="CAUSAL_LM"
)

model = get_peft_model(base_model, lora_config)
```

### Quality

DoRA closes the gap between LoRA and full fine-tune
**QDoRA** (combine with quantization) sometimes exceeds full fine-tune

### When to Use DoRA

- More complex tasks (DoRA helps most)
- Have budget for slightly slower training (~10% slower than LoRA)
- Want maximum quality from PEFT

---

## 6. PEFT Methods Comparison

| Method | Memory | Speed | Quality | Notes |
|---|---|---|---|---|
| Full FT | 100% | 100% | 100% | baseline |
| LoRA | 5-10% | 80-90% | 90-95% | classic PEFT |
| QLoRA | 1-3% | 60-70% | 85-90% | most popular |
| DoRA | 6-12% | 70-80% | 95-98% | better LoRA |
| QDoRA | 2-4% | 50-60% | 92-97% | best PEFT |
| Adapter (legacy) | 5-10% | 70% | 85-90% | older |
| Prefix Tuning | 1% | 90% | 80-85% | very small |
| (IA)³ | <1% | 95% | 85% | ultra-light |

### 2026 Default Recommendations

```
Generic fine-tune:    QLoRA (memory + quality balanced)
Quality critical:     QDoRA  (slight slower, +2-5% quality)
Many adapters:        LoRA (no quantization noise)
Edge deployment:      LoRA + merge (no overhead)
```

---

## 7. Preference Fine-Tuning (RLHF & friends)

### Why Preference Fine-Tuning

Standard fine-tuning (SFT):
- Learn from "good answer" examples
- Doesn't know what's "bad"

Preference fine-tuning:
- Learn from "this answer better than that answer"
- Aligns with human values

### Stage of LLM Training

```
1. Pre-training        (next token prediction on web)
2. SFT (Supervised)    (instruction-tuned on examples)
3. Preference tuning   (RLHF / DPO) ← alignment
```

### Data Format

```json
{
  "prompt": "Explain quantum computing",
  "chosen": "Quantum computing uses quantum mechanics... [helpful, accurate]",
  "rejected": "Quantum stuff makes computers fast [vague, low quality]"
}
```

---

## 8. RLHF (Reinforcement Learning from Human Feedback)

### Classic Pipeline (3 stages)

#### Stage 1: SFT (Supervised Fine-Tuning)
Train model on (prompt, ideal answer) pairs

#### Stage 2: Reward Model Training
```
Train reward model on (prompt, chosen, rejected):
  - Input: prompt + answer
  - Output: scalar score
  - Loss: chosen score > rejected score (Bradley-Terry)
```

#### Stage 3: PPO (Reinforcement Learning)
```
For each prompt:
  1. Generate answer with current policy
  2. Score with reward model
  3. Update policy: increase prob of high-reward generations
  4. KL penalty: don't drift too far from SFT
```

### Implementation (TRL library)

```python
from trl import PPOTrainer, PPOConfig
from transformers import AutoModelForCausalLM

# Load policy and reference (same model)
policy = AutoModelForCausalLM.from_pretrained("./sft_model")
ref = AutoModelForCausalLM.from_pretrained("./sft_model")

# Reward model (separately trained)
reward_model = AutoModelForSequenceClassification.from_pretrained("./reward_model")

ppo_config = PPOConfig(
    learning_rate=1.4e-5,
    batch_size=64,
    mini_batch_size=4,
    gradient_accumulation_steps=4,
    kl_coef=0.1,  # KL penalty
)

ppo_trainer = PPOTrainer(
    config=ppo_config,
    model=policy,
    ref_model=ref,
    reward_model=reward_model,
    tokenizer=tokenizer,
    dataset=prompt_dataset,
)

# Training loop
for batch in dataloader:
    # Generate
    response = policy.generate(batch.prompts)
    # Score
    rewards = reward_model(response)
    # Update
    ppo_trainer.step(batch.prompts, response, rewards)
```

### Cons of RLHF

❌ Complex (3 stages, 4 models in memory)
❌ Computationally expensive
❌ Sensitive to hyperparams
❌ Reward hacking risk
❌ Hard to debug

---

## 9. DPO (Direct Preference Optimization, 2023+)

### Why DPO

Mathematical insight: optimal RLHF policy can be derived in **closed form**
→ Skip reward model + PPO!

### How It Works

```
Loss = -log σ(β × [log π(chosen|x)/π_ref(chosen|x) - log π(rejected|x)/π_ref(rejected|x)])

Where:
  π    = current policy (being trained)
  π_ref = reference (frozen SFT model)
  β    = inverse temperature (regularization)
```

### Pseudocode

```python
def dpo_loss(model, ref_model, batch):
    # Get logits for chosen and rejected
    chosen_logits = model(batch.chosen).logits
    rejected_logits = model(batch.rejected).logits
    
    # Same for reference model
    with torch.no_grad():
        ref_chosen_logits = ref_model(batch.chosen).logits
        ref_rejected_logits = ref_model(batch.rejected).logits
    
    # Log probs
    chosen_logprob = log_prob(chosen_logits, batch.chosen)
    rejected_logprob = log_prob(rejected_logits, batch.rejected)
    ref_chosen_logprob = log_prob(ref_chosen_logits, batch.chosen)
    ref_rejected_logprob = log_prob(ref_rejected_logits, batch.rejected)
    
    # DPO loss
    chosen_reward = beta * (chosen_logprob - ref_chosen_logprob)
    rejected_reward = beta * (rejected_logprob - ref_rejected_logprob)
    
    loss = -F.logsigmoid(chosen_reward - rejected_reward)
    return loss.mean()
```

### Implementation (TRL)

```python
from trl import DPOTrainer

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,  # frozen SFT
    args=training_args,
    train_dataset=preference_dataset,
    tokenizer=tokenizer,
    beta=0.1,  # KL trade-off
)
dpo_trainer.train()
```

### DPO Pros

✅ Single training stage (vs RLHF 3 stages)
✅ Simpler implementation
✅ Comparable quality to PPO
✅ More stable training
✅ Cheaper (no reward model)

### DPO Cons

❌ Requires reference model (2 models in memory)
❌ Sensitive to β parameter
❌ Slightly worse on some benchmarks vs PPO
❌ Length bias (favors longer responses)

### When DPO

> **Default for alignment in 2026** — most teams use this

---

## 10. ORPO (Odds Ratio Preference Optimization, 2024+)

### What ORPO Adds

Eliminate reference model entirely!
Combines SFT + preference in one loss

### Formula

```
L_ORPO = L_SFT + λ * L_OR

L_SFT = -log P(chosen | prompt)  # standard SFT
L_OR = -log σ(log P(chosen)/P(rejected) × scaling)
```

### Key Insight

- SFT term: pull toward chosen
- OR term: push apart chosen vs rejected
- No reference model needed
- Single training run combines SFT + alignment

### Implementation

```python
from trl import ORPOTrainer, ORPOConfig

config = ORPOConfig(
    beta=0.1,
    learning_rate=8e-6,
    max_length=2048,
)

trainer = ORPOTrainer(
    model=model,
    args=config,
    train_dataset=preference_data,
    tokenizer=tokenizer,
)
trainer.train()
```

### ORPO Pros

✅ Single model in memory (vs 2 for DPO)
✅ One training run (vs SFT then DPO)
✅ Simpler pipeline
✅ Memory-efficient

### When ORPO

- Don't have SFT model yet (skip step)
- Memory-constrained
- Want simplest pipeline

---

## 11. Other Alignment Methods (2024-2026)

### KTO (Kahneman-Tversky Optimization)

```
Use only chosen OR rejected (not pairs)
Easier to collect data
Good when no pairs available
```

### IPO (Identity Preference Optimization)

```
Modified DPO loss
More robust to length bias
Better for some scenarios
```

### SimPO (Simple Preference Optimization)

```
DPO without reference model
Length-normalized rewards
Performant on benchmarks
```

### GRPO (Group Relative Policy Optimization, 2024+)

```
DeepSeek's variant
Used in DeepSeek-R1 reasoning
For verifiable tasks (math, code)
```

### DAPO

```
Newer (2025+)
Better stability
Used for some 2026 frontier models
```

---

## 12. Practical Fine-Tune Recipe (2026)

### Step 1: Pick Base Model

```
General: Llama 4, Qwen 3, Gemma 3
Code: DeepSeek Coder, Qwen Coder
Multilingual: Qwen 3, Aya
Fast/cheap: Phi 4, Gemma 3 small
```

### Step 2: Pick Data

```
SFT: 1K - 100K (prompt, ideal_response) pairs
   Quality > quantity (500 clean > 5000 noisy)

Preference (DPO/ORPO):
   1K - 50K (prompt, chosen, rejected) triples
```

### Step 3: Pick Method

```
Limited compute (1 GPU):       QLoRA + DPO/ORPO
Decent compute (4-8 GPU):      LoRA + DPO
Production max quality:        Full FT (rare)
```

### Step 4: Hyperparameters (sensible defaults)

```python
# QLoRA + DPO defaults that work
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules="all-linear",
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    use_dora=True,  # if compute allows
)

training_args = TrainingArguments(
    learning_rate=2e-4,           # higher than full FT (1e-5)
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    optim="paged_adamw_8bit",     # 8-bit Adam saves memory
    bf16=True,
    save_strategy="epoch",
)

dpo_args = DPOConfig(
    beta=0.1,                     # 0.05-0.5 typical
    max_length=2048,
    max_prompt_length=512,
)
```

### Step 5: Evaluate

```python
# Standard benchmarks
- MMLU, ARC, HellaSwag (general)
- HumanEval (code)
- AlpacaEval, MT-Bench (chat quality)

# Domain-specific
- Custom test set
- Human eval
- A/B vs base model
```

### Step 6: Deploy

```python
# Merge LoRA to base
model = model.merge_and_unload()

# Quantize for serving
from optimum.quanto import quantize, qint4
quantize(model, weights=qint4, activations=None)

# Or use vLLM with adapter
# vllm serve base_model --enable-lora --lora-modules my_lora=./adapter
```

---

## 13. Common Pitfalls

### Pitfall 1: Catastrophic Forgetting
```
Fine-tune too aggressively
   → forgets pre-training
   → general capabilities degrade

Fix:
- Lower learning rate
- Mix in pre-training data
- Use PEFT (preserves base)
- Early stopping
```

### Pitfall 2: Overfitting to Style
```
Train on 1000 customer service replies
   → model only knows that style
   → fails on new types of queries

Fix:
- Diverse training data
- Eval on held-out diverse set
- Regularization
```

### Pitfall 3: Reward Hacking (RLHF)
```
Reward model says "longer = better"
   → policy gives 5000-token answers
   → user hates verbosity

Fix:
- Better reward model
- Length penalty
- Use DPO instead (less hacking)
```

### Pitfall 4: Mode Collapse
```
Policy converges to same output
   → no diversity

Fix:
- Higher temperature in evaluation
- Beta higher in DPO
- Better data
```

### Pitfall 5: Tokenizer Mismatch
```
Use Llama tokenizer with Qwen model
   → garbage output
   
Always: same tokenizer as base model
```

### Pitfall 6: Bad Data Format
```
"Train on Q&A":  
  Bad: just newline-separated
  Good: proper chat template

Use tokenizer.apply_chat_template()
```

---

## 14. Cheat Sheet

### Q: "Fine-tune หรือ RAG?"
> "RAG: dynamic info, factual grounding (default)
> Fine-tune: consistent style, niche reasoning, smaller faster model
> ส่วนใหญ่ใช้ RAG ก่อน fine-tune ต่อยอดเฉพาะที่ RAG ไม่พอ"

### Q: "เริ่ม fine-tune จากไหน?"
> "1. SFT บน 1K-10K examples ก่อน (prove value)
> 2. ถ้าต้อง alignment → DPO ต่อ
> 3. Use QLoRA for efficiency
> 4. Llama 3 / Qwen 3 / Gemma เป็น good base"

### Q: "LoRA r ตั้งเท่าไหร่?"
> "r=16 default, alpha=16
> r=8 ถ้า simple task
> r=32-64 ถ้า complex task
> ใช้ all-linear target_modules — 2026 default"

### Q: "DPO vs PPO/RLHF?"
> "DPO: simpler, single stage, 80-95% of PPO quality
> PPO/RLHF: gold standard, but complex + expensive
> ปี 2026 default: DPO (then ORPO if want even simpler)"

### Q: "QLoRA vs full FT?"
> "QLoRA: 80-90% quality, 1-3% memory, 30x cheaper
> Full FT: max quality, expensive
> Most practitioners 2026: QLoRA default — full FT only when budget + quality critical"

---

## Sources

- [Comprehensive Guide to Fine-Tuning LLMs with LoRA and QLoRA in 2026](https://explore.n1n.ai/blog/fine-tune-llm-lora-qlora-guide-2026-2026-04-17)
- [In-depth guide to fine-tuning LLMs with LoRA and QLoRA](https://www.mercity.ai/blog-post/guide-to-fine-tuning-llms-with-lora-and-qlora/)
- [Introducing DoRA, a High-Performing Alternative to LoRA](https://developer.nvidia.com/blog/introducing-dora-a-high-performing-alternative-to-lora-for-fine-tuning/)
- [LoRA vs. QLoRA - Red Hat](https://www.redhat.com/en/topics/ai/lora-vs-qlora)
- [Direct Preference Optimization (DPO) - Cameron Wolfe](https://cameronrwolfe.substack.com/p/direct-preference-optimization)
- [DPO arXiv Paper](https://arxiv.org/abs/2305.18290)
- [RLHF vs DPO vs PPO: How to Align LLMs](https://mljourney.com/rlhf-vs-dpo-vs-ppo-how-to-align-llms-without-losing-your-mind/)
- [PEFT Beyond LoRA: Advanced Parameter-Efficient Fine-Tuning](https://mbrenndoerfer.com/writing/peft-beyond-lora-advanced-parameter-efficient-finetuning-techniques)
- [Hugging Face PEFT Library](https://huggingface.co/docs/peft)
- [TRL Library Documentation](https://huggingface.co/docs/trl)
