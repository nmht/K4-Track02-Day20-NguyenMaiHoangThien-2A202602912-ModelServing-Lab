# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=4` `ngl=0` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 3269 | 424 / 628 | 42.5 / 58.8 | 3198 / 4167 / 4167 | 23.5 |
| UD-Q2_K_XL | 0.39 | 6075 | 846 / 1395 | 75.7 / 114.1 | 5649 / 6324 / 6324 | 13.2 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.78x SLOWER** than `Q4_K_M` here, despite being 0.11 GB smaller. That is a real result, not a mistake: fewer bits only buys speed when decode is limited by memory bandwidth. On a machine that is compute-limited instead — few cores, no GPU offload — the extra dequantization work of a heavily-quantized format can cost more than the bytes it saves. Say which case yours is.

## Your observation (required)

On this machine (compute-limited, CPU only without GPU offload), the smaller quantization (`UD-Q2_K_XL`) is actually **1.78x SLOWER** (13.2 tok/s) compared to `Q4_K_M` (23.5 tok/s). 
The memory savings of 0.11 GB is not worth the massive performance drop. The CPU spends too much compute overhead dequantizing the heavily packed Q2 format. Therefore, **`Q4_K_M` is the clear winner** for CPU-only inference on this hardware.
