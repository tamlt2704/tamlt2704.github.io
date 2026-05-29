# Chapter 6: Text Generation

[prev: Training](chapter-05-training.md) | [next: Scaling](chapter-07-scaling.md)

Once trained, the model generates text by repeatedly predicting the next token. Different sampling strategies control the quality and diversity of output.

## Greedy Decoding

Always pick the highest-probability token. Deterministic but often repetitive:

```python
import torch

@torch.no_grad()
def generate_greedy(model, prompt_ids, max_new_tokens=50):
    """
    model: trained GPT model
    prompt_ids: tensor of shape (1, prompt_len)
    """
    model.eval()
    ids = prompt_ids.clone()  # (1, current_len)

    for _ in range(max_new_tokens):
        logits = model(ids)              # (1, current_len, vocab_size)
        next_logits = logits[:, -1, :]   # (1, vocab_size)
        next_id = next_logits.argmax(dim=-1, keepdim=True)  # (1, 1)
        ids = torch.cat([ids, next_id], dim=1)  # (1, current_len + 1)

    return ids  # (1, prompt_len + max_new_tokens)
```

## Temperature Sampling

Temperature controls randomness. Lower = more focused, higher = more creative:

`P(token) = softmax(logits / temperature)`

```python
import torch

@torch.no_grad()
def generate_temperature(model, prompt_ids, max_new_tokens=50, temperature=0.8):
    model.eval()
    ids = prompt_ids.clone()

    for _ in range(max_new_tokens):
        logits = model(ids)[:, -1, :]  # (1, vocab_size)
        logits = logits / temperature
        probs = torch.softmax(logits, dim=-1)  # (1, vocab_size)
        next_id = torch.multinomial(probs, num_samples=1)  # (1, 1)
        ids = torch.cat([ids, next_id], dim=1)

    return ids
```

- `temperature = 1.0`: original distribution
- `temperature = 0.1`: nearly greedy (very peaked)
- `temperature = 2.0`: very flat (high randomness)

## Top-k Sampling

Only sample from the k most likely tokens:

```python
import torch

def top_k_filter(logits, k=50):
    """Zero out all logits except top-k."""
    # logits shape: (batch, vocab_size)
    values, indices = torch.topk(logits, k, dim=-1)
    # values shape: (batch, k)
    min_value = values[:, -1].unsqueeze(-1)  # (batch, 1)
    logits = torch.where(logits >= min_value, logits, torch.full_like(logits, float('-inf')))
    return logits
```

## Top-p (Nucleus) Sampling

Sample from the smallest set of tokens whose cumulative probability exceeds p:

```python
import torch

def top_p_filter(logits, p=0.9):
    """Keep smallest set of tokens with cumulative prob >= p."""
    # logits shape: (batch, vocab_size)
    sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
    cumulative_probs = torch.softmax(sorted_logits, dim=-1).cumsum(dim=-1)

    # Remove tokens with cumulative prob above threshold
    sorted_mask = cumulative_probs - torch.softmax(sorted_logits, dim=-1) >= p
    sorted_logits[sorted_mask] = float('-inf')

    # Scatter back to original positions
    logits = logits.scatter(-1, sorted_indices, sorted_logits)
    return logits
```

## Repetition Penalty

Reduce probability of tokens that already appeared:

```python
import torch

def apply_repetition_penalty(logits, generated_ids, penalty=1.2):
    """
    logits shape: (1, vocab_size)
    generated_ids: list of token IDs already generated
    """
    for token_id in set(generated_ids):
        if logits[0, token_id] > 0:
            logits[0, token_id] /= penalty
        else:
            logits[0, token_id] *= penalty
    return logits
```

## Beam Search

Maintain multiple candidate sequences and pick the best overall:

```python
import torch

@torch.no_grad()
def beam_search(model, prompt_ids, max_new_tokens=50, beam_width=5):
    """Simple beam search implementation."""
    model.eval()
    device = prompt_ids.device

    # Each beam: (sequence_tensor, cumulative_log_prob)
    beams = [(prompt_ids.clone(), 0.0)]

    for _ in range(max_new_tokens):
        candidates = []
        for seq, score in beams:
            logits = model(seq)[:, -1, :]  # (1, vocab_size)
            log_probs = torch.log_softmax(logits, dim=-1)  # (1, vocab_size)

            # Get top-k next tokens for this beam
            top_log_probs, top_ids = torch.topk(log_probs, beam_width, dim=-1)

            for i in range(beam_width):
                new_seq = torch.cat([seq, top_ids[:, i:i+1]], dim=1)
                new_score = score + top_log_probs[0, i].item()
                candidates.append((new_seq, new_score))

        # Keep top beam_width candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        beams = candidates[:beam_width]

    # Return best beam
    return beams[0][0]
```

## Complete Generate Function

Combining all strategies:

```python
import torch
import torch.nn.functional as F

@torch.no_grad()
def generate(model, prompt_ids, max_new_tokens=100, temperature=0.8,
             top_k=50, top_p=0.9, repetition_penalty=1.0):
    """
    Full generation with temperature, top-k, top-p, and repetition penalty.
    prompt_ids shape: (1, prompt_len)
    """
    model.eval()
    ids = prompt_ids.clone()
    generated = prompt_ids[0].tolist()

    for _ in range(max_new_tokens):
        # Truncate to max context length if needed
        input_ids = ids[:, -1024:]

        logits = model(input_ids)[:, -1, :]  # (1, vocab_size)

        # Apply repetition penalty
        if repetition_penalty != 1.0:
            logits = apply_repetition_penalty(logits, generated, repetition_penalty)

        # Apply temperature
        logits = logits / temperature

        # Apply top-k
        if top_k > 0:
            logits = top_k_filter(logits, k=top_k)

        # Apply top-p
        if top_p < 1.0:
            logits = top_p_filter(logits, p=top_p)

        # Sample
        probs = F.softmax(logits, dim=-1)  # (1, vocab_size)
        next_id = torch.multinomial(probs, num_samples=1)  # (1, 1)

        ids = torch.cat([ids, next_id], dim=1)
        generated.append(next_id.item())

        # Stop at EOS token (if defined)
        # if next_id.item() == eos_token_id:
        #     break

    return ids
```

## KV-Cache for Fast Inference

Without cache, generating N tokens requires N forward passes over increasingly long sequences. With KV-cache, each step only processes the new token:

```python
import torch

@torch.no_grad()
def generate_with_cache(model, prompt_ids, max_new_tokens=100, temperature=0.8):
    """
    Generation with KV-cache (requires model to support cache).
    Assumes model.forward(ids, kv_cache) returns (logits, new_cache).
    """
    model.eval()

    # Prefill: process entire prompt
    logits, kv_cache = model(prompt_ids, kv_cache=None)
    # logits: (1, prompt_len, vocab_size)

    next_logits = logits[:, -1, :] / temperature
    probs = torch.softmax(next_logits, dim=-1)
    next_id = torch.multinomial(probs, num_samples=1)  # (1, 1)

    generated = [next_id.item()]

    # Decode: one token at a time using cache
    for _ in range(max_new_tokens - 1):
        logits, kv_cache = model(next_id, kv_cache=kv_cache)
        # logits: (1, 1, vocab_size) — only 1 new token processed

        next_logits = logits[:, -1, :] / temperature
        probs = torch.softmax(next_logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)
        generated.append(next_id.item())

    return generated
```

**Speed comparison**: For a 1024-token generation with 768-dim model:

- Without cache: each step processes all previous tokens = `O(N^2)` total
- With cache: each step processes 1 token = `O(N)` total

## Streaming Output

Print tokens as they are generated:

```python
import torch
import tiktoken
import sys

@torch.no_grad()
def generate_streaming(model, prompt_text, max_new_tokens=200, temperature=0.8):
    """Generate and print tokens as they are produced."""
    model.eval()
    enc = tiktoken.get_encoding("gpt2")

    prompt_ids = torch.tensor([enc.encode(prompt_text)], device="cuda")
    ids = prompt_ids.clone()

    print(prompt_text, end="", flush=True)

    for _ in range(max_new_tokens):
        logits = model(ids[:, -1024:])[:, -1, :] / temperature
        probs = torch.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)
        ids = torch.cat([ids, next_id], dim=1)

        # Decode and print the new token
        token_text = enc.decode([next_id.item()])
        sys.stdout.write(token_text)
        sys.stdout.flush()

    print()  # newline at end
```

## Key Takeaways

- Greedy decoding is fast but repetitive
- Temperature controls the sharpness of the distribution
- Top-k limits choices to k most likely tokens
- Top-p adapts the cutoff based on cumulative probability
- Combine temperature + top-p for best results (common default: temp=0.8, top_p=0.9)
- KV-cache is essential for efficient generation (O(N) vs O(N^2))
- Streaming gives better user experience for interactive applications
