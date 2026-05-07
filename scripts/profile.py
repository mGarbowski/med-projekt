import os
import sys
import tempfile
import tracemalloc
from argparse import ArgumentParser, ArgumentTypeError
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter_ns
from typing import Literal
from tqdm import tqdm

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

    def __str__(self) -> str:
        suffix = f" {self.unit}" if self.unit else ""
        return f"{self.mean:.2f} ± {self.std:.2f}{suffix}"

    @classmethod
    def from_values(cls, values: list[int | float], unit: str = ""):
        return cls(
            mean=mean(values),
            std=stdev(values) if len(values) > 1 else 0.0,
            unit=unit,
        )


@dataclass(frozen=True)
class BenchmarkResult:
    time: AggregatedValue
    mem_after_peak: AggregatedValue
    mem_delta_current: AggregatedValue

    @classmethod
    def aggregate(cls, results: list[SingleBenchmarkResult]):
        if not results:
            raise ValueError("No benchmark results to aggregate.")
        return cls(
            time=AggregatedValue.from_values([r.time_ns / 1e9 for r in results], "s"),
            mem_delta_current=AggregatedValue.from_values(
                [r.mem_delta_current / 1024 for r in results], "KiB"
            ),
            mem_after_peak=AggregatedValue.from_values(
                [r.mem_after_peak / 1024 for r in results], "KiB"
            ),
        )

    def summary(self):
        return f"Time: {self.time}\nPeak memory use: {self.mem_after_peak}\n"



def parse_supports(raw: str) -> list[float]:
    supports: list[float] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            value = float(part)
        except ValueError as exc:
            raise ArgumentTypeError(f"Invalid support value: {part!r}") from exc

        if not 0 < value <= 1:
            raise ArgumentTypeError(f"Support must be in (0, 1], got {value}")

        supports.append(value)

    if not supports:
        raise ArgumentTypeError("Provide at least one support, e.g. 0.6,0.7,0.8")

    return supports


def benchmark_run(
    dataset_file: Path,
    min_support: float,
    algorithm_version: str,
    output_mode: Literal["file", "memory"],
    spmf_jar: Path,
) -> SingleBenchmarkResult:

    fd, tmp_name = tempfile.mkstemp(prefix="benchmark_", suffix=".txt")
    os.close(fd)
    output_path = Path(tmp_name)

    algorithm = None
    try:
        tracemalloc.start()
        tracemalloc.reset_peak()
        time_start = perf_counter_ns()
        before_current, _ = tracemalloc.get_traced_memory()

        algorithm = AlgorithmFactory.create(
            algorithm_version=AlgorithmVersion(algorithm_version),
            input_file=dataset_file,
            output_file=output_path,
            min_support=min_support,
            output_mode=output_mode,
            spmf_jar=spmf_jar,
        )
        algorithm.run()
        after_current, after_peak = tracemalloc.get_traced_memory()
        time_end = perf_counter_ns()

        return SingleBenchmarkResult(
            time_ns=time_end - time_start,
            mem_after_peak=after_peak,
            mem_delta_current=after_current - before_current,
        )
    finally:
        if algorithm is not None:
            algorithm.close()
        tracemalloc.stop()
        output_path.unlink(missing_ok=True)


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-n", "--num_samples", type=int, default=3)
    parser.add_argument(
        "-s",
        "--minsup",
        type=parse_supports,
        required=True,
        help="Comma-separated list of supports, e.g. 0.6,0.7,0.8,0.9",
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        type=str,
        choices=[e.value for e in AlgorithmVersion],
        default=AlgorithmVersion.OPTIMIZED,
        help="Algorithm implementation to use (default: 'optimized')",
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
    parser.add_argument(
        "--readme",
        action="store_true",
        help="Print a Markdown-ready table row instead of a verbose summary",
    )

    args = parser.parse_args()

    if not (0 < args.num_samples):
        raise ValueError("Number of samples must be > 0")

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

    support_results: list[tuple[float, BenchmarkResult]] = []

    total_runs = len(args.minsup) * args.num_samples

    with tqdm(total=total_runs, desc="Benchmarking", unit="run") as pbar:
        for support in args.minsup:
            results: list[SingleBenchmarkResult] = []

            for sample_idx in range(args.num_samples):
                pbar.set_postfix(
                    algorithm=args.algorithm,
                    mode=args.output_mode,
                    support=support,
                    sample=f"{sample_idx + 1}/{args.num_samples}",
                )

                result = benchmark_run(
                    args.input,
                    support,
                    args.algorithm,
                    args.output_mode,
                    args.spmf_jar,
                )

                results.append(result)
                pbar.update(1)

            support_results.append((support, BenchmarkResult.aggregate(results)))

    if args.readme:
        header = ["algorithm", "mode"] + [
            f"{s:g}" for s, _ in support_results
        ]

        time_row = [
            args.algorithm,
            args.output_mode,
        ] + [
            str(r.time) for _, r in support_results
        ]

        memory_row = [
            args.algorithm,
            args.output_mode,
        ] + [
            str(r.mem_after_peak) for _, r in support_results
        ]

        print("# Time")
        print("| " + " | ".join(header) + " |")
        print("| " + " | ".join(["---"] * len(header)) + " |")
        print("| " + " | ".join(time_row) + " |")

        print()

        print("# Memory")
        print("| " + " | ".join(header) + " |")
        print("| " + " | ".join(["---"] * len(header)) + " |")
        print("| " + " | ".join(memory_row) + " |")
    else:
        for support, aggregate_result in support_results:
            print(f"Support = {support:g}")
            print(aggregate_result.summary())


if __name__ == "__main__":
    main()
