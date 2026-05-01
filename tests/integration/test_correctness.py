"""Parametrized integration tests comparing LCM versions against SPMF reference implementation."""

from pathlib import Path

import pytest

from lcm.dataset import Dataset, DatasetIntersec
from lcm.lcm import LCMAlgorithm
from lcm.lcm_intersec import LCMAlgorithmIntersec
from lcm_opt.dataset import DatasetOpt
from lcm_opt.lcm import LCMAlgorithmOpt
from extern.lcm_spmf import LCMSpmf
from base.output import LCMOutputToFile


@pytest.fixture(scope="module")
def spmf_jar_path() -> Path:
    """Locate SPMF jar file."""
    jar_path = Path("extern/spmf.jar")
    if not jar_path.exists():
        pytest.skip(f"SPMF jar not found at {jar_path}")
    return jar_path


def _compute_spmf(
    spmf_jar: Path, input_file: Path, output_file: Path, min_support: float
) -> None:
    """Compute closed frequent itemsets using SPMF."""
    LCMSpmf(spmf_jar, input_file, output_file, min_support).run()


def _compute_this(input_file: Path, output_file: Path, min_support: float) -> None:
    """Compute closed frequent itemsets using our LCM implementation."""
    with open(input_file) as f:
        dataset = Dataset.from_stream(f)
    output = LCMOutputToFile(output_file)
    lcm = LCMAlgorithm(
        relative_minimum_support=min_support, dataset=dataset, output=output
    )
    lcm.run()


def _compute_this_intersec(
    input_file: Path, output_file: Path, min_support: float
) -> None:
    """Compute closed frequent itemsets using our LCM with transactions intersections implementation."""
    with open(input_file) as f:
        dataset = DatasetIntersec.from_stream(f)
    output = LCMOutputToFile(output_file)
    lcm = LCMAlgorithmIntersec(
        relative_minimum_support=min_support, dataset=dataset, output=output
    )
    lcm.run()


def _compute_this_opt(input_file: Path, output_file: Path, min_support: float) -> None:
    """Compute closed frequent itemsets using our optimized LCM implementation."""
    with open(input_file) as f:
        dataset = DatasetOpt.from_stream(f)
    output = LCMOutputToFile(output_file)
    lcm = LCMAlgorithmOpt(
        relative_minimum_support=min_support, dataset=dataset, output=output
    )
    lcm.run()


@pytest.mark.parametrize(
    ("input_file",),
    [
        (Path("data/test_files/contextPasquier99.txt"),),
        (Path("data/test_files/contextCFPGrowth.txt"),),
        (Path("data/test_files/contextIndirect.txt"),),
        (Path("data/test_files/contextInverse.txt"),),
    ],
)
@pytest.mark.parametrize(
    ("min_support",),
    [
        (0.1,),
        (0.2,),
        (0.3,),
        (0.4,),
        (0.5,),
        (0.6,),
        (0.7,),
        (0.8,),
        (0.9,),
    ],
)
def test_lcm_correctness_against_spmf(
    spmf_jar_path: Path,
    tmp_path: Path,
    input_file: Path,
    min_support: float,
) -> None:
    """Test that LCM output matches SPMF for given input and support threshold."""
    if not input_file.exists():
        pytest.skip(f"Test file not found: {input_file}")

    spmf_out = tmp_path / "spmf.txt"
    base_out = tmp_path / "base.txt"
    intersec_out = tmp_path / "intersec.txt"
    opt_out = tmp_path / "opt.txt"

    _compute_spmf(spmf_jar_path, input_file, spmf_out, min_support)
    _compute_this(input_file, base_out, min_support)

    spmf_result = spmf_out.read_text()
    base_result = base_out.read_text()

    assert spmf_result == base_result, (
        f"Results differ for base LCM tested on {input_file.name} with min_support={min_support}"
    )

    _compute_this_intersec(input_file, intersec_out, min_support)
    intersec_result = intersec_out.read_text()

    assert spmf_result == intersec_result, (
        f"Results differ for LCM with transactions intersections tested on {input_file.name} with min_support={min_support}"
    )

    _compute_this_opt(input_file, opt_out, min_support)
    opt_result = opt_out.read_text()

    assert spmf_result == opt_result, (
        f"Results differ for optimized LCM tested on {input_file.name} with min_support={min_support}"
    )
