# Chapter 8: Fine-tuning

[prev: Scaling](chapter-07-scaling.md) | [next: Inference and Deployment](chapter-09-inference.md)

Pre-training gives the model general language ability. Fine-tuning specializes it for specific tasks like instruction following, chat, or code generation.

## Supervised Fine-Tuning (SFT)

Train on (instruction, response) pairs with the same next-token prediction objective, but only compute loss on the response tokens:

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset

class InstructionDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=512):
        """
        data: list of {"instruction": str, "response": str}
        """
        self.examples = []
        for item in data:
            prompt = f"### Instruction:\n{item['instruction']}\n\n### Response:\n"
            full = prompt + item["response"]
            ids = tokenizer.encode(full)[:max_len]
            prompt_len = len(tokenizer.encode(prompt))
            self.examples.append((ids, prompt_len))

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ids, prompt_len = self.examples[idx]
        x = torch.tensor(ids[:-1], dtype=torch.long)
        y = torch.tensor(ids[1:], dtype=torch.long)

        # Mask loss on prompt tokens (only train on response)
        loss_mask = torch.zeros_like(y)
        loss_mask[prompt_len - 1:] = 1.0
        return x, y, loss_mask

def sft_loss(logits, targets, loss_mask):
    """
    logits: (batch, seq_len, vocab_size)
    targets: (batch, seq_len)
    loss_mask: (batch, seq_len) — 1 for response tokens, 0 for prompt
    """
    loss = nn.functional.cross_entropy(
        logits.view(-1, logits.size(-1)),
        targets.view(-1),
        reduction="none"
    )  # (batch * seq_len,)
    loss = loss.view(targets.shape)  # (batch, seq_len)
    loss = (loss * loss_mask).sum() / loss_mask.sum()
    return loss
```

## LoRA (Low-Rank Adaptation) from Scratch

Instead of updating all parameters, LoRA adds small trainable matrices to frozen weights:

`W_new = W_frozen + (A @ B) * (alpha / rank)`

Where A is `(d, r)` and B is `(r, d)` with rank `r` much smaller than `d`.

```python
import torch
import torch.nn as nn
import math

class LoRALinear(nn.Module):
    def __init__(self, original_linear, rank=8, alpha=16):
        super().__init__()
        self.original = original_linear
        self.original.weight.requires_grad_(False)  # Freeze original

        in_features = original_linear.in_features
        out_features = original_linear.out_features

        # Low-rank matrices
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) / math.sqrt(rank))
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        self.scaling = alpha / rank

    def forward(self, x):
        # x shape: (batch, seq_len, in_features)
        base_output = self.original(x)  # (batch, seq_len, out_features)
        lora_output = (x @ self.lora_A @ self.lora_B) * self.scaling
        return base_output + lora_output

def apply_lora(model, rank=8, alpha=16, target_modules=("W_qkv", "W_out")):
    """Replace target linear layers with LoRA versions."""
    for name, module in model.named_modules():
        for attr_name in target_modules:
            if hasattr(module, attr_name):
                original = getattr(module, attr_name)
                if isinstance(original, nn.Linear):
                    setattr(module, attr_name, LoRALinear(original, rank, alpha))

    # Count trainable params
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable: {trainable/1e6:.2f}M / {total/1e6:.2f}M "
          f"({100*trainable/total:.2f}%)")
    return model

# Usage: typically trains only 0.1-1% of parameters
# model = apply_lora(model, rank=16, alpha=32)
```

## QLoRA (Quantized LoRA)

QLoRA quantizes the base model to 4-bit, then applies LoRA on top. This allows fine-tuning a 7B model on a single 24GB GPU:

```python
import torch
import torch.nn as nn

class QuantizedLinear(nn.Module):
    """Simplified 4-bit quantized linear (conceptual implementation)."""

    def __init__(self, weight, group_size=128):
        super().__init__()
        # Quantize weight to 4-bit with group-wise scaling
        self.group_size = group_size
        n_groups = weight.shape[1] // group_size

        # Compute scale per group
        w_grouped = weight.reshape(weight.shape[0], n_groups, group_size)
        scales = w_grouped.abs().max(dim=-1).values  # (out, n_groups)

        # Quantize to 4-bit range [-8, 7]
        w_quantized = torch.round(w_grouped / scales.unsqueeze(-1) * 7)
        w_quantized = w_quantized.clamp(-8, 7).to(torch.int8)

        self.register_buffer("weight_quantized", w_quantized)
        self.register_buffer("scales", scales)

    def forward(self, x):
        # Dequantize on-the-fly
        w = self.weight_quantized.float() * self.scales.unsqueeze(-1) / 7
        w = w.reshape(w.shape[0], -1)  # (out_features, in_features)
        return x @ w.T

# QLoRA = QuantizedLinear (frozen) + LoRA adapters (trainable)
# In practice, use bitsandbytes library:
# from bitsandbytes import nn as bnb
# model = AutoModelForCausalLM.from_pretrained(..., load_in_4bit=True)
```

## RLHF Overview (Reward Model + PPO)

RLHF aligns the model with human preferences in three stages:

**Stage 1**: SFT (covered above)

**Stage 2**: Train a reward model on human preference data:

```python
import torch
import torch.nn as nn

class RewardModel(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.base = base_model  # Pre-trained GPT (frozen or fine-tuned)
        self.reward_head = nn.Linear(base_model.ln_final.weight.shape[0], 1)

    def forward(self, token_ids):
        # token_ids: (batch, seq_len)
        # Get last hidden state
        with torch.no_grad():
            logits = self.base(token_ids)
        # Use the hidden state before lm_head (hack: get from hook or modify model)
        # Simplified: use mean of logits as features
        hidden = logits.mean(dim=-1)  # (batch, seq_len)
        reward = self.reward_head(hidden[:, -1:, :].squeeze())  # (batch, 1)
        return reward

def reward_model_loss(reward_chosen, reward_rejected):
    """Bradley-Terry preference model loss."""
    # We want reward_chosen > reward_rejected
    return -torch.log(torch.sigmoid(reward_chosen - reward_rejected)).mean()
```

**Stage 3**: PPO optimization (simplified):

```python
import torch

def ppo_step(model, ref_model, reward_model, prompts, optimizer,
             clip_epsilon=0.2, kl_coeff=0.1):
    """Simplified PPO update for language model alignment."""
    # Generate responses from current model
    with torch.no_grad():
        responses = generate(model, prompts, max_new_tokens=128)
        rewards = reward_model(responses)

        # Reference model log probs (for KL penalty)
        ref_logits = ref_model(responses)
        ref_log_probs = torch.log_softmax(ref_logits, dim=-1)

    # Current model log probs
    logits = model(responses)
    log_probs = torch.log_softmax(logits, dim=-1)

    # KL divergence penalty
    kl = (torch.exp(log_probs) * (log_probs - ref_log_probs)).sum(dim=-1).mean()

    # PPO objective (simplified)
    loss = -(rewards - kl_coeff * kl).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()
```

## DPO (Direct Preference Optimization)

DPO skips the reward model entirely. It directly optimizes the policy using preference pairs:

```python
import torch
import torch.nn.functional as F

def dpo_loss(model, ref_model, chosen_ids, rejected_ids, beta=0.1):
    """
    Direct Preference Optimization loss.
    chosen_ids: (batch, seq_len) — preferred responses
    rejected_ids: (batch, seq_len) — dispreferred responses
    beta: temperature parameter controlling deviation from reference
    """
    # Get log probabilities from policy model
    chosen_logits = model(chosen_ids)
    rejected_logits = model(rejected_ids)
    chosen_logprobs = get_sequence_logprobs(chosen_logits, chosen_ids)
    rejected_logprobs = get_sequence_logprobs(rejected_logits, rejected_ids)

    # Get log probabilities from reference model (frozen)
    with torch.no_grad():
        ref_chosen_logits = ref_model(chosen_ids)
        ref_rejected_logits = ref_model(rejected_ids)
        ref_chosen_logprobs = get_sequence_logprobs(ref_chosen_logits, chosen_ids)
        ref_rejected_logprobs = get_sequence_logprobs(ref_rejected_logits, rejected_ids)

    # DPO loss: log-sigmoid of scaled preference margin
    chosen_reward = beta * (chosen_logprobs - ref_chosen_logprobs)
    rejected_reward = beta * (rejected_logprobs - ref_rejected_logprobs)

    loss = -F.logsigmoid(chosen_reward - rejected_reward).mean()
    return loss

def get_sequence_logprobs(logits, ids):
    """Sum of log probs for each token in the sequence."""
    # logits: (batch, seq_len, vocab_size)
    # ids: (batch, seq_len)
    log_probs = torch.log_softmax(logits[:, :-1, :], dim=-1)
    token_log_probs = log_probs.gather(-1, ids[:, 1:].unsqueeze(-1)).squeeze(-1)
    return token_log_probs.sum(dim=-1)  # (batch,)
```

**DPO vs RLHF**: DPO is simpler (no reward model, no PPO), more stable, and often performs comparably.

## Evaluation

### Perplexity

```python
import torch
import math

@torch.no_grad()
def evaluate_perplexity(model, dataloader, device="cuda"):
    model.eval()
    total_loss = 0.0
    total_tokens = 0

    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)), y.view(-1), reduction="sum"
        )
        total_loss += loss.item()
        total_tokens += y.numel()

    avg_loss = total_loss / total_tokens
    perplexity = math.exp(avg_loss)
    return perplexity
```

### Common Benchmarks

| Benchmark  | What it measures                   |
| ---------- | ---------------------------------- |
| MMLU       | Multi-task knowledge (57 subjects) |
| HellaSwag  | Commonsense reasoning              |
| HumanEval  | Code generation                    |
| TruthfulQA | Factual accuracy                   |
| GSM8K      | Math reasoning                     |
| MT-Bench   | Multi-turn chat quality            |

## Key Takeaways

- SFT teaches the model to follow instructions using (prompt, response) pairs
- LoRA reduces trainable parameters to less than 1% while maintaining quality
- QLoRA enables fine-tuning large models on consumer GPUs
- RLHF aligns models with human preferences but is complex (3 stages)
- DPO achieves similar alignment with a single training stage
- Always evaluate on held-out data; perplexity alone does not capture quality
