# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=4` ·
`ngl=0`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 16 | 0.28 | 29000 | 46000 | 46000 | 7.9 | 0.0% |
| 50 | 14 | 0.24 | 38000 | 59000 | 59000 | 8.3 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.86x** (17% of linear) |
| P95 latency | **1.28x** |
| Effective concurrency at 50 users | 8.3 vs `--parallel 4` slots (occupancy/slot ratio 2.08) |

**Saturated.** Throughput delivered only 0.86x for 5x the offered load, and effective concurrency (8.3) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.86x while P95 moved 1.28x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

> **Small sample.** Only 14 requests completed in the
> shorter run, so these percentiles are indicative rather than solid. Note also that
> locust averages only *completed* requests: when the run ends with requests still
> queued, effective concurrency is an **under**-estimate. Trust the throughput-scaling
> row over the concurrency row here, and run longer (`-t 3m`) if you want firmer numbers.

## Your reading (required -- replace this line)

_Where does your server saturate, and what is the evidence? Name the number that
convinced you. Then say what you would change first to raise goodput at your SLO --
and why that knob and not another._
