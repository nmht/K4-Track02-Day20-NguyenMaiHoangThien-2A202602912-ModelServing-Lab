# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** _Nguyen Mai Hoang Thien_
**MSSV:** _2A202602912_
**Cohort:** _A20-K4_
**Ngày submit:** _2026-10-06_

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** _Windows 10_
- **CPU:** _AMD Ryzen 5 3550H_
- **Cores:** _4 / 8_
- **CPU extensions:** _AVX2_
- **RAM:** _13.9_
- **Accelerator:** _CPU only (llama_cpp_backend)_
- **llama.cpp asset đã tải:** _llama-b10488-bin-win-avx2-x64.zip_
- **Model đã dùng:** _Qwen3.5 0.8B_ (`LAB_MODEL=`_qwen35-0.8b_)
- **Quantization:** _Q4_K_M_ + _UD-Q2_K_XL_ (từ `models/active.json`)

**Chạy ở đâu:** _laptop của tôi_
_(Nếu dùng cloud fallback: nói rõ vì sao — RAM < 8 GB, setup fail, v.v. Không mất điểm.)_

**Setup story** (≤ 80 chữ): điều gì cần thay đổi để lab chạy trên máy bạn? Có bước
nào fail rồi phải workaround không?

Dùng aria2 để tải model vì thư viện requests/urllib bị lỗi reset connection trên Windows. Model chạy 100% bằng CPU do bản prebuilt chưa kích hoạt backend CUDA cho GPU.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 3269 | 424 / 628 | 42.5 / 58.8 | 3198 / 4167 / 4167 | 23.5 |
| UD-Q2_K_XL | 0.39 | 6075 | 846 / 1395 | 75.7 / 114.1 | 5649 / 6324 / 6324 | 13.2 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn bao nhiêu, và **có đáng không**? Bạn đã thử
hỏi cùng một câu trên cả hai (`make serve` vs `.venv/bin/python labs/02-serve/serve.py --compare`)
chưa? Chất lượng khác nhau thế nào?

Bản 2-bit CHẬM HƠN bản 4-bit (13.2 tok/s so với 23.5 tok/s). Điều này xảy ra do máy chạy hoàn toàn bằng CPU nên quá trình giải nén (dequantize) format siêu nén Q2_K tốn quá nhiều chu kỳ CPU, gây phản tác dụng. Bản 4-bit đáng dùng hơn.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 0.28 | 29000 | 46000 | 46000 | 7.9 | 0 |
| 50 | 0.24 | 38000 | 59000 | 59000 | 8.3 | 0 |

- **Offered load tăng 5×, throughput thực tăng:** _0.86_
- **P95 tăng:** _1.28_
- **Effective concurrency ở 50 users:** _8.3_ so với `--parallel` = _4_ slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): _3.79_ / _4_ slots

**Saturation reading** (≤ 80 chữ): server của bạn bão hoà ở đâu, và **bằng chứng nào**
thuyết phục bạn? Nếu P95 tăng nhanh hơn RPS thì phần latency thêm đó là queue time hay
compute time — bạn biết bằng cách nào? Nếu bạn phải nâng goodput@SLO, bạn sẽ đổi knob
nào **trước**, và vì sao knob đó?

Server bão hòa ở dưới 50 users (thậm chí 10 users đã bão hòa). Bằng chứng là throughput giảm còn 0.86x trong khi load tăng 5x, và P95 tăng 1.28x, cho thấy request bị xếp hàng. Để nâng goodput, thay vì tăng số lượng luồng (gây overhead), nên dùng GPU offload để tăng tốc xử lý cho CPU.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | - | stub |
| N17 Data pipeline | - | stub |
| N18 Lakehouse | - | stub |
| N19 Vector + features | keyword | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: _0.0 ms_
- retrieve: _0.1 ms_
- llm: _8848.9 ms_
- **stage chiếm nhiều nhất:** _llm_ (_100%_ của total)

**Reflection** (≤ 60 chữ): bottleneck ở đâu? Có khớp với kỳ vọng của bạn không? Nếu
phải giảm latency của pipeline này 2×, bạn sẽ tấn công vào đâu?

Bottleneck nằm hoàn toàn ở LLM (chiếm 100% thời gian) đúng như kỳ vọng vì CPU chạy inference quá chậm. Để giảm latency, tôi sẽ tối ưu phần LLM bằng cách giảm quantize hoặc đưa lên GPU chạy.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** _Hạ -t từ 16 xuống -t 4_

```
before:  8.8 tok/s
after:   20.9 tok/s
speedup: 2.38
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

_Giải thích như đang nói với bạn ngồi cạnh. Bám vào **cơ chế**, không phải "vibes":
memory bandwidth? vector width? cache residency? scheduling? queueing? Nếu kết quả
**khác** với kỳ vọng từ deck — nói rõ, và giải thích vì sao. Grader thưởng điểm cho
lập luận đúng về một kết quả bất ngờ, hơn là một con số đẹp không được giải thích._

Kết quả này rất hợp lý: CPU chỉ có 4 nhân vật lý. Khi nhồi tới 16 luồng, các luồng sinh ra liên tục tranh giành băng thông bộ nhớ và CPU cache, dẫn đến overhead khổng lồ từ context switching, khiến tốc độ rớt thê thảm. Chạy đúng 4 luồng ứng với 4 nhân vật lý cho ra throughput cao nhất.

---

## 6. Bonus  *(optional — tối đa 10 điểm)*

> Bỏ trống nếu không làm. Xem `docs/bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** _Không làm_

**Numbers:**

```
before:  <số>
after:   <số>
speedup: <X.Y>×
```

**Điều này nói lên gì mà deck chưa nói:**

_(để trống nếu bạn không làm phần này)_

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

_(1–2 câu. Không bắt buộc, nhưng grader đọc hết.)_

_(để trống nếu bạn không làm phần này)_

---

## 8. Self-check trước khi push

- [ ] `hardware.json` committed
- [ ] `models/active.json` committed
- [ ] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [ ] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [ ] `benchmarks/02-server-results.md` committed (`make load-report`)
- [ ] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [ ] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [ ] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [ ] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [ ] 5 screenshots trong `submission/screenshots/`
- [ ] `make verify` → **exit 0**
- [ ] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [ ] Repo GitHub ở chế độ **public**
- [ ] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab**
- [ ] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI  *(xem `docs/RULES.md` §3)*

_(Công cụ nào, dùng vào việc gì. Ghi "Không dùng" nếu không dùng.)_
