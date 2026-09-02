from __future__ import annotations
import os, subprocess, sys

def main() -> int:
    env = dict(os.environ)
    env["PROPERTY_STUDIO_WRITE_BENCHMARK_EVIDENCE"] = "1"
    env["PROPERTY_STUDIO_BENCH_NOTES"] = "5000"
    print("Running authoritative 5,000-note release benchmark...")
    cmd = [sys.executable, "-m", "pytest", "-v", "tests/test_benchmark.py"]
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        print("Benchmark failed!")
        return res.returncode
    print("Authoritative release benchmark successfully recorded to evidence/benchmark.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
