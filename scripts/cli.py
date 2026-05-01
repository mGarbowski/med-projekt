import sys
from argparse import ArgumentParser
from pathlib import Path

from base.factory import AlgorithmFactory, AlgorithmVersion


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("-s", "--minsup", type=float, required=True)
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

    if args.algorithm == "spmf":
        print(
            "WARNING: You are using the Java implementation. tracemalloc will only measure memory used by the Python script! "
            "Memory allocated by the Java Virtual Machine (JVM) will not be tracked.",
            file=sys.stderr,
        )

    algorithm = AlgorithmFactory.create(
        algorithm_version=AlgorithmVersion(args.algorithm),
        input_file=args.input,
        output_file=args.output,
        min_support=args.minsup,
        output_mode=args.output_mode,
        spmf_jar=args.spmf_jar,
    )

    algorithm.run()
    algorithm.close()


if __name__ == "__main__":
    main()
