"""Run the `gen_agg` script on the test data."""

import os
import subprocess

import create_data as cd
import numpy as np


class RunGenAgg:
    def __init__(self) -> None:
        here = os.path.basename(abs_path := os.path.abspath("."))
        if here == "cesm-helper-scripts":
            self.data_path = os.path.join("tests", "data")
            script_path = os.path.join("src", "cesm_helper_scripts")
        elif here == "tests":
            self.data_path = "data"
            script_path = os.path.join("..", "src", "cesm_helper_scripts")
        else:
            raise OSError(
                "You are in the wrong path or something. I tried to find ./tests/data,"
                f" but could only find absolute path {abs_path}, and that ends in the"
                f" {here} directory."
            )
        self.script = os.path.join(script_path, "gen_agg")

    def get_file_list(self) -> list[str]:
        return os.listdir(self.data_path)

    def simulate(self, splits: int = 1) -> None:
        """Simulate generation of aggregated variables.

        Parameters
        ----------
        splits : int
            Specify the number of files the aggregated data should be split into.
        """
        data = self.get_file_list()
        data.sort()
        steps = int(np.ceil(len(data) / splits))
        file_list: list[list[str]] = [
            data[x : x + steps] for x in range(0, len(data), steps)
        ]
        for i, chunk in enumerate(file_list):
            if return_code := subprocess.call(
                [
                    "python",
                    self.script,
                    "-a",
                    "FLNT",
                    "-p",
                    self.data_path,
                    "-i",
                    # "simulation.cam*",
                    *chunk,
                    "-o",
                    f"FLNT_{i}",
                ]
            ):
                print(f"Return code: {return_code}")


def main() -> None:
    cd.main()
    s = RunGenAgg()
    s.get_file_list()
    s.simulate(3)


if __name__ == "__main__":
    main()
