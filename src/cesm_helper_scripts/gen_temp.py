#! /cluster/home/een023/.virtualenvs/p3/bin/python
"""Send in a path to .nc files and the name of the files.
Either as a list of many files or with the asterisk (wildcard?) notation, `"*.nc"`.
Note that the wildcard notation must be sent in as a string like the above example.

Then creates a summary file for temperature.
Usage:
    gen_temp.py -p look/here -i one.nc two.nc -sp input -o output_name
"""

import argparse
import datetime
import glob
import os
import sys
from typing import Union

import xarray as xr

parser = argparse.ArgumentParser(
    description="Create a file containing only the temperature variable."
)
parser.add_argument("-p", "--path", help="path to .nc files")
parser.add_argument("-sp", "--savepath", help="path to where the .nc file is saved")
parser.add_argument(
    "-i",
    "--input",
    type=str,
    nargs="+",
    help='input .nc files. Use quotes around *, e.g. "*.nc".',
)
parser.add_argument("-o", "--output", help="output .nc files")
parser.add_argument(
    "-y",
    "--year",
    action="store_true",
    help="If given, a 12 month running average is computed.",
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
if output.split(".")[-1] != "nc":
    output += ".nc"
# Correct the path argument
if args.path is not None:
    path = args.path + "/" if args.path[-1] != "/" else args.path
else:
    path = ""
# Combine the path with all files
inputs = [
    f"{path}{file}"
    if file.split(".")[-1] == "nc" or "*" in file
    else f"{path}{file}.nc"
    for file in args.input
]
# If an asterisk (*) is used, all other files are discarded
the_input: Union[str, list[str]]
if any("*" in f for f in inputs):
    val = inputs[[i for i, s in enumerate(inputs) if "*" in s][0]]
    the_input = str(val)
    if not glob.glob(the_input):
        print(f"I could not find {the_input}")
        print("Exiting...")
        sys.exit()
else:
    the_input = inputs
    for input_ in the_input:
        if not glob.glob(input_):
            print(f"I could not find {input_}")
            print("Exiting...")
            sys.exit()
# Correct the savepath argument
savepath = args.savepath if args.savepath is not None else ""
savepath = path if savepath == "input" else savepath
savepath = savepath + "/" if savepath != "" and savepath[-1] != "/" else savepath
# Check if output file exist
if os.path.exists(savepath + output):
    ans = str(
        input(
            f'The file {output} already exist in {savepath[:-1] if savepath != "" else "this directory"}. Do you want to overwrite this? (y/n)\t'
        )
    )
    if ans != "y":
        print("Exiting...")
        sys.exit()
    else:
        print("Saving to", savepath + output)
else:
    ans = str(input(f"Save to {savepath}{output}? (y/n)\t"))
    if ans != "y":
        print("Exiting...")
        sys.exit()
    else:
        if savepath != "":
            os.makedirs(savepath, exist_ok=True)
        print("Saving to", savepath + output)

dataset = xr.open_mfdataset(the_input)
dataset = xr.decode_cf(dataset)
ds = dataset.TREFHT  # This is probably the correct one, reference height temperature
# ds = dataset.T
if args.year:
    ds = ds.chunk({"time": 12})
    r = ds.rolling(time=12)
    ds = r.mean()
ds.to_netcdf(savepath + output)
