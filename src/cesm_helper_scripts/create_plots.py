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
import cftime
import cosmoplots
import matplotlib
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from mpl_toolkits.basemap import Basemap
from xmovie import Movie

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
parser.add_argument("-i", "--input", type=str, nargs="+", help="Input .nc file(s).")
parser.add_argument("-o", "--output", help="Name of the output files.")
parser.add_argument(
    "-m",
    "--map",
    default="cyl",
    type=str,
    help="Set the map projection. Note that not all projections support limiting the lat/lon region.",
)
parser.add_argument(
    "--maps",
    action="store_true",
    help="Show URL to a list of available map projections.",
)
parser.add_argument(
    "-plt",
    "--plots",
    type=str,
    nargs="+",
    help="List of the plots that should be generated.",
)
parser.add_argument(
    "--slice",
    help="Used to slice the DataArray. Slices are defined in quotes in the same way they would be inside square brackets.",
)
parser.add_argument(
    "-t", "--timestamp", type=int, default=0, help="Time index of spherical plot."
)
parser.add_argument(
    "--latlon",
    default=[None, None, None, None],
    type=int,
    nargs=4,
    help="Latitude (low, high) and longitude (low, high).",
)
parser.add_argument(
    "--vrange",
    default=[None, None],
    type=str,
    nargs=2,
    help="vmin and vmax, used when plotting three dimensions. Setting one to 'None' yields the default value of min and max.",
)

args = parser.parse_args()
if args.maps:
    print(
        "Find all available map projections at "
        + "https://matplotlib.org/basemap/api/basemap_api.html#module-mpl_toolkits.basemap"
    )
    sys.exit(0)
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
lat_1, lat_2, lon_1, lon_2 = args.latlon
map_proj = args.map
_VMIN = None if str(args.vrange[0]) == "None" else float(args.vrange[0])
_VMAX = None if str(args.vrange[1]) == "None" else float(args.vrange[1])


def _file_exist(end):
    """Check if output file exist."""
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
    _file_exist("_simple.png")
if "sphere" in args.plots:
    _file_exist("_sphere.png")
if "anim" in args.plots:
    _file_exist(".mp4")

# === <CODE> ===
__FIG_STD__ = cosmoplots.set_rcparams_dynamo(matplotlib.rcParams)


def _latlon_over_time(
    da: xr.DataArray, fig: plt.figure, time: int, *args, vmin=0, vmax=16, **kwargs
):
    __FIG_STD__[2] = 0.7
    # fig = plt.figure()
    fig.subplots()
    # ax = fig.add_axes(__FIG_STD__)
    # the_map = Basemap(projection="moll", lon_0=0, lat_0=0, resolution="l")
    the_map = Basemap(
        projection=map_proj,
        lon_0=0,
        lat_0=0,
        llcrnrlon=lon_1,
        llcrnrlat=lat_1,
        urcrnrlon=lon_2,
        urcrnrlat=lat_2,
        resolution="l",
    )
    the_map.drawcoastlines(linewidth=0.25)
    the_map.drawmeridians(np.arange(0, 360, 30), linewidth=0.25)
    the_map.drawparallels(np.arange(-90, 90, 30), linewidth=0.25)
    x, y = np.meshgrid(da.isel(time=time).lon.data, da.isel(time=time).lat.data)
    the_map.contourf(x, y, da.isel(time=time).data, latlon=True, vmin=vmin, vmax=vmax)
    # plt.title(time)
    # plt.colorbar()
    return None, None


def spherical_plot(da: xr.DataArray, ts: int, save="") -> None:
    """Create an image of latxlon at a given time step."""
    _latlon_over_time(da, fig := plt.figure(), ts)
    if save:
        plt.savefig(save)
    else:
        plt.savefig(f"{savepath}{output}_sphere.png")
    fig.clear()
    plt.close()


def xmov(da):
    """Show animation of Model output.

    Parameters
    ----------
    da: xr.DataArray
        Model data
    """
    vmin = da.min().values if _VMIN is None else _VMIN
    vmax = da.max().values * 0.8 if _VMAX is None else _VMAX
    mov = Movie(da.chunk({"time": 1}), _latlon_over_time, vmin=vmin, vmax=vmax)
    # FIXME: parallel gives several prompts
    mov.save(
        f"{savepath}{output}.mp4",
        progress=True,
        parallel=True,
        parallel_compute_kwargs=dict(scheduler="processes", num_workers=4),
        overwrite_existing=True,
        remove_movie=False,
        framerate=5,
        # verbose=True,
    )


def height_anim(da: xr.DataArray):
    """Animate latitude versus height/pressure through time."""
    if "lev" not in da.dims:
        xmov(da)
        return
    vmin = np.nanmin(da.mean(dim="lon").values) if _VMIN is None else _VMIN
    vmax = np.nanmax(da.mean(dim="lon").values) if _VMAX is None else _VMAX
    plt.rcParams["image.cmap"] = "gist_ncar"
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # 1 mb = 1 hPa
    hPa2alt = (1 - (da.lev / 1013.25) ** 0.190284) * 145366.45 * 0.3048
    block = amp.blocks.Pcolormesh(
        da.lat,
        hPa2alt,
        da.mean(dim="lon").values,
        norm=colors.LogNorm(vmin=vmin, vmax=vmax),
    )
    plt.colorbar(block.quad)
    time_float = cftime.date2num(da.time, "days since 0000-01-01") / 365
    timeline = amp.Timeline(time_float, fps=10)
    anim = amp.Animation([block], timeline)
    anim.controls()
    anim.save_gif(f"{savepath}{output}")
    anim.save(f"{savepath}{output}.mp4")


def attr_vs_time(da: xr.DataArray):
    """Create a plot of the DataArray variable over time."""
    # Compensate for the different width of grid cells at different latitudes.
    # https://xarray.pydata.org/en/stable/examples/area_weighted_temperature.html
    # Need mean = ( sum n*cos(lat) ) / ( sum cos(lat) )
    fig = plt.figure()
    _ = fig.add_axes(__FIG_STD__)
    weights = np.cos(np.deg2rad(da.lat))
    weights.name = "weights"
    air_weighted = da.weighted(weights)
    k_w = air_weighted.mean(("lon", "lat"))
    k_w.plot()
    plt.savefig(f"{savepath}{output}_simple.png")
    plt.close()


# === </CODE> ===
def main():
    """Run the main function."""
    multi_ds = xr.open_mfdataset(inputs, chunks="auto")
    # It is assumed that the first variable is the only variable, and as such, the right
    # variable.
    try:
        multi = getattr(multi_ds, list(multi_ds.data_vars)[0])
    except Exception as e:
        raise e
    if args.slice is not None:
        try:
            multi = multi[
                slice(
                    *map(
                        lambda x: int(x.strip()) if x.strip() else None,
                        args.slice.split(":"),
                    )
                )
            ]
        except Exception as e:
            raise IndexError(f"Slicing failed. Tried with `da[{args.slice}]`.") from e
    if "simple" in args.plots:
        attr_vs_time(multi)
    if "sphere" in args.plots:
        spherical_plot(multi, args.timestamp)
    if "anim" in args.plots:
        height_anim(multi)


if __name__ == "__main__":
    main()
