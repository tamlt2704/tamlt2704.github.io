# Chapter 9: Inference and Deployment

[prev: Fine-tuning](chapter-08-finetuning.md) | [next: Overview](chapter-00-overview.md)

Deploying an LLM efficiently requires quantization to reduce memory, optimized serving for throughput, and proper API design for production use.

## Quantization

Reduce model precision from fp16 (2 bytes per param) to INT8 (1 byte) or INT4 (0.5 bytes):

### INT8 Quantization

```python
import torch
import torch.nn as nn

class Int8Linear(nn.Module):
    """Simple per-channel INT8 quantization."""

    def __init__(self, weight):
        super().__init__()
        # weight shape: (out_features, in_features)
        # Compute per-channel scale
        scale = weight.abs().max(dim=1).values / 127.0  # (out_features,)
        weight_int8 = torch.round(weight / scale.unsqueeze(1)).clamp(-128, 127).to(torch.int8)

        self.register_buffer("weight_int8", weight_int8)
        self.register_buffer("scale", scale)

    def forward(self, x):
        # x shape: (batch, seq_len, in_features)
        # Dequantize weight
        weight_fp = self.weight_int8.float() * self.scale.unsqueeze(1)
        return x @ weight_fp.T

def quantize_model_int8(model):
    """Replace all Linear layers with INT8 versions."""
    for name, module in model.named_modules():
        for attr in dir(module):
            layer = getattr(module, attr, None)
            if isinstance(layer, nn.Linear):
                setattr(module, attr, Int8Linear(layer.weight.data))
    return model
```

### INT4 Quantization (Group-wise)

```python
import torch
import torch.nn as nn

class Int4Linear(nn.Module):
    """Group-wise INT4 quantization (GPTQ-style concept)."""

    def __init__(self, weight, group_size=128):
        super().__init__()
        out_features, in_features = weight.shape
        assert in_features % group_size == 0

        n_groups = in_features // group_size
        w = weight.reshape(out_features, n_groups, group_size)

        # Per-group scale
        scales = w.abs().max(dim=-1).values / 7.0  # (out, n_groups)
        w_int4 = torch.round(w / scales.unsqueeze(-1)).clamp(-8, 7).to(torch.int8)

        self.register_buffer("weight_int4", w_int4)
        self.register_buffer("scales", scales)
        self.group_size = group_size

    def forward(self, x):
        # Dequantize
        w = self.weight_int4.float() * self.scales.unsqueeze(-1)
        w = w.reshape(w.shape[0], -1)  # (out_features, in_features)
        return x @ w.T
```

**GPTQ**: Uses second-order information (Hessian) to minimize quantization error. Quantizes one column at a time, compensating errors in remaining columns.

**AWQ**: Activation-Aware Weight Quantization. Identifies important weights (those multiplied by large activations) and keeps them at higher precision.

## ONNX Export

Export for cross-platform inference:

```python
import torch

def export_to_onnx(model, output_path="model.onnx", seq_len=128):
    model.eval()
    dummy_input = torch.randint(0, 50257, (1, seq_len))

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "seq_len"},
            "logits": {0: "batch", 1: "seq_len"},
        },
        opset_version=17,
    )
    print(f"Exported to {output_path}")
```

## vLLM for Serving

vLLM provides high-throughput serving with PagedAttention:

```python
# Install: pip install vllm
# Serve a model:
# python -m vllm.entrypoints.openai.api_server \
#     --model meta-llama/Llama-2-7b-chat-hf \
#     --dtype bfloat16 \
#     --max-model-len 4096

# Client usage:
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="unused")
response = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100,
)
print(response.choices[0].message.content)
```

**PagedAttention**: Manages KV-cache like virtual memory pages. Eliminates memory fragmentation and enables efficient batching of variable-length sequences.

## Speculative Decoding

Use a small "draft" model to propose tokens, then verify with the large model in parallel:

```python
import torch

@torch.no_grad()
def speculative_decode(large_model, small_model, prompt_ids, n_tokens=5,
                       max_new_tokens=100, temperature=1.0):
    """
    Generate faster by drafting with small model, verifying with large model.
    n_tokens: number of speculative tokens per step.
    """
    ids = prompt_ids.clone()

    tokens_generated = 0
    while tokens_generated < max_new_tokens:
        # Draft: small model generates n_tokens
        draft_ids = ids.clone()
        for _ in range(n_tokens):
            logits = small_model(draft_ids)[:, -1, :] / temperature
            next_id = torch.multinomial(torch.softmax(logits, dim=-1), 1)
            draft_ids = torch.cat([draft_ids, next_id], dim=1)

        # Verify: large model scores all draft tokens in one forward pass
        draft_tokens = draft_ids[:, ids.shape[1]:]  # (1, n_tokens)
        verify_input = torch.cat([ids, draft_tokens], dim=1)
        large_logits = large_model(verify_input)  # (1, total_len, vocab_size)

        # Accept tokens that match large model's distribution
        accepted = 0
        for i in range(n_tokens):
            pos = ids.shape[1] + i - 1
            large_probs = torch.softmax(large_logits[:, pos, :] / temperature, dim=-1)
            draft_token = draft_tokens[:, i]

            # Accept if large model agrees (simplified acceptance)
            if large_probs[0, draft_token[0]] > 0.1:
                accepted += 1
            else:
                break

        # Keep accepted tokens + sample one from large model
        ids = torch.cat([ids, draft_tokens[:, :accepted]], dim=1)

        # Sample next token from large model at rejection point
        pos = ids.shape[1] - 1
        next_logits = large_logits[:, pos, :] / temperature
        next_id = torch.multinomial(torch.softmax(next_logits, dim=-1), 1)
        ids = torch.cat([ids, next_id], dim=1)

        tokens_generated += accepted + 1

    return ids

# Speedup: 2-3x when draft model acceptance rate is high
```

## Batching Strategies

### Continuous Batching

Instead of waiting for all sequences in a batch to finish, immediately fill empty slots:

```python
import torch
from dataclasses import dataclass
from typing import Optional

@dataclass
class Request:
    id: int
    input_ids: torch.Tensor
    generated_ids: list
    max_tokens: int
    done: bool = False

class ContinuousBatcher:
    def __init__(self, model, max_batch_size=32):
        self.model = model
        self.max_batch_size = max_batch_size
        self.active_requests: list[Request] = []
        self.waiting_queue: list[Request] = []

    def add_request(self, request: Request):
        if len(self.active_requests) < self.max_batch_size:
            self.active_requests.append(request)
        else:
            self.waiting_queue.append(request)

    def step(self):
        """Process one generation step for all active requests."""
        if not self.active_requests:
            return

        # Batch all active sequences (pad to same length)
        max_len = max(
            r.input_ids.shape[1] + len(r.generated_ids)
            for r in self.active_requests
        )

        # Run model on batch (simplified — real impl uses KV-cache)
        for req in self.active_requests:
            current_ids = torch.cat([
                req.input_ids,
                torch.tensor([req.generated_ids], dtype=torch.long)
            ], dim=1) if req.generated_ids else req.input_ids

            logits = self.model(current_ids)[:, -1, :]
            next_id = logits.argmax(dim=-1).item()
            req.generated_ids.append(next_id)

            if len(req.generated_ids) >= req.max_tokens:
                req.done = True

        # Remove done requests, add waiting ones
        self.active_requests = [r for r in self.active_requests if not r.done]
        while self.waiting_queue and len(self.active_requests) < self.max_batch_size:
            self.active_requests.append(self.waiting_queue.pop(0))
```

## API Serving with FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel
import torch
import tiktoken

app = FastAPI()

# Load model at startup
model = None  # Load your trained model here
enc = tiktoken.get_encoding("gpt2")

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.8
    top_p: float = 0.9

class GenerateResponse(BaseModel):
    text: str
    tokens_generated: int

@app.post("/generate")
async def generate_endpoint(req: GenerateRequest):
    prompt_ids = torch.tensor([enc.encode(req.prompt)], device="cuda")

    with torch.no_grad():
        output_ids = generate(
            model, prompt_ids,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
        )

    generated_ids = output_ids[0, prompt_ids.shape[1]:].tolist()
    text = enc.decode(generated_ids)
    return GenerateResponse(text=text, tokens_generated=len(generated_ids))

# Run: uvicorn serve:app --host 0.0.0.0 --port 8000
```

## Running Locally

### llama.cpp

C++ inference engine with aggressive quantization. Runs on CPU or GPU:

```
# Build
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

# Convert model to GGUF format
python convert.py --outfile model.gguf --outtype q4_0 /path/to/model

# Run inference
./main -m model.gguf -p "Once upon a time" -n 100

# Start API server
./server -m model.gguf --host 0.0.0.0 --port 8080
```

### Ollama

User-friendly wrapper around llama.cpp:

```
# Install: https://ollama.ai
# Pull and run a model
ollama pull llama2
ollama run llama2 "Explain transformers in one paragraph"

# Serve as API
# Ollama automatically serves on localhost:11434
# curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"Hello"}'
```

## Memory Requirements

| Model | fp16   | INT8  | INT4   |
| ----- | ------ | ----- | ------ |
| 7B    | 14 GB  | 7 GB  | 3.5 GB |
| 13B   | 26 GB  | 13 GB | 6.5 GB |
| 70B   | 140 GB | 70 GB | 35 GB  |

Rule: `memory ≈ params * bytes_per_param + KV_cache`

KV-cache per token: `2 * n_layers * embed_dim * 2 bytes` (K and V, fp16)

## Key Takeaways

- INT4 quantization reduces memory 4x with minimal quality loss
- vLLM with PagedAttention is the standard for high-throughput serving
- Speculative decoding gives 2-3x speedup without quality loss
- Continuous batching maximizes GPU utilization
- llama.cpp and Ollama make local inference accessible on consumer hardware
- Always profile: measure tokens/second and memory usage before deploying
