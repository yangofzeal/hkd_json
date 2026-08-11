# HKD JSON

**HKD JSON (`hkd_json`)** is an HKD∞-inspired structural serializer for JSON-shaped Python data.

It is designed as a low-friction alternative to Python's standard `json` serialization workflow for large, homogeneous record collections such as API responses, application logs, telemetry, event streams, and structured datasets.

In tested high-entropy workloads, HKD JSON achieved:

- **approximately 2× smaller serialized representations than compact native Python JSON**
- **approximately 3× faster encoding in representative tests**
- **up to about 3.9× faster encoding in the tested workload suite**
- **approximately 2× fewer defined structural serialization cycles**
- **exact Python-object round trips**

> **Important:** HKD mode is a compact binary serialization format with a familiar JSON-style API. It is **not textual JSON wire format**. Use `format="json"` when ordinary JSON text interoperability is required.

---

## Buy HKD JSON Unlimited

**HKD JSON Free** supports input datasets up to **8 MiB (8,388,608 bytes)**.

**HKD JSON Unlimited** removes the HKD JSON file-size limit.

[**Buy HKD JSON Unlimited**](https://buy.stripe.com/6oUaEQ7CH6o7gYa6ALgUM04)

---

## Why HKD JSON?

Native Python JSON repeatedly writes structural information such as field names and JSON syntax for every record.

For example:

```python
[
    {
        "request_id": "...",
        "timestamp_ns": 1760000000000000000,
        "user_id": 12345,
        "method": "GET",
        "status": 200
    },
    {
        "request_id": "...",
        "timestamp_ns": 1760000000001000000,
        "user_id": 67890,
        "method": "POST",
        "status": 201
    }
]
```

When millions of records share the same schema, much of that structure is repeated.

HKD∞ treats the persistent schema as established structure and concentrates serialization work on the active values.

Conceptually:

```text
Native JSON

record 1 = keys + structure + values
record 2 = keys + structure + values
record 3 = keys + structure + values
...
```

HKD JSON:

```text
schema
  +
active values
active values
active values
...
```

The exact internal representation, structural selection rules, transforms, and optimization strategy are implementation details and are intentionally not documented here.

---

## Easy Migration from Python `json`

Python's standard library uses `json.dump()` / `json.load()` for files and `json.dumps()` / `json.loads()` for in-memory serialization.

### Native Python

```python
import json

with open("data.json", "w") as f:
    json.dump(records, f)

with open("data.json", "r") as f:
    restored = json.load(f)
```

### HKD JSON

Change the import:

```python
import hkd_json as json

with open("data.hkd", "wb") as f:
    json.dump(records, f)

with open("data.hkd", "rb") as f:
    restored = json.load(f)
```

The programming model remains:

```text
object -> dump -> file
file   -> load -> object
```

---

## `dumps()` / `loads()`

Native Python:

```python
import json

payload = json.dumps(records)
restored = json.loads(payload)
```

HKD JSON:

```python
import hkd_json as json

payload = json.dumps(records)
restored = json.loads(payload)

assert restored == records
```

HKD mode returns compact binary `bytes`.

---

## File Save / Load Example

```python
import hkd_json as json

records = [
    {
        "user_id": 1001,
        "event": "login",
        "region": "us-east-1"
    },
    {
        "user_id": 1002,
        "event": "purchase",
        "region": "us-west-2"
    }
]

with open("records.hkd", "wb") as f:
    json.dump(records, f)

with open("records.hkd", "rb") as f:
    restored = json.load(f)

assert restored == records

print(restored)
```

---

## Ordinary JSON Compatibility Mode

If you need ordinary textual JSON rather than the HKD binary representation:

```python
import hkd_json as json

text = json.dumps(records, format="json")
```

This produces conventional JSON text.

HKD's structural size and performance advantages apply to the default HKD binary mode, not to strict textual JSON mode.

---

## Benchmark

HKD JSON was tested on high-entropy, real-world-shaped datasets containing randomized request IDs, traces, paths, users, timestamps, messages, device identifiers, floating-point telemetry, and other changing values.

The benchmark verifies the complete operation:

```text
Python object
     |
     v
serialize
     |
     v
serialized representation
     |
     v
deserialize
     |
     v
reconstructed Python object
     |
     v
exact equality test
```

### 15,000-record benchmark suite

| Dataset | Compact JSON | HKD JSON | Size Reduction | Encode Speedup | Decode Speedup | Exact |
|---|---:|---:|---:|---:|---:|---:|
| API | 3,610,565 B | **1,784,251 B** | **2.02×** | **2.96×** | **1.50×** | Yes |
| Logs | 3,185,191 B | **1,527,290 B** | **2.09×** | **3.53×** | **1.61×** | Yes |
| Telemetry | 2,912,331 B | **1,364,345 B** | **2.13×** | **3.94×** | **1.67×** | Yes |

These results show approximately **2× smaller output** and roughly **3×–4× faster encoding** on the tested record-oriented workloads.

Decode speed also improved in these tests, although the measured decode gain was smaller than the encoding gain.

Benchmark results are workload- and machine-dependent and should not be interpreted as a guarantee for arbitrary Python objects.

---

## Packaged 8 MiB Benchmark

The Free/Unlimited distribution includes a reproducible dataset benchmark.

The packaged Free test uses:

```text
dataset_free.npz = 8,388,608 bytes
```

A representative run measured:

```text
records=22000

method,bytes,encode_ms,decode_ms,exact
json,6020857,64.472672,62.955134,True
pickle,3875691,18.321205,23.245961,True
zlib_json,1902322,341.588147,86.340592,True
hkd_json,3348069,19.614210,62.860664,True

hkd_size_reduction_vs_json_x=1.798307
hkd_encode_speedup_vs_json_x=3.287039

json_structural_cycles=440000
hkd_structural_cycles=220010
structural_cycle_reduction_x=1.999909

exact=True
PASS=True
```

On this particular packaged dataset, HKD JSON encoded approximately **3.29× faster** while producing a representation approximately **1.80× smaller** than compact JSON.

---

## HKD∞ Structural Cycle Reduction

The benchmark reports a defined **logical structural work count**.

These values are not hardware CPU clock cycles.

For `n` homogeneous records containing `k` fields, the benchmark models ordinary JSON structural work as processing a key and value for every field:

```text
JSON structural cycles = 2 × n × k
```

HKD∞ represents the stable schema once and then processes the active values:

```text
HKD structural cycles = k + n × k
```

Therefore:

```text
JSON / HKD -> approximately 2×
```

as the number of records grows.

For the included 22,000-record dataset:

```text
json_structural_cycles=440000
hkd_structural_cycles=220010
structural_cycle_reduction_x=1.999909
```

---

## Exactness

Performance is useful only if the reconstructed object is correct.

Every published benchmark performs an actual round trip:

```python
blob = hkd_json.dumps(records)
restored = hkd_json.loads(blob)

assert restored == records
```

The benchmark reports:

```text
exact=True
PASS=True
```

HKD JSON does not count a serialization result as successful unless the reconstructed Python object equals the original benchmark object.

---

## Free Edition

HKD JSON Free has a maximum input dataset size of:

```text
8 MiB
8,388,608 bytes
```

The included:

```text
dataset_free.npz
```

is exactly:

```text
8,388,608 bytes
```

and is accepted by the Free edition.

Run:

```bash
cd free
python test.py
```

---

## Free Size-Limit Test

The included:

```text
dataset_large.npz
```

is exactly one byte larger:

```text
8,388,609 bytes
```

Run:

```bash
cd free
python test_large.py
```

HKD JSON Free rejects the file and displays an upgrade message directing the user to:

[https://github.com/yangofzeal/hkd_json](https://github.com/yangofzeal/hkd_json)

---

## Unlimited Edition

HKD JSON Unlimited removes the HKD JSON file-size restriction.

Both included datasets are accepted:

```bash
cd paid

python test.py
python test_large.py
```

The Unlimited edition reports:

```text
free_limit=None
```

and performs the complete serialization, deserialization, benchmark, cycle-count, and exactness test on both datasets.

[**Buy HKD JSON Unlimited**](https://buy.stripe.com/6oUaEQ7CH6o7gYa6ALgUM04)

---

## Included Tests

The distribution contains:

```text
free/
├── hkd_json/
├── test.py
├── test_large.py
├── dataset_free.npz
└── dataset_large.npz

paid/
├── hkd_json/
├── test.py
├── test_large.py
├── dataset_free.npz
└── dataset_large.npz
```

`test.py` and `test_large.py` execute the actual serialization workload.

They benchmark:

- native compact JSON
- Python pickle
- zlib-compressed JSON
- HKD JSON
- serialized byte size
- encoding time
- decoding time
- structural cycle count
- exact reconstruction

`test_large.py` differs from `test.py` only in selecting `dataset_large.npz`.

---

## Run the Benchmark

Free:

```bash
cd free
python test.py
```

Free size-limit test:

```bash
python test_large.py
```

Unlimited:

```bash
cd paid
python test.py
python test_large.py
```

---

## Where HKD JSON Is Most Applicable

HKD JSON is designed primarily for large collections of similarly structured records, including:

- API request and response datasets
- application and server logs
- telemetry
- event streams
- analytics records
- machine-learning metadata
- structured scientific records
- repeated dictionaries
- database/API exports
- high-volume Python data pipelines

The largest gains are expected when many records share structural information while their actual values continue to carry substantial entropy.

---

## Compression vs. Serialization

HKD JSON is not simply a general-purpose compressor.

A general compressor receives a byte stream after serialization and attempts to compress it.

HKD JSON acts earlier:

```text
Python objects
     |
     v
structural analysis
     |
     v
persistent structure + active values
     |
     v
compact HKD representation
```

This lets HKD JSON avoid repeatedly materializing some redundant serialization structure in the first place.

For maximum compression ratio regardless of CPU cost, a dedicated compressor may still produce a smaller final byte stream. HKD JSON instead targets the combination of:

**smaller representation + faster serialization + exact reconstruction.**

---

## Pure Python / Portable Design

The current HKD JSON implementation uses Python and the standard library and does not require Numba/JIT for the benchmarked fast path.

This keeps deployment straightforward on:

- macOS
- Linux

The implementation deliberately relies on efficient native-backed standard-library operations where appropriate instead of introducing a JIT dependency when it does not improve the complete serialization pipeline.

---

## Performance Summary

For the tested homogeneous, high-entropy record workloads:

> **HKD JSON reduced serialized size by approximately 2× and accelerated encoding by approximately 3× or more while preserving exact Python-object reconstruction.**

The exact speed and size improvements vary with dataset structure, entropy, Python version, hardware, and workload.

HKD JSON is particularly intended for cases where conventional JSON repeatedly serializes the same schema across very large numbers of records.

---

## Get HKD JSON Unlimited

Free:

```text
Maximum input dataset: 8 MiB / 8,388,608 bytes
```

Unlimited:

```text
No HKD JSON file-size limit
```

[**Buy HKD JSON Unlimited**](https://buy.stripe.com/6oUaEQ7CH6o7gYa6ALgUM04)

Project:

[https://github.com/yangofzeal/hkd_json](https://github.com/yangofzeal/hkd_json)
