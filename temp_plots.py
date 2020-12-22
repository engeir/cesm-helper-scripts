#! /cluster/home/een023/.virtualenvs/p3/bin/python
"""Send in a path to an .nc file and the name of the file.

Then creates plots of temperature.
"""

import glob
import os
import sys
import datetime
import argparse
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy.crs as ccrs
import cartopy.feature as cfeat

parser = argparse.ArgumentParser(
    description='Create plots and animations wrt. temperature from a .nc file. \
        Any number of plots can be generated: \
        (1) simpel: Temperature vs time \
        (2) sphere: Temperature vs (lat vs lon) at time `t` \
        (3) anim:   Temperature vs (lat vs lon) animation.')
parser.add_argument('-p', '--path', help='path to .nc file')
parser.add_argument('-sp', '--savepath',
                    help='path to where the plot files are saved')
parser.add_argument('-i', '--input', type=str,
                    help='input .nc files')
parser.add_argument('-o', '--output', help='output files')
parser.add_argument('-plt', '--plots', type=str, nargs='+',
                    help='list of the plots that should be generated')

args = parser.parse_args()
# Correct the input argument
if args.input is None:
    raise ValueError('you must give the input files')
if args.plots is None:
    raise ValueError('you must specify what kind of plot you want (simple, sphere, anim)')
if not set(args.plots).issubset(set(['simple', 'sphere', 'anim'])):
    raise ValueError('you must choose between: simple, sphere, anim')
# Correct the output argument
if args.output is None:
    output = datetime.date.today().strftime("%Y%m%d")
else:
    output = args.output
# Correct the path argument
if args.path is not None:
    path = args.path + '/' if args.path[-1] != '/' else args.path
else:
    path = ''
# Combine the path with all files
inputs = f'{path}{args.input}' if args.input.split(
    '.')[-1] == 'nc' else f'{path}{args.input}.nc'
if not glob.glob(inputs):
    print(f'I could not find {inputs}')
    print('Exiting...')
    sys.exit()
# Correct the savepath argument
savepath = args.savepath if args.savepath is not None else ''
savepath = path if savepath == 'input' else savepath
savepath = savepath + \
    '/' if savepath != '' and savepath[-1] != '/' else savepath
# Check if output file exist
def file_exist(end):
    if os.path.exists(savepath + output + end):
        ans = str(input(
            f'The file {output}{end} already exist in {savepath[:-1] if savepath != "" else "this directory"}. Do you want to overwrite this? (y/n)\t'))
        if ans != 'y':
            print('Exiting without making any plots...')
            sys.exit()
        else:
            print('Saving to', savepath + output + end)
    else:
        ans = str(input(f'Save to {savepath}{output}{end}? (y/n)\t'))
        if ans != 'y':
            print('Exiting without making any plots...')
            sys.exit()
        else:
            if savepath != '':
                os.makedirs(savepath, exist_ok=True)
            print('Saving to', savepath + output + end)


if 'simple' in args.plots:
    file_exist('_temp.png')
if 'sphere' in args.plots:
    file_exist('_sphere.png')
if 'anim' in args.plots:
    file_exist('.mp4')

# === <CODE> ===
def spherical_plot(time_temp):
    # projections: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
    # PlateCarree(), Orthographic(-80, 35)
    p = time_temp.isel(time=0).plot(
        subplot_kws=dict(projection=ccrs.Mollweide(), facecolor="gray"),
        transform=ccrs.PlateCarree(),)
    p.axes.set_global()
    p.axes.coastlines()
    plt.savefig(f'{savepath}{output}_sphere.png')
    plt.close()


def temperature_animation(time_temp):
    def make_figure():
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # generate a basemap with country borders, oceans and coastlines
        # ax.add_feature(cfeat.LAND)
        # ax.add_feature(cfeat.OCEAN)
        ax.add_feature(cfeat.COASTLINE)
        ax.add_feature(cfeat.BORDERS, linestyle='dotted')
        return fig, ax

    def draw(frame, add_colorbar):
        grid = time_temp[frame]
        contour = grid.plot(ax=ax, transform=ccrs.PlateCarree(),
                            add_colorbar=add_colorbar, vmin=min_value, vmax=max_value)
        # title = u"%s — %s" % (ds.t2m.long_name, str(
        #     time_temp.time[frame].values)[:19])
        # ax.set_title(title)
        return contour

    def init():
        return draw(0, add_colorbar=True)

    def animate(frame):
        return draw(frame, add_colorbar=False)

    fig, ax = make_figure()

    frames = time_temp.time.size        # Number of frames
    min_value = time_temp.values.min()  # Lowest value
    max_value = time_temp.values.max()  # Highest value

    ani = animation.FuncAnimation(fig, animate, frames, interval=0.01, blit=False,
                                  init_func=init, repeat=False)
    ani.save(f'{savepath}{output}.mp4',
             writer=animation.FFMpegWriter(fps=8))
    plt.close(fig)


def just_temp(temps):
    k = temps.mean(dim=['lat', 'lon'])
    k.plot()
    plt.savefig(f'{savepath}{output}_temp.png')
    plt.close()
# === </CODE> ===


multi_T = xr.open_dataarray(inputs, decode_times=False)
multi_T = multi_T.isel(lev=0)
if 'simple' in args.plots:
    just_temp(multi_T)
if 'sphere' in args.plots:
    spherical_plot(multi_T)
if 'anim' in args.plots:
    temperature_animation(multi_T)
