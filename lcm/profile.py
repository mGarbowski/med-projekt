import tracemalloc
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter_ns

from .dataset import Dataset
from .lcm import LCMAlgorithm


@dataclass(frozen=True)
class SingleBenchmarkResult:
    time_ns: int
    mem_before_current: int
    mem_before_peak: int
    mem_after_current: int
    mem_after_peak: int


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
    mem_before_current: AggregatedValue
    mem_before_peak: AggregatedValue
    mem_after_current: AggregatedValue
    mem_after_peak: AggregatedValue

    @classmethod
    def aggregate(cls, results: list[SingleBenchmarkResult]):
        return cls(
            time=AggregatedValue.from_values([r.time_ns / 1000 for r in results], "ms"),
            mem_before_current=AggregatedValue.from_values(
                [r.mem_before_current / 1024 for r in results], "KiB"
            ),
            mem_before_peak=AggregatedValue.from_values(
                [r.mem_before_peak / 1024 for r in results], "KiB"
            ),
            mem_after_current=AggregatedValue.from_values(
                [r.mem_after_current / 1024 for r in results], "KiB"
            ),
            mem_after_peak=AggregatedValue.from_values(
                [r.mem_after_peak / 1024 for r in results], "KiB"
            ),
        )

    def summary(self):
        return (
            f"Time: {self.time}\n"
            f"Current before: {self.mem_before_current}\n"
            f"Current after: {self.mem_after_current}\n"
            f"Peak during run: {self.mem_after_peak}\n"
        )


def benchmark_run(dataset: Dataset, min_support: float) -> SingleBenchmarkResult:
    tracemalloc.start()
    time_start = perf_counter_ns()
    before_current, before_peak = tracemalloc.get_traced_memory()

    lcm = LCMAlgorithm(relative_minimum_support=min_support, dataset=dataset)
    _ = lcm.run()

    after_current, after_peak = tracemalloc.get_traced_memory()
    time_end = perf_counter_ns()
    tracemalloc.stop()

    return SingleBenchmarkResult(
        time_ns=time_end - time_start,
        mem_before_current=before_current,
        mem_before_peak=before_peak,
        mem_after_current=after_current,
        mem_after_peak=after_peak,
    )


# TODO ensure assertions are disabled for profiling
def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-s", "--minsup", type=float, required=True)
    parser.add_argument("-n", "--num_samples", type=int, default=100)

    args = parser.parse_args()
    if not (0 <= args.minsup <= 1):
        raise ValueError("Minimum support must be between 0 and 1")

    with open(args.input) as input_file:
        dataset = Dataset.from_stream(input_file)

    results = [benchmark_run(dataset, args.minsup) for _ in range(args.num_samples)]
    aggregaet_results = BenchmarkResult.aggregate(results)
    print(aggregaet_results.summary())


if __name__ == "__main__":
    main()
