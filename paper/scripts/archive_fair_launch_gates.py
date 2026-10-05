"""Run and retain the pre-launch verification gates for the fair revision."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper/array_revision_fair"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    commands = [
        [sys.executable, "paper/scripts/verify_fair_revision.py"],
        [sys.executable, "paper/scripts/run_array_fair_benchmark.py", "--self-test"],
        [sys.executable, "paper/scripts/run_array_fair_benchmark.py", "--pilot"],
    ]
    env = dict(os.environ)
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                 "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[name] = "1"
    results = []
    for command in commands:
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        results.append({"command": command, "returncode": result.returncode,
                        "elapsed_seconds": time.perf_counter() - start,
                        "output": result.stdout})
        print(result.stdout, end="", flush=True)
        if result.returncode:
            raise RuntimeError(f"Pre-launch verification failed: {command}")
    sources = [
        "paper/scripts/verify_fair_revision.py",
        "paper/scripts/run_array_fair_benchmark.py",
        "paper/scripts/build_fair_revision_runtime.py",
        "paper/scripts/fair_revision_runtime.py",
        "paper/array_revision_fair/runtime/_sighted_fast.pyx",
        "paper/array_revision_fair/PROTOCOL.md",
        "paper/tables/mixed_sighted_dataset_sample.csv",
    ]
    report = {
        "all_passed": True,
        "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_hashes": {name: sha256(ROOT / name) for name in sources},
        "harness": json.loads((OUT / "harness_checks.json").read_text()),
        "commands": results,
    }
    (OUT / "launch_gates.json").write_text(json.dumps(report, indent=2) + "\n")
    print("All pre-launch gates passed and were archived.", flush=True)


if __name__ == "__main__":
    main()
