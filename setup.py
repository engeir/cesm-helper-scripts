# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = {"": "src"}

packages = ["cesm_helper_scripts", "cesm_helper_scripts.rewrite_variable"]

package_data = {"": ["*"]}

install_requires = [
    "Cartopy>=0.20.2,<0.21.0",
    "animatplot>=0.4.2,<0.5.0",
    "cftime>=1.5.0,<2.0.0",
    "cosmoplots>=0.1.5,<0.2.0",
    "dask>=2021.4.0,<2022.0.0",
    "matplotlib>=3.4.1,<4.0.0",
    "nc-time-axis>=1.2.0,<2.0.0",
    "netCDF4>=1.5.6,<2.0.0",
    "numpy>=1.20.2,<2.0.0",
    "pykdtree>=1.3.4,<2.0.0",
    "rich>=10.1.0,<11.0.0",
    "scipy>=1.7.1,<2.0.0",
    "xarray>=0.19.0,<0.20.0",
]

entry_points = {
    "console_scripts": [
        "cplt = cesm_helper_scripts.create_plots:main",
        "nc2np = cesm_helper_scripts.nc_to_np:main",
    ]
}

setup_kwargs = {
    "name": "cesm-helper-scripts",
    "version": "0.2.1",
    "description": "",
    "long_description": None,
    "author": "engeir",
    "author_email": "eirroleng@gmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": None,
    "package_dir": package_dir,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.8,<3.11",
}


setup(**setup_kwargs)
