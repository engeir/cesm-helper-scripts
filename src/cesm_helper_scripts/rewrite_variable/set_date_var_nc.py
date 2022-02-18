import os
import sys

import netCDF4 as nc


def rewrite_date_variable() -> None:
    # Check file path
    data = sys.stdin.readlines()
    new_path = data[0].strip("\n")
    if not isinstance(new_path, str) or new_path[-3:] != ".nc":
        raise TypeError(f"Are you sure {new_path} is a valid netCDF file?")
    if not os.path.exists(new_path):
        raise FileNotFoundError(f"Cannot find file named {new_path}.")

    # Open file
    with nc.Dataset(new_path, "r+") as ncfile:
        # Fix values
        for i, d in enumerate(ncfile.variables["date"][:]):
            n = 1 if i < 12 else 9999
            ncfile.variables["date"][i] = d % 10000 + n * 10000


if __name__ == "__main__":
    rewrite_date_variable()
