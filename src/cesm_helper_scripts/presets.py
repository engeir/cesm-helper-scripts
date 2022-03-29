import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from xmovie.presets import (
    _add_coast,
    _add_land,
    _base_plot,
    _check_input,
    _set_style,
    _style_dict_raw,
)


def static_globe(
    da,
    fig,
    timestamp,
    framedim="time",
    plotmethod=None,
    plot_variable=None,
    overlay_variables=None,
    lon_start=-110,
    lon_rotations=0.5,
    lat_start=25,
    lat_rotations=0,
    land=False,
    gridlines=False,
    coastline=True,
    style=None,
    debug=False,
    **kwargs
):
    """
    Rotating globe plot.

    Parameters
    ----------
    da : DataArray
        Data to be plotted.
    fig : Figure
        Figure to plot on.
    timestamp : int
        Used to select the animation frame using :meth:`~xarray.DataArray.isel`
        with dimension `framedim`.
    framedim : str
        Dimension name along which frames will be generated.
    plotmethod : str, optional
        Method of :attr:`xarray.DataArray.plot` to use.
    plot_variable : str, optional
        Variable to plot. Not needed for :class:`~xarray.DataArray`.
    overlay_variables
        Currently unused.
    lon_start : float
        Central longitude at the beginning of the animation.
    lon_rotations : float
        Number of longitude rotations to be completed in the animation.
    lat_start : float
        As in `lon_start`.
    lat_rotations : float
        As in `lon_rotations`.
    land : bool
        Plot the land.
    gridlines : bool
        Plot lat/lon gridlines.
    coastline : bool
        Plot the coastlines.
    style : {'standard', 'dark'}
    debug : bool
        Currently unused.
    **kwargs
        Passed on to the xarray plotting method.

    Returns
    -------
    ax: Axes
        Axes object.
    pp: matplotlib.collections.PatchCollection
        Patches for the land and coastlines.
    """

    proj = ccrs.Robinson()
    subplot_kw = dict(projection=proj)

    map_style_kwargs = dict(transform=ccrs.PlateCarree())
    kwargs.update(map_style_kwargs)

    ax = fig.subplots(subplot_kw=subplot_kw)
    data = _check_input(da, plot_variable)
    pp = _base_plot(ax, data, timestamp, framedim, plotmethod=plotmethod, **kwargs)

    _set_style(fig, ax, pp, style=style)

    clr = _style_dict_raw()[style]["fgcolor"]
    ax.set_title("time = %s" % data.isel(time=timestamp).time.data, color=clr)
    ax.set_global()

    if land:
        _add_land(ax, style)

    if coastline:
        _add_coast(ax, style)

    if gridlines:
        gl = ax.gridlines()
        # Increase gridline res
        gl.n_steps = 500
        # for now fixed locations
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 30))
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 30))
    else:
        gl = None

    return ax, pp
