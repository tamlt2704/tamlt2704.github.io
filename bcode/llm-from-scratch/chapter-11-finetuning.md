# Chapter 11: Fine-Tuning — From Text Completion to Instruction Following

[← Chapter 10: Scaling](chapter-10-scaling.md) | [Chapter 12: Evaluation →](chapter-12-eval.md)

---

## The Problem

Our pretrained model is a text completion engine. Give it "The capital of France is" and it might continue with "Paris, which is known for..." — but it might also continue with "a question often asked in geography class." It doesn't understand that you're asking a question.

Dr. Lin: "Pretraining teaches the model language. Fine-tuning teaches it behavior. The same model that generates random Shakespeare can be taught to follow instructions, answer questions, and refuse harmful requests. The architecture doesn't change — only the training data does."

## Supervised Fine-Tuning (SFT)

SFT trains the model on (instruction, response) pairs. The model learns to generate helpful responses given instructions.

### Instruction Format

```
### Instruction:
What is the capital of France?

### Response:
The capital of France is Paris.
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# ─── Instruction Dataset ──────────────────────────────────────────────────────

class InstructionDataset(Dataset):
    """Dataset of instruction-response pairs for SFT."""

    def __init__(self, examples: list[dict], tokenizer, block_size: int):
        """
        examples: [{"instruction": "...", "response": "..."}, ...]
        """
        self.tokenizer = tokenizer
        self.block_size = block_size
        self.data = []

        for ex in examples:
            # Format as a single sequence
            text = self.format_example(ex)
            tokens = tokenizer.encode(text)

            if len(tokens) <= block_size:
                # Pad to block_size
                tokens = tokens + [0] * (block_size - len(tokens))
                self.data.append(torch.tensor(tokens, dtype=torch.long))

    def format_example(self, ex):
        return (
            f"### Instruction:\n{ex['instruction']}\n\n"
            f"### Response:\n{ex['response']}\n"
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        tokens = self.data[idx]
        x = tokens[:-1]
        y = tokens[1:]
        return x, y


# ─── Example Training Data ────────────────────────────────────────────────────

instruction_examples = [
    {"instruction": "What is the capital of France?",
     "response": "The capital of France is Paris."},
    {"instruction": "Write a haiku about programming.",
     "response": "Code flows like water\nBugs hide in the deepest pools\nTests reveal the truth"},
    {"instruction": "Explain gravity in one sentence.",
     "response": "Gravity is the force that attracts objects with mass toward each other."},
    {"instruction": "Translate 'hello' to Spanish.",
     "response": "Hello in Spanish is 'hola'."},
    {"instruction": "What is 2 + 2?",
     "response": "2 + 2 equals 4."},
    # In practice, you'd have thousands of these
]

print(f"Training examples: {len(instruction_examples)}")
print(f"\nFormatted example:")
print(InstructionDataset.format_example(None, instruction_examples[0]))
```

### SFT Training Loop

```python
def sft_train(model, dataset, epochs=3, lr=2e-5, device='cuda'):
    """Supervised fine-tuning on instruction data."""
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            _, loss = model(x, y)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")

# Usage:
# sft_train(model, instruction_dataset, epochs=3, lr=2e-5)
```

## LoRA: Efficient Fine-Tuning

Full fine-tuning updates all parameters. For a 7B model, that's 7 billion floats in memory for gradients + optimizer states. LoRA (Low-Rank Adaptation) freezes the base model and adds tiny trainable matrices.

### The Idea

Instead of updating a weight matrix W directly:
```
W_new = W + ΔW    (ΔW is full-rank, same size as W)
```

LoRA decomposes the update into two small matrices:
```
W_new = W + B @ A    (A is d×r, B is r×d, where r << d)
```

If W is 768×768 (589,824 params), and rank r=8:
- A: 768×8 = 6,144 params
- B: 8×768 = 6,144 params
- Total: 12,288 params (2% of original!)

```python
# ─── LoRA Implementation ──────────────────────────────────────────────────────

class LoRALinear(nn.Module):
    """Linear layer with LoRA adaptation."""

    def __init__(self, original_linear: nn.Linear, rank: int = 8, alpha: float = 16.0):
        super().__init__()
        in_features = original_linear.in_features
        out_features = original_linear.out_features

        # Freeze original weights
        self.linear = original_linear
        self.linear.weight.requires_grad = False
        if self.linear.bias is not None:
            self.linear.bias.requires_grad = False

        # LoRA matrices
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))

        # Scaling factor
        self.scaling = alpha / rank

    def forward(self, x):
        # Original output + LoRA adaptation
        base_output = self.linear(x)
        lora_output = (x @ self.lora_A @ self.lora_B) * self.scaling
        return base_output + lora_output


def apply_lora(model, rank=8, alpha=16.0, target_modules=None):
    """Apply LoRA to specified linear layers in the model."""
    if target_modules is None:
        target_modules = ['W_Q', 'W_K', 'W_V', 'proj']  # attention layers

    lora_params = 0
    frozen_params = 0

    for name, module in model.named_modules():
        for attr_name in target_modules:
            if hasattr(module, attr_name):
                original = getattr(module, attr_name)
                if isinstance(original, nn.Linear):
                    lora_layer = LoRALinear(original, rank=rank, alpha=alpha)
                    setattr(module, attr_name, lora_layer)
                    lora_params += rank * (original.in_features + original.out_features)

    # Freeze all non-LoRA parameters
    for name, param in model.named_parameters():
        if 'lora_' not in name:
            param.requires_grad = False
            frozen_params += param.numel()
        else:
            lora_params += 0  # already counted

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters:     {total:,}")
    print(f"Trainable (LoRA):     {trainable:,} ({100*trainable/total:.2f}%)")
    print(f"Frozen:               {total - trainable:,}")

    return model


# Usage:
# model = GPT(config).to(device)
# model.load_state_dict(pretrained_weights)  # load pretrained
# model = apply_lora(model, rank=8)          # add LoRA
# sft_train(model, instruction_dataset)      # fine-tune (only LoRA params update)
```

Output:
```
Total parameters:     10,788,929
Trainable (LoRA):     73,728 (0.68%)
Frozen:               10,715,201
```

Only 0.68% of parameters are trainable! Training is much faster and uses much less memory.

### Merging LoRA Weights

After training, merge LoRA weights back into the base model for inference (no overhead):

```python
def merge_lora(model):
    """Merge LoRA weights into base model for efficient inference."""
    for module in model.modules():
        if isinstance(module, LoRALinear):
            # W_merged = W + B @ A * scaling
            merged_weight = (
                module.linear.weight.data +
                (module.lora_B.T @ module.lora_A.T) * module.scaling
            )
            module.linear.weight.data = merged_weight
    print("LoRA weights merged into base model.")
```

## RLHF Overview

After SFT, models can be further aligned using Reinforcement Learning from Human Feedback:

```
1. SFT Model generates multiple responses to a prompt
2. Human ranks the responses (best to worst)
3. Train a Reward Model to predict human preferences
4. Use PPO (or DPO) to optimize the SFT model against the reward model
```

```python
# ─── RLHF Conceptual Pipeline ────────────────────────────────────────────────

"""
Step 1: Supervised Fine-Tuning (what we did above)
  - Train on (instruction, good_response) pairs

Step 2: Reward Model Training
  - Collect pairs: (prompt, response_A, response_B, preference)
  - Train a model to predict which response humans prefer
  - reward_model(prompt, response) → scalar score

Step 3: PPO Training
  - For each prompt:
    - Generate response with current policy (SFT model)
    - Score with reward model
    - Update policy to maximize reward (with KL penalty to stay near SFT)

Simplified DPO (Direct Preference Optimization) — no reward model needed:
  - Directly optimize the policy from preference pairs
  - Loss = -log(σ(β * (log π(y_w|x) - log π(y_l|x))))
  - Where y_w = preferred response, y_l = rejected response
"""

class DPOTrainer:
    """Simplified Direct Preference Optimization."""

    def __init__(self, model, ref_model, beta=0.1, lr=1e-6):
        self.model = model
        self.ref_model = ref_model  # frozen copy of SFT model
        self.beta = beta
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    def compute_log_probs(self, model, input_ids, labels):
        """Compute log probabilities of labels under model."""
        logits, _ = model(input_ids)
        log_probs = F.log_softmax(logits, dim=-1)
        # Gather log probs for actual tokens
        token_log_probs = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
        return token_log_probs.sum(dim=-1)

    def train_step(self, prompt_ids, chosen_ids, rejected_ids):
        """One DPO training step."""
        # Log probs under current policy
        pi_chosen = self.compute_log_probs(self.model, prompt_ids, chosen_ids)
        pi_rejected = self.compute_log_probs(self.model, prompt_ids, rejected_ids)

        # Log probs under reference (frozen SFT) model
        with torch.no_grad():
            ref_chosen = self.compute_log_probs(self.ref_model, prompt_ids, chosen_ids)
            ref_rejected = self.compute_log_probs(self.ref_model, prompt_ids, rejected_ids)

        # DPO loss
        log_ratio_chosen = pi_chosen - ref_chosen
        log_ratio_rejected = pi_rejected - ref_rejected
        loss = -F.logsigmoid(self.beta * (log_ratio_chosen - log_ratio_rejected)).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
```

## The Full Pipeline

```
Raw Text Corpus (TB of data)
    │
    ▼ Pretraining (weeks on many GPUs)
Base Model (text completion)
    │
    ▼ SFT (hours on few GPUs)
Instruction-Following Model
    │
    ▼ RLHF/DPO (days on few GPUs)
Aligned Model (helpful, harmless, honest)
```

## What You Learned

- **SFT (Supervised Fine-Tuning)** — train on instruction/response pairs to teach behavior
- **Instruction format** — structured prompt template the model learns to follow
- **LoRA** — efficient fine-tuning by adding small trainable matrices (< 1% of params)
- **Weight merging** — combine LoRA weights back into base model for inference
- **RLHF** — align model with human preferences using reward models
- **DPO** — simpler alternative to RLHF that skips the reward model
- **The pipeline** — pretrain → SFT → RLHF = how ChatGPT-style models are made

We can now train and fine-tune our model. But how do we know if it's any good? Next: evaluation metrics, inference optimization, and deployment.

---

[← Chapter 10: Scaling](chapter-10-scaling.md) | [Chapter 12: Evaluation →](chapter-12-eval.md)
