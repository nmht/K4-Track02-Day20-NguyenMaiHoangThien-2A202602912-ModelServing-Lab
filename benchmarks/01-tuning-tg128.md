# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **4 physical · 8 logical** cores · `ngl=0` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 11.4 | 55% |
| 2 | 17.2 | 82% |
| 4 | 20.9 | 100% |
| 8 | 11.4 | 55% |
| 16 | 8.8 | 42% |

**Best**: `-t 4` at 20.9 tok/s
**Slowest tested**: `-t 16` at 8.8 tok/s (2.38x spread)
**Against the physical-core default** (`-t 4`, 20.9 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=4 make bench
```

## Your explanation (required)

The peak performance (20.9 tok/s) is exactly at `-t 4`, which is the physical core count of this CPU. It sharply drops beyond that (down to 11.4 tok/s at 8 threads and 8.8 tok/s at 16 threads).
This happens because LLM inference is highly dependent on memory bandwidth and dense matrix multiplication. When we spawn more threads than physical cores (like 8 or 16), the hyperthreads or extra OS threads compete for the same physical execution units and L3 cache. This causes severe context-switching overhead and cache thrashing, completely destroying performance. Therefore, strictly pinning the thread count to the physical core count (`-t 4`) yields the maximum throughput.
