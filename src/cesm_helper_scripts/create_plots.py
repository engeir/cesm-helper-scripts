#!/cluster/home/een023/.virtualenvs/p3/bin/python

"""Create plots of attribute data.

Send in a path to a .nc file and the name of the file. Then creates plots of the attribute
found in the file.

Usage:
    temp_plots -i single_file.nc -p up/three/layers -sp save_two_layers_below_input -o output_name -plt simple sphere anim
"""

import argparse
import datetime
import glob
import os
import sys

import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

parser = argparse.ArgumentParser(
    description="Create plots and animations wrt. the attribute of a .nc file. \
        Any number of plots can be generated: \
        (1) simple: Attribute vs time \
        (2) sphere: Attribute vs (lat vs lon) at time `t` \
        (3) anim:   Attribute vs (lat vs lon) animation.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
    help="Relative path to where the plot files are saved. If the savepath is -sp "
    + "input, the same path is used here as is for the path parameter. "
    + "If not given, the current directory is used.",
)
parser.add_argument("-i", "--input", type=str, help="Input .nc file.")
parser.add_argument("-o", "--output", help="Name of the output files.")
parser.add_argument(
    "-plt",
    "--plots",
    type=str,
    nargs="+",
    help="List of the plots that should be generated.",
)

args = parser.parse_args()
# Correct the input argument
if args.input is None:
    raise ValueError("you must give the input files")
if args.plots is None:
    raise ValueError(
        "you must specify what kind of plot you want (simple, sphere, anim)"
    )
if not set(args.plots).issubset({"simple", "sphere", "anim"}):
    raise ValueError("you must choose between: simple, sphere, anim")
# Correct the output argument
if args.output is None:
    output = datetime.date.today().strftime("%Y%m%d")
else:
    output = args.output
# Correct the path argument
if args.path is not None:
    path = args.path + "/" if args.path[-1] != "/" else args.path
else:
    path = ""
# Combine the path with all files
inputs = (
    f"{path}{args.input}"
    if args.input.split(".")[-1] == "nc"
    else f"{path}{args.input}.nc"
)
if not glob.glob(inputs):
    print(f"I could not find {inputs}")
    print("Exiting...")
    sys.exit()
# Correct the savepath argument
savepath = args.savepath if args.savepath is not None else ""
savepath = path if savepath == "input" else savepath
savepath = savepath + "/" if savepath != "" and savepath[-1] != "/" else savepath

# Check if output file exist


def file_exist(end):
    if os.path.exists(savepath + output + end):
        ans = str(
            input(
                f"The file {output}{end} already exist in "
                + f'{savepath[:-1] if savepath != "" else "this directory"}. '
                + "Do you want to overwrite this? (y/n)\t"
            )
        )
        if ans != "y":
            print("Exiting without making any plots...")
            sys.exit()
        else:
            print("Saving to", savepath + output + end)
    else:
        ans = str(input(f"Save to {savepath}{output}{end}? (y/n)\t"))
        if ans != "y":
            print("Exiting without making any plots...")
            sys.exit()
        else:
            if savepath != "":
                os.makedirs(savepath, exist_ok=True)
            print("Saving to", savepath + output + end)


if "simple" in args.plots:
    file_exist("_simple.png")
if "sphere" in args.plots:
    file_exist("_sphere.png")
if "anim" in args.plots:
    file_exist(".mp4")

# === <CODE> ===


def spherical_plot(time_temp):
    # projections: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
    # PlateCarree(), Orthographic(-80, 35)
    p = time_temp.isel(time=0).plot(
        subplot_kws=dict(projection=ccrs.Mollweide(), facecolor="gray"),
        transform=ccrs.PlateCarree(),
    )
    p.axes.set_global()
    p.axes.coastlines()
    plt.savefig(f"{savepath}{output}_sphere.png")
    plt.close()


def anim(signal):
    def make_figure():
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # generate a basemap with country borders, oceans and coastlines
        # ax.add_feature(cfeat.LAND)
        # ax.add_feature(cfeat.OCEAN)
        ax.add_feature(cfeat.COASTLINE)
        ax.add_feature(cfeat.BORDERS, linestyle="dotted")
        return fig, ax

    def draw(frame, add_colorbar):
        grid = signal[frame]
        # title = u"%s — %s" % (ds.t2m.long_name, str(
        #     time_temp.time[frame].values)[:19])
        # ax.set_title(title)
        return grid.plot(
            ax=ax,
            transform=ccrs.PlateCarree(),
            add_colorbar=add_colorbar,
            vmin=min_value,
            vmax=max_value,
        )

    def init():
        return draw(0, add_colorbar=True)

    def animate(frame):
        return draw(frame, add_colorbar=False)

    fig, ax = make_figure()

    frames = signal.time.size  # Number of frames
    min_value = signal.values.min()  # Lowest value
    max_value = signal.values.max()  # Highest value

    ani = animation.FuncAnimation(
        fig, animate, frames, interval=0.01, blit=False, init_func=init, repeat=False
    )
    ani.save(f"{savepath}{output}.mp4", writer=animation.FFMpegWriter(fps=8))
    plt.close(fig)


def attr_vs_time(sigmal):
    # Compensate for the different width of grid cells at different latitudes.
    # https://xarray.pydata.org/en/stable/examples/area_weighted_temperature.html
    # Need mean = ( sum n*cos(lat) ) / ( sum cos(lat) )
    weights = np.cos(np.deg2rad(sigmal.lat))
    weights.name = "weights"
    air_weighted = sigmal.weighted(weights)
    k_w = air_weighted.mean(("lon", "lat"))
    k_w.plot()
    plt.savefig(f"{savepath}{output}_simple.png")
    plt.show()
    plt.close()


# === </CODE> ===
def main():
    multi = xr.open_dataarray(inputs)
    # multi_T = multi_T.isel(lev=0)
    if "simple" in args.plots:
        attr_vs_time(multi)
    if "sphere" in args.plots:
        spherical_plot(multi)
    if "anim" in args.plots:
        anim(multi)


if __name__ == "__main__":
    main()
