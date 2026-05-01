import os
import sys
import tempfile
import tracemalloc
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter_ns
from typing import Literal

from base.factory import AlgorithmFactory, AlgorithmVersion


@dataclass(frozen=True)
class SingleBenchmarkResult:
    time_ns: int
    mem_after_peak: int
    mem_delta_current: int


@dataclass(frozen=True)
class AggregatedValue:
    mean: float
    std: float
    unit: str = ""

    def __str__(self):
        return f"{self.mean:.2f} ± {self.std:.2f} {self.unit}"

    @classmethod
    def from_values(cls, values: list[int | float], unit: str = ""):
        return cls(
            mean=mean(values),
            std=stdev(values),
            unit=unit,
        )


@dataclass(frozen=True)
class BenchmarkResult:
    time: AggregatedValue
    mem_after_peak: AggregatedValue
    mem_delta_current: AggregatedValue

    @classmethod
    def aggregate(cls, results: list[SingleBenchmarkResult]):
        return cls(
            time=AggregatedValue.from_values([r.time_ns / 1e6 for r in results], "ms"),
            mem_delta_current=AggregatedValue.from_values(
                [r.mem_delta_current / 1024 for r in results], "KiB"
            ),
            mem_after_peak=AggregatedValue.from_values(
                [r.mem_after_peak / 1024 for r in results], "KiB"
            ),
        )

    def summary(self):
        return f"Time: {self.time}\nPeak memory use: {self.mem_after_peak}\n"


def benchmark_run(
    dataset_file: Path, min_support: float, algorithm_version: str, output_mode: Literal["file", "memory"], spmf_jar: Path
) -> SingleBenchmarkResult:
    tracemalloc.start()
    tracemalloc.reset_peak()
    time_start = perf_counter_ns()
    before_current, before_peak = tracemalloc.get_traced_memory()

    with tempfile.NamedTemporaryFile(delete_on_close=True) as output_file:
        output_path = Path(output_file.name)

        algorithm = AlgorithmFactory.create(
            algorithm_version=AlgorithmVersion(algorithm_version),
            input_file=dataset_file,
            output_file=output_path,
            min_support=min_support,
            output_mode=output_mode,
            spmf_jar=spmf_jar,
        )
        algorithm.run()
        algorithm.close()

    after_current, after_peak = tracemalloc.get_traced_memory()
    time_end = perf_counter_ns()
    tracemalloc.stop()

    return SingleBenchmarkResult(
        time_ns=time_end - time_start,
        mem_after_peak=after_peak,
        mem_delta_current=after_current - before_current,
    )


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-s", "--minsup", type=float, required=True)
    parser.add_argument("-n", "--num_samples", type=int, default=100)
    parser.add_argument(
        "-a",
        "--algorithm",
        type=str,
        choices=[e.value for e in AlgorithmVersion],
        default="custom",
        help="Algorithm implementation to use (default: 'custom')",
    )
    parser.add_argument(
        "-m",
        "--output-mode",
        type=str,
        choices=["file", "memory"],
        default="file",
        help="Choose where to save itemsets during execution (default: 'file')",
    )
    parser.add_argument(
        "--spmf-jar",
        type=Path,
        default=Path("extern/spmf.jar"),
        help="Path to the spmf.jar file (only used for 'spmf' algorithm)",
    )

    args = parser.parse_args()
    if not (0 <= args.minsup <= 1):
        raise ValueError("Minimum support must be between 0 and 1")

    if os.environ.get("PYTHONOPTIMIZE", "") != "1":
        print(
            "WARNING: PYTHONOPTIMIZE environment variable is not set, expensive assertions will run during profiling",
            file=sys.stderr,
        )

    if args.algorithm == "spmf":
        print(
            "WARNING: You are using the Java implementation. tracemalloc will only measure memory used by the Python script! "
            "Memory allocated by the Java Virtual Machine (JVM) will not be tracked.",
            file=sys.stderr,
        )

    results = [
        benchmark_run(args.input, args.minsup, args.algorithm, args.output_mode, args.spmf_jar)
        for _ in range(args.num_samples)
    ]

    aggregate_results = BenchmarkResult.aggregate(results)
    print(aggregate_results.summary())


if __name__ == "__main__":
    main()
