import subprocess
from pathlib import Path

from base.abstract_lcm import AbstractLCM


class LCMOriginal(AbstractLCM):
    """Wrapper for the reference LCM implementation in the SPMF library (Java)."""

    def __init__(
        self, spmf_jar: Path, input_file: Path, output_file: Path, min_support: float
    ):
        self.spmf_jar = spmf_jar
        self.input_file = input_file
        self.output_file = output_file
        self.min_support = min_support

    def run(self) -> None:
        """Runs the Java process with the SPMF LCM algorithm."""
        support_text = f"{self.min_support * 100}%"
        subprocess.run(
            [
                "java",
                "-jar",
                str(self.spmf_jar),
                "run",
                "LCM",
                str(self.input_file),
                str(self.output_file),
                support_text,
            ],
            capture_output=True,
            check=True,
        )
