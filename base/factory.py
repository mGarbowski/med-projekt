from pathlib import Path
from typing import Optional

from .abstract_lcm import AbstractLCM
from lcm.lcm import LCMAlgorithm
from lcm.dataset import Dataset
from base.output import LCMOutputToFile

from lcm_opt.lcm import LCMAlgorithmOpt
from lcm_opt.dataset import DatasetOpt

from extern.lcm_original import LCMOriginal


class AlgorithmFactory:
    """Factory for creating algorithm instances."""

    @staticmethod
    def create(
        algorithm_type: str,
        input_file: Path,
        output_file: Path,
        min_support: float,
        spmf_jar: Optional[Path] = None,
    ) -> AbstractLCM:
        """
        Creates and returns an instance of the requested algorithm.

        Args:
            algorithm_type: 'custom' or 'spmf'
            input_file: Path to the dataset file
            output_file: Path where the output should be saved
            min_support: Minimum support threshold (0.0 to 1.0)
            spmf_jar: Path to the SPMF jar file (required if algorithm_type is 'spmf')

        Returns:
            An instance of a class inheriting from BaseAlgorithm.
        """
        if algorithm_type == "custom":
            with open(input_file) as f:
                dataset = Dataset.from_stream(f)
            output = LCMOutputToFile(output_file)
            return LCMAlgorithm(
                relative_minimum_support=min_support, dataset=dataset, output=output
            )

        elif algorithm_type == "optimized":
            with open(input_file) as f:
                dataset = DatasetOpt.from_stream(f)
            output = LCMOutputToFile(output_file)
            return LCMAlgorithmOpt(
                relative_minimum_support=min_support, dataset=dataset, output=output
            )

        elif algorithm_type == "spmf":
            if not spmf_jar or not spmf_jar.exists():
                raise FileNotFoundError(f"SPMF jar not found at: {spmf_jar}")
            return LCMOriginal(
                spmf_jar=spmf_jar,
                input_file=input_file,
                output_file=output_file,
                min_support=min_support,
            )

        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
