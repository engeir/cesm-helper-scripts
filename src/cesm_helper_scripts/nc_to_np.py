"""Send in a path to a .nc file and the name of the file.

Then creates a numpy array of the attribute as a function of time, and saves to a
npz-file.

Usage:
    temp_nc_to_np -i single_file.nc -p up/three/layers -sp save_two_layers_below_input -o output_name
"""


import argparse
import datetime
import glob
import os
import sys

import cftime
import numpy as np
import xarray as xr

parser = argparse.ArgumentParser(
    description="Create a numpy array of the attribute from a .nc file."
)
parser.add_argument(
    "-p",
    "--path",
    default=".",
    type=str,
    help="Relative path to .nc file. If not given, the current directory is used.",
)
parser.add_argument(
    "-sp",
    "--savepath",
    default="input",
    type=str,
    help="Relative path to where the file is saved. If the savepath is -sp input, "
    + "the same path is used here as is for the path parameter. "
    + "If not given, the current directory is used.",
)
parser.add_argument("-i", "--input", type=str, nargs="+", help="Input .nc file(s).")
parser.add_argument("-o", "--output", help="Name of the output files.")
parser.add_argument(
    "-y",
    "--yes",
    default=False,
    help="Answer yes to all questions.",
    action="store_true",
)

args = parser.parse_args()
# Correct the input argument
if args.input is None:
    raise ValueError("you must give the input files")
# Correct the output argument
if args.output is None:
    output = datetime.date.today().strftime("%Y%m%d")
else:
    output = args.output
# Correct the path argument
if args.path is not None:
    path = f"{args.path}/" if args.path[-1] != "/" else args.path
else:
    path = ""
# Combine the path with all files
inputs = [
    f"{path}{input_}" if input_.split(".")[-1] == "nc" else f"{path}{input_}.nc"
    for input_ in args.input
]
for input_ in inputs:
    if not glob.glob(input_):
        print(f"I could not find {input_}")
        print("Exiting...")
        sys.exit()
# Correct the savepath argument
savepath = args.savepath if args.savepath is not None else ""
savepath = path if savepath == "input" else savepath
savepath = f"{savepath}/" if savepath != "" and savepath[-1] != "/" else savepath

# Check if output file exist


def file_exist(end):
    """Check if the file exist and if it should be overwritten.

    Parameters
    ----------
    end : str
        The file extension.
    """
    if os.path.exists(savepath + output + end):
        ans = str(
            input(
                f"The file {output}{end} already exist in "
                + f'"{savepath[:-1] if savepath != "" else "this directory"}". '
                + "Do you want to overwrite this? (y/n)\t"
            )
        )
        if ans == "y":
            print("Saving to", savepath + output + end)
        else:
            print("Exiting without creating any file...")
            sys.exit()
    elif not args.yes:
        ans = str(input(f"Save to {savepath}{output}{end}? (y/n)\t"))
        if ans != "y":
            print("Exiting without creating any file...")
            sys.exit()
    else:
        if savepath != "":
            os.makedirs(savepath, exist_ok=True)
        print("Saving to", savepath + output + end)


file_exist(".npz")

# Do some work


def nc_to_np(temps: xr.Dataset):
    """Convert the data in an xr.Datset object to a numpy array, and save to .npz.

    Parameters
    ----------
    temps : xr.Dataset
        The data to be converted.
    """
    # Compensate for the different width of grid cells at different latitudes.
    # https://xarray.pydata.org/en/stable/examples/area_weighted_temperature.html
    # Need mean = ( sum n*cos(lat) ) / ( sum cos(lat) )
    weights = np.cos(np.deg2rad(temps.lat))
    weights.name = "weights"
    air_weighted = temps.weighted(weights)
    k_w = air_weighted.mean(("lon", "lat"))
    # Sets the time in decimal years. Calendar is without leap years.
    shift = str(k_w["time"].data[0])[:4]
    t_0 = f"{shift}-01-01 00:00:00"
    t = (
        cftime.date2num(
            k_w["time"].data, f"days since {t_0}", calendar="noleap", has_year_zero=True
        )
        + float(shift) * 365
    ) / 365
    T = k_w.data
    lev = getattr(k_w, "lev", None)
    ilev = getattr(k_w, "ilev", None)
    np.savez(f"{savepath}{output}.npz", data=T, times=t, t_0=t_0, lev=lev, ilev=ilev)


def main():
    """Run the main function for the script."""
    array_ds = xr.open_mfdataset(inputs, chunks="auto")
    if len(list(array_ds.data_vars)) != 1:
        raise ValueError(
            "The input file must contain only one variable. "
            + f"Found {list(array_ds.data_vars)}"
        )
    array = getattr(array_ds, list(array_ds.data_vars)[0])
    nc_to_np(array)


if __name__ == "__main__":
    main()
