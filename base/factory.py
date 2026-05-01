from pathlib import Path
from typing import Optional, Literal
from enum import Enum

from .abstract_lcm import AbstractLCM
from lcm.lcm import LCMAlgorithm
from lcm.lcm_intersec import LCMAlgorithmIntersec
from lcm.dataset import Dataset, DatasetIntersec
from base.output import LCMOutputToFile, LCMOutputInMemory

from lcm_opt.lcm import LCMAlgorithmOpt
from lcm_opt.dataset import DatasetOpt

from extern.lcm_spmf import LCMSpmf

from line_profiler import profile


class AlgorithmVersion(Enum):
    SPMF = "spmf"
    CUSTOM = "custom"
    INTERSEC = "intersec"
    OPTIMIZED = "optimized"


class AlgorithmFactory:
    """Factory for creating algorithm instances."""

    @staticmethod
    # @profile
    def create(
        algorithm_version: AlgorithmVersion,
        input_file: Path,
        output_file: Path,
        min_support: float,
        output_mode: Literal["file", "memory"] = "file",
        spmf_jar: Optional[Path] = None,
    ) -> AbstractLCM:
        """
        Creates and returns an instance of the requested algorithm.

        Args:
            algorithm_version
            input_file: Path to the dataset file
            output_file: Path where the output should be saved
            min_support: Minimum support threshold (0.0 to 1.0)
            spmf_jar: Path to the SPMF jar file (required if algorithm_type is 'spmf')

        Returns:
            An instance of a class inheriting from BaseAlgorithm.
        """
        if output_mode == "memory":
            output_handler = LCMOutputInMemory(output_file)
        else:
            output_handler = LCMOutputToFile(output_file)

        match algorithm_version:
            case AlgorithmVersion.CUSTOM:
                with open(input_file) as f:
                    dataset = Dataset.from_stream(f)
                return LCMAlgorithm(
                    relative_minimum_support=min_support,
                    dataset=dataset,
                    output=output_handler,
                )

            case AlgorithmVersion.INTERSEC:
                with open(input_file) as f:
                    dataset = DatasetIntersec.from_stream(f)
                return LCMAlgorithmIntersec(
                    relative_minimum_support=min_support,
                    dataset=dataset,
                    output=output_handler,
                )

            case AlgorithmVersion.OPTIMIZED:
                with open(input_file) as f:
                    dataset = DatasetOpt.from_stream(f)
                return LCMAlgorithmOpt(
                    relative_minimum_support=min_support,
                    dataset=dataset,
                    output=output_handler,
                )

            case AlgorithmVersion.SPMF:
                if not spmf_jar or not spmf_jar.exists():
                    raise FileNotFoundError(f"SPMF jar not found at: {spmf_jar}")
                return LCMSpmf(
                    spmf_jar=spmf_jar,
                    input_file=input_file,
                    output_file=output_file,
                    min_support=min_support,
                )

            case _:
                raise ValueError(f"Unknown algorithm type: {algorithm_version}")
