# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.1 | 11903.4 | 11903.6 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.1 | 6117.6 | 6117.8 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.1 | 8525.6 | 8525.8 |

Mean per stage (ms): embed **0.0** · retrieve **0.1** ·
llm **8848.9** · total **8849.1**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the provided context, **Goodput** is more useful than raw throughput primarily because it **ignores SLOs (Service Level Objectives) at saturation**.

The context explains that while Goodput counts requests per second meeting specific targets (TTFT and TPOT), it does not account for SLOs when the system reaches its maximum capacity (saturation). In contrast, "raw throughput" would likely i

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation in GPU memory** by storing the KV cache in non-contiguous pages.

This design removes the wasted internal fragmentation that typically occurs when GPU memory is used for contiguous data, thereby optimizing memory usage for compute-bound operations.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps primarily when **prefill is compute-bound and decode is memory-bound**.

This is because prefilling the model requires expensive computation (like matrix multiplication), while decoding requires significant memory bandwidth. By splitting these tasks into separate pools (prefill and decode), the system can process the computation-intensive part first and efficient


## Which N16-N19 pieces are real (required)

* N16 (Document embedding): **Stubbed** (no real vector embeddings were created, just text chunks).
* N17 (Query embedding): **Stubbed** (query is not converted into a vector).
* N18 (Semantic similarity search): **Stubbed** (retrieval uses simple keyword overlap).
* N19 (Call inference server): **Real** (the script actually POSTs to llama-server to generate answers).

**Is the dominant stage what you expected?** 
Yes. The `llm` stage takes ~100% (8848.9 ms) of the total time. The retrieval stage takes only 0.1 ms because it is stubbed with a fast keyword overlap. Generating text on a compute-limited CPU takes orders of magnitude longer than searching text.

**If you had to halve this pipeline's latency, which stage would you attack and why?**
I would attack the `llm` stage. Since it consumes almost all the execution time, optimizing retrieval (e.g., adding vector DBs) would only *increase* total latency. To halve latency, I would either add GPU acceleration to speed up decoding, reduce the model size, or implement **semantic caching** to skip the LLM generation entirely for similar repeated queries.
