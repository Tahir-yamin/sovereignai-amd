# SovereignAI-AMD Debug Session — Master Documentation

## 1. Project Overview
**Goal:** Run a LangGraph-based multi-agent AI pipeline (`src/main.py`) on an AMD Instinct MI300X VF GPU (192GB HBM3) using ROCm 7.2.

**Stack:**
- **Core**: PyTorch 2.11.0+rocm7.2
- **Initial Engine**: vLLM 0.20.2 (CUDA Wheel - Failed)
- **Final Engine**: Transformers 5.8.0 (ROCm Native - Success)
- **Workflow**: LangGraph 1.1.10
- **Models**: Qwen2.5 series (7B, 14B, 72B)
- **OS**: Ubuntu / Python 3.12

---

## 2. Project Structure
```text
/workspace/
├── src/
│   ├── main.py                # Pipeline Entry Point
│   ├── agents/
│   │   ├── sanitizer_agent.py # PII Redaction
│   │   ├── analyst_agent.py   # Qwen 72B Analysis
│   │   └── compliance_agent.py# Regulatory Audit
│   ├── models/
│   │   └── model_manager.py   # Model Loading & Inference Logic
│   └── pipeline/
│       └── graph.py           # LangGraph Definition
└── models/
    ├── qwen2.5-7b/            # Local Weights
    ├── qwen2.5-14b/
    └── qwen2.5-72b/
```

---

## 3. Original (Broken) State
The initial `ModelManager` was built assuming a functional `vLLM` installation. 

### Original `src/models/model_manager.py` (vLLM-based)
```python
import os
import torch
from loguru import logger
from vllm import LLM, SamplingParams

class ModelManager:
    # ... configurations ...
    def load_model(self, model_name: str) -> LLM:
        # FAILED: Triggered dynamic linker errors on MI300X
        model = LLM(
            model=model_path,
            dtype="float16",
            gpu_memory_utilization=0.60,
            trust_remote_code=True,
        )
        return model
```

---

## 4. Error Timeline & Resolution Log

### Error 1: `NotImplementedError` (EngineCore)
- **Symptom**: vLLM V1 engine failed to identify the platform, falling back to `UnspecifiedPlatform`.
- **Action**: Unset `VLLM_USE_V1` and switched to multiproc `spawn`.

### Error 2: `amdsmi` Missing (Silent Detection Failure)
- **Discovery**: `vllm/platforms/__init__.py` was failing to import `amdsmi`.
- **Root Cause**: vLLM uses `amdsmi` as the *exclusive* check for ROCm. Without it, it defaults to CUDA.
- **Fix**: Patched `vllm` sources to hardcode `RocmPlatform` and MI300X `gfx942` architecture.

### Error 3: The "Binary Wall" (Linker Errors)
- **Errors**: `undefined symbol: __cudaGetKernel`, `cublasGemmEx`, `cuTensorMapEncodeTiled`.
- **Forensic Analysis**: Using `nm -D` on `vllm/_C.abi3.so` revealed 50+ unresolved NVIDIA symbols.
- **Diagnosis**: The environment had a **CUDA-targeted vLLM wheel** installed. There is no official ROCm vLLM wheel on PyPI.

### Error 4: "Sovereign Shimming" Failure
- **Action**: Created `sovereign_shim.c` to stub CUDA calls via `LD_PRELOAD`.
- **Result**: Linker was satisfied, but the runtime segfaulted. Stubs cannot replace hardware-specific memory kernels (like PagedAttention).

---

## 5. The Final Solution: ROCm-Native Transformation

### Step 1: Environment De-Pollution
We unmasked the environment by unsetting all CUDA-shim variables:
```bash
unset LD_PRELOAD
unset VLLM_PLATFORM
```

### Step 2: The "Clean Venv" Protocol
Established a native ROCm stack in `/opt/vllm-clean`:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
pip install transformers accelerate langgraph loguru
```

### Step 3: MI300X Memory Optimization
We refactored `ModelManager` to use **Transformers + Accelerate**.
- **Memory Math**: Qwen 72B (144GB) + 14B + 7B fits comfortably within the MI300X's 192GB HBM3.
- **Optimization**: Used `device_map="auto"` and `torch.bfloat16` for maximum throughput.

### Step 4: Final Code Implementation
```python
# Fixed generate method
def generate(self, model_name: str, prompt: str, system_prompt: Optional[str] = None):
    # Use **inputs to correctly pass input_ids and attention_mask
    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=4096)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)
```

---

## 6. Successful Execution Results
The pipeline achieved a full end-to-end run on the MI300X:

```text
==================================================
SANITIZED TEXT:
    Patient: John Doe (SSN: [SSN_1])
    Findings: acute MI. Immediate intervention required.

ANALYSIS REPORT:
    ### Expert Analysis (Qwen 72B)
    The patient exhibits symptoms of Acute Myocardial Infarction.
    Recommended: Immediate Catheterization Lab transfer.

COMPLIANCE SCORE: 70.0
==================================================
```

---

## 7. Key Lessons Learned
1.  **vLLM Build Policy**: `pip install vllm` always installs a CUDA wheel. For ROCm, you MUST build from source or use a vendor wheel.
2.  **Detection Hooks**: `amdsmi` is a hard dependency for vLLM ROCm detection; without it, the engine defaults to a broken CUDA path.
3.  **Shimming Limitations**: You cannot shim modern GPU kernels. If the binary targets the wrong architecture, you must replace the binary, not patch the linker.
4.  **MI300X Capacity**: 192GB of HBM3 is a game-changer. It allows running a 72B model in high precision alongside multiple smaller agents without quantization.

---
**Documentation Complete**
