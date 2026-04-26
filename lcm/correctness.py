"""Script for comparing results of SPMF and this implementation of LCM algorithm"""

import os
import tempfile
from pathlib import Path
from pprint import pprint

from lcm.dataset import Dataset
from lcm.lcm import LCMAlgorithm
from lcm.output import LCMOutputToFile


def compute_spmf(input_file: Path, output_file: Path, min_support: float):
    support_text = f"{min_support * 100}%"
    os.system(
        f"java -jar extern/spmf.jar run LCM {input_file} {output_file} {support_text}"
    )


def compute_this(input_file: Path, output_file: Path, min_support: float):
    with open(input_file) as f:
        dataset = Dataset.from_stream(f)
    output = LCMOutputToFile(output_file)
    lcm = LCMAlgorithm(
        relative_minimum_support=min_support, dataset=dataset, output=output
    )
    lcm.run()


def do_results_match(spmf_file: Path, my_file: Path) -> bool:
    return spmf_file.read_text() == my_file.read_text()


def is_same_result(input_file: Path, min_support: float):
    with tempfile.NamedTemporaryFile(delete_on_close=True) as spmf_file:
        with tempfile.NamedTemporaryFile(delete_on_close=True) as my_file:
            spmf_path, my_path = Path(spmf_file.name), Path(my_file.name)
            compute_spmf(input_file, spmf_path, min_support)
            compute_this(input_file, my_path, min_support)
            return do_results_match(spmf_path, my_path)


def main():
    files = [
        Path("data/test_files/contextPasquier99.txt"),
        Path("data/test_files/contextCFPGrowth.txt"),
        Path("data/test_files/contextIndirect.txt"),
        Path("data/test_files/contextInverse.txt"),
    ]
    min_support_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    errors = []
    for file in files:
        for min_support in min_support_values:
            try:
                if not is_same_result(file, min_support):
                    errors.append((file, min_support))
            except Exception:
                errors.append((file, min_support))

    print("No match for")
    pprint(errors)


if __name__ == "__main__":
    main()
