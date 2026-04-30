"""Parametrized integration tests comparing LCM against SPMF reference implementation."""

import subprocess
import tempfile
from pathlib import Path

import pytest

from lcm.dataset import Dataset
from lcm.lcm import LCMAlgorithm
from base.output import LCMOutputToFile


@pytest.fixture(scope="module")
def spmf_jar_path() -> Path:
    """Locate SPMF jar file."""
    jar_path = Path("extern/spmf.jar")
    if not jar_path.exists():
        pytest.skip(f"SPMF jar not found at {jar_path}")
    return jar_path


@pytest.fixture
def temp_files():
    """Provide temporary files for SPMF and LCM output."""
    with tempfile.NamedTemporaryFile(delete=False) as spmf_file:
        with tempfile.NamedTemporaryFile(delete=False) as my_file:
            spmf_path = Path(spmf_file.name)
            my_path = Path(my_file.name)
            yield spmf_path, my_path
            # Cleanup
            spmf_path.unlink(missing_ok=True)
            my_path.unlink(missing_ok=True)


def _compute_spmf(
    spmf_jar: Path, input_file: Path, output_file: Path, min_support: float
) -> None:
    """Compute closed frequent itemsets using SPMF."""
    support_text = f"{min_support * 100}%"
    subprocess.run(
        [
            "java",
            "-jar",
            str(spmf_jar),
            "run",
            "LCM",
            str(input_file),
            str(output_file),
            support_text,
        ],
        capture_output=True,
        check=True,
    )


def _compute_this(input_file: Path, output_file: Path, min_support: float) -> None:
    """Compute closed frequent itemsets using our LCM implementation."""
    with open(input_file) as f:
        dataset = Dataset.from_stream(f)
    output = LCMOutputToFile(output_file)
    lcm = LCMAlgorithm(
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
    temp_files: tuple[Path, Path],
    input_file: Path,
    min_support: float,
) -> None:
    """Test that LCM output matches SPMF for given input and support threshold."""
    if not input_file.exists():
        pytest.skip(f"Test file not found: {input_file}")

    spmf_out, my_out = temp_files

    _compute_spmf(spmf_jar_path, input_file, spmf_out, min_support)
    _compute_this(input_file, my_out, min_support)

    spmf_result = spmf_out.read_text()
    my_result = my_out.read_text()

    assert spmf_result == my_result, (
        f"Results differ for {input_file.name} with min_support={min_support}"
    )
