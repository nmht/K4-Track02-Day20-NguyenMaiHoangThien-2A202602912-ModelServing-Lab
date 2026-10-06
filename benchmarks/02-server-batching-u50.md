# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 15 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.79 of 4 slots (95%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 2109 |

Highest sampled value was **3.79 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation (required)

The peak batch width reached **3.79 out of 4 slots**. This means the scheduler successfully packed concurrent requests into shared decode steps (close to 4 requests running simultaneously). 
However, the effective concurrency calculated from Little's Law in `02-server-results.md` was **8.3**. They disagree because `8.3` includes *both* requests being decoded and requests waiting in the queue, whereas the batch width (`3.79`) only measures requests currently occupying decode slots. 
I trust the **peak batch width (3.79)** for hardware utilization (since it physically cannot exceed 4 slots), but I trust the **effective concurrency (8.3)** for understanding total system load (4 decoding + ~4.3 waiting).
