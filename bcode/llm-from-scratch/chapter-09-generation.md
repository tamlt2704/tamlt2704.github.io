# Chapter 9: Text Generation — Sampling Strategies

[← Chapter 8: Data Pipeline](chapter-08-data.md) | [Chapter 10: Scaling →](chapter-10-scaling.md)

---

## The Problem

Our model computes logits and loss during training, but generation is just "sample from softmax." The output is often repetitive, incoherent, or too random. We need control over the generation process.

Dr. Lin: "A trained model gives you a probability distribution over the next token. HOW you sample from that distribution changes everything. Greedy decoding is boring. Pure random sampling is chaotic. The art is in between."

## The Generation Problem

At each step, the model outputs logits for every token in the vocabulary:

```
logits = [2.1, -0.5, 3.8, 0.2, -1.1, ...]  (65 values for char-level)
```

We need to pick ONE token. How?

## Strategy 1: Greedy Decoding

Always pick the highest-probability token.

```python
import torch
import torch.nn.functional as F

def generate_greedy(model, idx, max_new_tokens):
    """Always pick the most likely next token."""
    model.eval()
    with torch.no_grad():
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -model.config.block_size:]
            logits, _ = model(idx_cond)
            logits = logits[:, -1, :]  # last position
            idx_next = logits.argmax(dim=-1, keepdim=True)  # highest prob
            idx = torch.cat([idx, idx_next], dim=1)
    return idx
```

**Problem**: greedy decoding produces repetitive, boring text. The model gets stuck in loops:
```
"The king the king the king the king..."
```

It always picks the "safe" choice, never exploring interesting continuations.

## Strategy 2: Temperature Sampling

Scale logits before softmax. Temperature controls randomness:
- `T < 1.0` → sharper distribution (more confident, less random)
- `T = 1.0` → original distribution
- `T > 1.0` → flatter distribution (more random, more creative)

```python
def generate_temperature(model, idx, max_new_tokens, temperature=1.0):
    """Sample with temperature scaling."""
    model.eval()
    with torch.no_grad():
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -model.config.block_size:]
            logits, _ = model(idx_cond)
            logits = logits[:, -1, :] / temperature  # scale by temperature
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
    return idx
```

Example with different temperatures:
```
T=0.1: "The king said to the queen, 'I shall return to the castle.'"
        (safe, predictable, potentially repetitive)

T=0.8: "The king whispered to his faithful servant, 'Bring me the sword.'"
        (natural, varied, coherent)

T=1.5: "The king danced upon the moonlit xylophone of forgotten dreams!"
        (creative but potentially nonsensical)
```

## Strategy 3: Top-k Sampling

Only consider the top k most likely tokens. Zero out everything else.

```python
def generate_top_k(model, idx, max_new_tokens, temperature=1.0, top_k=40):
    """Sample from only the top-k most likely tokens."""
    model.eval()
    with torch.no_grad():
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -model.config.block_size:]
            logits, _ = model(idx_cond)
            logits = logits[:, -1, :] / temperature

            # Keep only top-k tokens
            if top_k is not None:
                # Find the top-k values
                top_k_values, _ = torch.topk(logits, top_k, dim=-1)
                # Get the minimum value in top-k
                min_top_k = top_k_values[:, -1].unsqueeze(-1)
                # Zero out everything below the threshold
                logits = logits.masked_fill(logits < min_top_k, float('-inf'))

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
    return idx
```

**Why top-k helps**: it prevents sampling from the "long tail" of unlikely tokens. Without it, the model occasionally picks bizarre tokens (probability 0.001) that derail the text.

**Problem with top-k**: the right k depends on context. Sometimes only 3 tokens make sense ("The capital of France is ___"), sometimes 100 do ("I like to eat ___").

## Strategy 4: Top-p (Nucleus) Sampling

Instead of a fixed number of tokens, keep the smallest set whose cumulative probability exceeds p.

```python
def generate_top_p(model, idx, max_new_tokens, temperature=1.0, top_p=0.9):
    """Nucleus sampling: keep smallest set of tokens with cumulative prob >= top_p."""
    model.eval()
    with torch.no_grad():
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -model.config.block_size:]
            logits, _ = model(idx_cond)
            logits = logits[:, -1, :] / temperature

            # Sort by probability (descending)
            sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
            sorted_probs = F.softmax(sorted_logits, dim=-1)

            # Cumulative probability
            cumulative_probs = torch.cumsum(sorted_probs, dim=-1)

            # Find cutoff: first position where cumulative prob exceeds top_p
            # Shift right so we keep the token that crosses the threshold
            sorted_mask = cumulative_probs - sorted_probs > top_p

            # Zero out tokens beyond the nucleus
            sorted_logits = sorted_logits.masked_fill(sorted_mask, float('-inf'))

            # Unsort back to original order
            logits = torch.zeros_like(logits).scatter_(
                dim=-1, index=sorted_indices, src=sorted_logits
            )

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
    return idx
```

**Why top-p is better than top-k**: it adapts to the distribution. When the model is confident (one token has 95% probability), nucleus sampling picks from ~1-2 tokens. When uncertain, it considers many.

## The Complete Generate Function

Combining all strategies:

```python
@torch.no_grad()
def generate(
    model,
    idx,
    max_new_tokens,
    temperature=1.0,
    top_k=None,
    top_p=None,
    repetition_penalty=1.0,
):
    """
    Full-featured text generation.

    Args:
        model: trained GPT model
        idx: starting token indices (B, T)
        max_new_tokens: how many tokens to generate
        temperature: randomness (0.1=focused, 1.0=normal, 1.5=creative)
        top_k: if set, only sample from top-k tokens
        top_p: if set, nucleus sampling threshold
        repetition_penalty: penalize tokens that already appeared (>1.0 = less repetition)
    """
    model.eval()
    block_size = model.config.block_size

    for _ in range(max_new_tokens):
        # Crop context to block_size
        idx_cond = idx[:, -block_size:]

        # Forward pass
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :]  # (B, vocab_size)

        # Repetition penalty: reduce logits for tokens already generated
        if repetition_penalty != 1.0:
            for i in range(idx.shape[0]):
                generated_tokens = idx[i].unique()
                logits[i, generated_tokens] /= repetition_penalty

        # Temperature
        logits = logits / temperature

        # Top-k filtering
        if top_k is not None:
            top_k_values, _ = torch.topk(logits, min(top_k, logits.size(-1)), dim=-1)
            min_val = top_k_values[:, -1].unsqueeze(-1)
            logits = logits.masked_fill(logits < min_val, float('-inf'))

        # Top-p (nucleus) filtering
        if top_p is not None:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
            sorted_probs = F.softmax(sorted_logits, dim=-1)
            cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
            sorted_mask = (cumulative_probs - sorted_probs) > top_p
            sorted_logits = sorted_logits.masked_fill(sorted_mask, float('-inf'))
            logits = torch.zeros_like(logits).scatter_(
                dim=-1, index=sorted_indices, src=sorted_logits
            )

        # Sample
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        idx = torch.cat([idx, idx_next], dim=1)

    return idx
```

## Comparing Strategies

```python
import os
import urllib.request

# Assuming model is trained (from Chapter 7)...
# Here's how you'd compare strategies:

def compare_strategies(model, tokenizer, prompt="KING HENRY:", device='cpu'):
    """Generate with different strategies and compare."""
    # Encode prompt
    prompt_tokens = torch.tensor(
        [tokenizer.encode(prompt)], dtype=torch.long, device=device
    )

    strategies = [
        ("Greedy",           dict(temperature=0.01)),
        ("Temp=0.5",         dict(temperature=0.5)),
        ("Temp=1.0",         dict(temperature=1.0)),
        ("Top-k=10",         dict(temperature=0.8, top_k=10)),
        ("Top-k=40",         dict(temperature=0.8, top_k=40)),
        ("Top-p=0.9",        dict(temperature=0.8, top_p=0.9)),
        ("Top-p=0.95",       dict(temperature=0.8, top_p=0.95)),
        ("Rep penalty=1.2",  dict(temperature=0.8, top_p=0.9, repetition_penalty=1.2)),
    ]

    for name, kwargs in strategies:
        output = generate(model, prompt_tokens.clone(), max_new_tokens=100, **kwargs)
        text = tokenizer.decode(output[0].tolist())
        # Show first 2 lines after prompt
        lines = text[len(prompt):].strip().split('\n')[:2]
        print(f"{name:20s} | {' / '.join(lines)}")
```

Expected output:
```
Greedy               | My lord, I am the king. / My lord, I am the king.
Temp=0.5             | My lord, what news from France? / The duke hath sent his men.
Temp=1.0             | What tidings bring you here? / A messenger from York.
Top-k=10             | My lord, the duke approaches. / With twenty thousand men.
Top-k=40             | Good morrow, cousin. What say you? / I fear the worst.
Top-p=0.9            | The time is come for war. / Let us march upon the field.
Top-p=0.95           | Speak, herald! What news? / The enemy retreats to London.
Rep penalty=1.2      | Now hear me well, good lords. / We must decide our course.
```

## Practical Recommendations

| Use Case | Settings |
|---|---|
| Factual/deterministic | temperature=0.1 or greedy |
| Creative writing | temperature=0.8, top_p=0.9 |
| Code generation | temperature=0.2, top_p=0.95 |
| Brainstorming | temperature=1.0, top_k=50 |
| Chat/dialogue | temperature=0.7, top_p=0.9, rep_penalty=1.1 |

## What You Learned

- **Greedy decoding** — always pick highest probability (boring, repetitive)
- **Temperature** — scales logits to control randomness (lower=focused, higher=creative)
- **Top-k sampling** — only consider the k most likely tokens
- **Top-p (nucleus)** — adaptive: keep smallest set with cumulative prob ≥ p
- **Repetition penalty** — reduce probability of already-generated tokens
- **The tradeoff** — coherence vs. diversity, controlled by these knobs

We can now generate text with fine-grained control. But our model is small (10M params) and trains on CPU. To get truly good text, we need to scale up — more parameters, GPU training, mixed precision.

---

[← Chapter 8: Data Pipeline](chapter-08-data.md) | [Chapter 10: Scaling →](chapter-10-scaling.md)
