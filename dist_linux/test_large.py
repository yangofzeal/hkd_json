#!/usr/bin/env python3
import json
import os
import pickle
import sys
import time
import zlib

import hkd_json

DATA_FILE = "dataset_large.npz"

def timed(fn, reps=3):
    vals = []
    result = None
    for _ in range(reps):
        t0 = time.perf_counter()
        result = fn()
        vals.append(time.perf_counter() - t0)
    vals.sort()
    return result, vals[len(vals)//2]

def main():
    print("HKD_JSON_EDITION=%s" % hkd_json.EDITION)
    print("hkd_json=%s" % hkd_json.__version__)
    print("data=%s" % DATA_FILE)
    print("file_size_bytes=%d" % os.path.getsize(DATA_FILE))
    print("free_limit=%s" % hkd_json.FREE_MAX_FILE_BYTES)

    try:
        records = hkd_json.load_npz_records(DATA_FILE)
    except Exception as e:
        print("ERROR: %s" % e)
        raise SystemExit(2)

    compact = lambda: json.dumps(records, separators=(",",":"), ensure_ascii=False).encode("utf-8")

    json_blob, json_enc = timed(compact)
    _, json_dec = timed(lambda: json.loads(json_blob.decode("utf-8")))

    hkd_blob, hkd_enc = timed(lambda: hkd_json.dumps(records))
    hkd_obj, hkd_dec = timed(lambda: hkd_json.loads(hkd_blob))

    pickle_blob, pickle_enc = timed(lambda: pickle.dumps(records, protocol=pickle.HIGHEST_PROTOCOL))
    _, pickle_dec = timed(lambda: pickle.loads(pickle_blob))

    zlib_blob, zlib_enc = timed(lambda: zlib.compress(json_blob, 9), reps=2)
    _, zlib_dec = timed(lambda: json.loads(zlib.decompress(zlib_blob).decode("utf-8")), reps=2)

    exact = (hkd_obj == records)
    cycles = hkd_json.logical_cycles(records)

    print("records=%d" % len(records))
    print("method,bytes,encode_ms,decode_ms,exact")
    print("json,%d,%.6f,%.6f,True" % (len(json_blob), json_enc*1000, json_dec*1000))
    print("pickle,%d,%.6f,%.6f,True" % (len(pickle_blob), pickle_enc*1000, pickle_dec*1000))
    print("zlib_json,%d,%.6f,%.6f,True" % (len(zlib_blob), zlib_enc*1000, zlib_dec*1000))
    print("hkd_json,%d,%.6f,%.6f,%s" % (len(hkd_blob), hkd_enc*1000, hkd_dec*1000, exact))

    print("hkd_size_reduction_vs_json_x=%.6f" % (len(json_blob)/float(len(hkd_blob))))
    print("hkd_encode_speedup_vs_json_x=%.6f" % (json_enc/float(hkd_enc)))
    print("hkd_decode_speedup_vs_json_x=%.6f" % (json_dec/float(hkd_dec)))
    if cycles:
        print("json_structural_cycles=%d" % cycles["json_structural_cycles"])
        print("hkd_structural_cycles=%d" % cycles["hkd_structural_cycles"])
        print("structural_cycle_reduction_x=%.6f" % cycles["cycle_reduction_x"])
    print("exact=%s" % exact)
    print("PASS=%s" % exact)

if __name__ == "__main__":
    main()
