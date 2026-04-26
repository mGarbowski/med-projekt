from argparse import ArgumentParser
from pathlib import Path

from .output import LCMOutputToFile
from .dataset import Dataset
from .lcm import LCMAlgorithm


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("-s", "--minsup", type=float, required=True)

    args = parser.parse_args()
    if not (0 <= args.minsup <= 1):
        raise ValueError("Minimum support must be between 0 and 1")

    with open(args.input) as input_file:
        dataset = Dataset.from_stream(input_file)

    output = LCMOutputToFile(args.output)
    lcm = LCMAlgorithm(
        relative_minimum_support=args.minsup, dataset=dataset, output=output
    )
    lcm.run()


if __name__ == "__main__":
    main()
