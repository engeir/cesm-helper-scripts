"""Run the `gen_agg` script on the test data."""

import os


class RunGenAgg:
    def __init__(self) -> None:
        here = os.path.basename(abs_path := os.path.abspath("."))
        if here == "cesm-helper-scripts":
            self.data_path = os.path.join("tests", "data")
            self.script_path = os.path.join("src", "cesm_helper_scripts")
        elif here == "tests":
            self.data_path = "data"
            self.script_path = os.path.join("..", "src", "cesm_helper_scripts")
        else:
            raise OSError(
                "You are in the wrong path or something. I tried to find ./tests/data,"
                f" but could only find absolute path {abs_path}, and that ends in the"
                f" {here} directory."
            )
        print(self.data_path)
        print(self.script_path)


def main() -> None:
    RunGenAgg()
    # s.simulate()


if __name__ == "__main__":
    main()
