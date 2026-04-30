import os
import sys
import tempfile
import tracemalloc
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter_ns

from lcm.output import LCMOutputToFile
from lcm.dataset import Dataset
from lcm.lcm import LCMAlgorithm


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
            time=AggregatedValue.from_values([r.time_ns / 1000 for r in results], "us"),
            mem_delta_current=AggregatedValue.from_values(
                [r.mem_delta_current / 1024 for r in results], "KiB"
            ),
            mem_after_peak=AggregatedValue.from_values(
                [r.mem_after_peak / 1024 for r in results], "KiB"
            ),
        )

    def summary(self):
        return f"Time: {self.time}\nPeak memory use: {self.mem_after_peak}\n"


def benchmark_run(dataset_file: Path, min_support: float) -> SingleBenchmarkResult:
    tracemalloc.start()
    tracemalloc.reset_peak()
    time_start = perf_counter_ns()
    before_current, before_peak = tracemalloc.get_traced_memory()

    with open(dataset_file) as input_file:
        dataset = Dataset.from_stream(input_file)

    with tempfile.NamedTemporaryFile(delete_on_close=True) as output_file:
        output = LCMOutputToFile(Path(output_file.name))
        lcm = LCMAlgorithm(
            relative_minimum_support=min_support, dataset=dataset, output=output
        )
        lcm.run()

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

    args = parser.parse_args()
    if not (0 <= args.minsup <= 1):
        raise ValueError("Minimum support must be between 0 and 1")

    if os.environ.get("PYTHONOPTIMIZE", "") != "1":
        print(
            "WARNING: PYTHONOPTIMIZE environment variable is not set, expensive assertions will run during profiling",
            file=sys.stderr,
        )

    results = [benchmark_run(args.input, args.minsup) for _ in range(args.num_samples)]
    aggregate_results = BenchmarkResult.aggregate(results)
    print(aggregate_results.summary())


if __name__ == "__main__":
    main()
