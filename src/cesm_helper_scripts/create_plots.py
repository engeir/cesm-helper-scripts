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

import animatplot as amp
import cartopy.crs as ccrs
import cftime
import cosmoplots
import matplotlib
import matplotlib.animation as animation
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from rich.progress import track

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
__FIG_STD__ = cosmoplots.set_rcparams_dynamo(matplotlib.rcParams)


def spherical_plot(time_temp, time=0, save=""):
    # projections: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
    # PlateCarree(), Orthographic(-80, 35)
    __FIG_STD__[2] = 0.7
    fig = plt.figure()
    ax = fig.add_axes(__FIG_STD__, projection=ccrs.PlateCarree())
    if not save:
        vmin = time_temp.isel(time=time).min().values
        vmax = time_temp.isel(time=time).max().values
    else:
        vmin = time_temp.min().values
        vmax = time_temp.max().values
    _ = time_temp.isel(time=time).plot(
        # subplot_kws=dict(projection=ccrs.Mollweide(), facecolor="gray"),
        transform=ccrs.PlateCarree(),
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_global()
    ax.coastlines()
    if not save:
        plt.savefig(f"{savepath}{output}_sphere.png")
    else:
        plt.savefig(save)
    fig.clear()
    plt.close()


def anim_medium(signal: xr.DataArray) -> None:
    """Create plot from each time step.

    From https://medium.com/udacity/creating-map-animations-with-python-97e24040f17b

    Parameters
    ----------
    signal: xarray.DataArray
        The signal to plot.
    """
    if not os.path.exists(f"{savepath}{output}"):
        os.makedirs(f"{savepath}{output}")
    for ii in track(range(1488, len(signal))):
        # date = signal.time[ii]
        spherical_plot(
            signal,
            ii,
            save=os.path.join(f"{savepath}{output}", f"frame_{ii:04d}.png"),
        )
    print(
        f"Now, run: ffmpeg -framerate 21 -i {savepath}{output}/frame_%4d.png -c:v h264 -r 30 -s 1920x1080 ./out.mp4"
    )


def anim(
    dataset: xr.DataArray,
) -> None:
    """Show animation of Model output.

    Parameters
    ----------
    dataset: xr.DataArray,
        Model data
    """
    fig = plt.figure()
    ax = fig.add_axes(__FIG_STD__, projection=ccrs.PlateCarree())
    # div = make_axes_locatable(ax)
    # cax = div.append_axes("right", "5%", "5%")
    vmax = np.nanmax(dataset.values)
    vmin = np.nanmin(dataset.values)

    frames = []

    for timestep in dataset.time.values:
        frame = dataset.sel(time=timestep).values
        frames.append(frame)

    cv0 = frames[0]
    im = ax.imshow(
        cv0,
        origin="lower",
        transform=ccrs.PlateCarree(),
        norm=colors.LogNorm(vmin=vmin, vmax=vmax),
    )
    # fig.colorbar(im, cax=cax)
    tx = ax.set_title("t = 0")

    def animate(i: int) -> None:
        arr = frames[i]
        now = dataset.time.values[i]
        im.set_data(arr)
        im.set_clim(vmin, vmax)
        tx.set_text(f"t = {now}")

    ani = animation.FuncAnimation(
        fig, animate, frames=dataset["time"].values.size, interval=1
    )
    ani.save(f"{savepath}{output}.mp4", writer="ffmpeg", fps=20)
    plt.show()


def anim3(signal):
    vmin = signal.min().values
    vmax = signal.max().values * 0.7
    fig = plt.figure()
    __FIG_STD__[2] = 0.7
    ax = fig.add_axes(__FIG_STD__, projection=ccrs.Robinson())
    image = signal.isel(time=0).plot.imshow(
        ax=ax,
        transform=ccrs.PlateCarree(),
        animated=True,
        # vmin=vmin,
        # vmax=vmax,
        norm=colors.LogNorm(vmin=vmin, vmax=vmax),
    )
    ax.coastlines()

    def update(t):
        # Update the plot for a specific time
        # print(t)
        ax.set_title("time = %s" % t)
        image.set_array(signal.sel(time=t))
        return (image,)

    # Run the animation, applying `update()` for each of the times in the variable
    anim = animation.FuncAnimation(fig, update, frames=signal.time.values, blit=False)

    # Save to file or display on screen
    anim.save(f"{savepath}{output}.mp4", writer="ffmpeg", fps=20)
    plt.show()


def anim2(signal):
    vmax = np.nanmax(signal.values)
    vmin = np.nanmin(signal.values)
    # fig = plt.figure()
    # _ = fig.add_axes(__FIG_STD__)
    # block = signal.plot.imshow(animate_over='time')
    block = amp.blocks.Pcolormesh(
        signal.lon,
        signal.lat,
        signal.values,
        vmin=vmin,
        vmax=vmax,
        # norm=colors.LogNorm(vmin=vmin, vmax=vmax),
    )
    plt.colorbar(block.quad)
    time_float = cftime.date2num(signal.time, "days since 0000-01-01") / 365
    timeline = amp.Timeline(time_float, fps=10)
    anim = amp.Animation([block], timeline)
    anim.controls()
    anim.save_gif(f"{savepath}{output}")
    anim.save(f"{savepath}{output}.mp4")
    plt.show()


def height_anim(signal):
    if "lev" not in signal.dims:
        anim3(signal)
        return
    # vmax = np.nanmax(signal.mean(dim="lon").values)
    # vmin = np.nanmin(signal.mean(dim="lon").values)
    vmax = 150
    vmin = 350
    plt.rcParams["image.cmap"] = "gist_ncar"
    block = amp.blocks.Pcolormesh(
        signal.lat,
        signal.lev,
        signal.mean(dim="lon").values,
        # vmin=vmin,
        # vmax=vmax,
        norm=colors.LogNorm(vmin=vmin, vmax=vmax),
    )
    plt.colorbar(block.quad)
    time_float = cftime.date2num(signal.time, "days since 0000-01-01") / 365
    timeline = amp.Timeline(time_float, fps=10)
    anim = amp.Animation([block], timeline)
    anim.controls()
    anim.save_gif(f"{savepath}{output}")
    anim.save(f"{savepath}{output}.mp4")
    plt.show()


def attr_vs_time(sigmal):
    # Compensate for the different width of grid cells at different latitudes.
    # https://xarray.pydata.org/en/stable/examples/area_weighted_temperature.html
    # Need mean = ( sum n*cos(lat) ) / ( sum cos(lat) )
    fig = plt.figure()
    _ = fig.add_axes(__FIG_STD__)
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
    if "simple" in args.plots:
        attr_vs_time(multi)
    if "sphere" in args.plots:
        spherical_plot(multi)
    if "anim" in args.plots:
        # anim3(multi)
        height_anim(multi)


if __name__ == "__main__":
    main()
