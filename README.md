# cesm-helper-scripts

<!-- [![codecov](https://codecov.io/gh/engeir/volcano-cooking/branch/main/graph/badge.svg?token=8I5VE7LYA4)](https://codecov.io/gh/engeir/volcano-cooking) -->
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Install

Clone with `git clone https://github.com/engeir/cesm-helper-scripts.git`.

Inside a virtual environment, run:

```sh
poetry install
```

This give two entry points / executable packages provided the virtual environment is
activated:

- `cplt`: attribute plots using an aggregated `.nc` file as input, i.e. output of the
  `gen_agg` script. See `cplt --help`.
- `nc2np`: generate an `.npz` file from an aggregated `.nc` file, output of the
  `gen_agg` script. See `nc2np --help`.

The version that uses the `cartopy` module to create maps with geographical geometry must
be installed as a `conda` environment:

```sh
# Install env with name conda-cesm ...
conda create --file environment.yaml
# ... or give the env a custom name.
conda create --file environment.yaml --name custom-name
```

The entry points will not work with the `conda` installation, and the full path need to be
used instead. [This][conda-stackoverflow] thread explains how it is not possible to
install modules from conda-forge when creating a conda project. Weird.

## Usage

<details><summary><code>gen_agg</code></summary><br>

Say you are in the location of your output files for the atmosphere module. It will list
files with name `<simulation_name>.cam.h0.YYYY.MM.nc` for the month resolution. Check out
what variables it contains by running

```sh
ncdump -c <file.nc> | sed 5000q | grep -i <search-string>
```

For example, we may search for `forcing`:

```console
$ ncdump -c e_slab_custom_frc.cam.h0.0001-01.nc | sed 5000q | grep -i forcing
                H2O_CLXF:long_name = "vertically intergrated external forcing for H2O" ;
                H2O_CMXF:long_name = "vertically intergrated external forcing for H2O" ;
                LWCF:long_name = "Longwave cloud forcing" ;
                SO2_CLXF:long_name = "vertically intergrated external forcing for SO2" ;
                SO2_CMXF:long_name = "vertically intergrated external forcing for SO2" ;
                SWCF:long_name = "Shortwave cloud forcing" ;
                bc_a4_CLXF:long_name = "vertically intergrated external forcing for bc_a4" ;
                bc_a4_CMXF:long_name = "vertically intergrated external forcing for bc_a4" ;
                num_a1_CLXF:long_name = "vertically intergrated external forcing for num_a1" ;
                num_a1_CMXF:long_name = "vertically intergrated external forcing for num_a1" ;
                num_a2_CLXF:long_name = "vertically intergrated external forcing for num_a2" ;
                num_a2_CMXF:long_name = "vertically intergrated external forcing for num_a2" ;
                num_a4_CLXF:long_name = "vertically intergrated external forcing for num_a4" ;
                num_a4_CMXF:long_name = "vertically intergrated external forcing for num_a4" ;
                pom_a4_CLXF:long_name = "vertically intergrated external forcing for pom_a4" ;
                pom_a4_CMXF:long_name = "vertically intergrated external forcing for pom_a4" ;
                so4_a1_CLXF:long_name = "vertically intergrated external forcing for so4_a1" ;
                so4_a1_CMXF:long_name = "vertically intergrated external forcing for so4_a1" ;
                so4_a2_CLXF:long_name = "vertically intergrated external forcing for so4_a2" ;
                so4_a2_CMXF:long_name = "vertically intergrated external forcing for so4_a2" ;
```

and we see that the variable `LWCF` includes information about forcing, specifically the
long wave radiation. So, lets generate a new file for all months with just that one
variable, i.e., we grab `LWCF` from all files

```console
$ ls -1 | sort
e_slab_custom_frc.cam.h0.0001-01.nc
e_slab_custom_frc.cam.h0.0001-02.nc
e_slab_custom_frc.cam.h0.0001-03.nc
e_slab_custom_frc.cam.h0.0001-04.nc
e_slab_custom_frc.cam.h0.0001-05.nc
e_slab_custom_frc.cam.h0.0001-06.nc
...
```

To accomplish this we first create an interactive bigmem job:

```sh
srun --nodes=1 --time=00:10:00 --partition=bigmem --mem=10G --account=nn9817k --pty bash -i
```

The needed allocated time and memory will depend on the number of files used. Load all
needed modules and activate the virtual environment:

```sh
module load Python/3.8.2-GCCcore-9.3.0;
module load matplotlib/3.2.1-intel-2020a-Python-3.8.2;
module load GEOS/3.8.1-iccifort-2020.1.217-Python-3.8.2;
module load PROJ/7.0.0-GCCcore-9.3.0;
module load FFmpeg/4.2.2-GCCcore-9.3.0;
source ~/.virtualenvs/p3/bin/activate
```

We then run

```sh
gen_agg -i "e_slab_custom_frc.cam.h0.000*" -a LWCF SWCF
```

if we want two files; one for the variable `LWCF` and one for `SWCF`. We probably want the
reference height temperature `TREFHT` as well, and maybe also the total aerosol optical
depth in the visible band `AEROD_v`, in which case we run

```sh
gen_agg -i "e_slab_custom_frc.cam.h0.000*" -a LWCF SWCF TREFHT AEROD_v
```

(See the full list of attributes [here](https://www.cesm.ucar.edu/models/cesm2/atmosphere/docs/ug6/hist_flds_f2000.html).)

</details>

<details><summary>Mimic <code>cycle</code> with <code>interp_missing_month</code></summary><br>

This is not really part of the project, but kept here just for convenience.

A file that in the CESM2 model is used in cycle mode on the year 1850 can be made into
produce the same input to CESM2, but in "interp_missing_month" mode.

Assuming you are in the directry of `c2imp.sh` and `set_date_var_nc.py`, and the file you
want to change is `in.nc`, do

```sh
sh c2imp.sh in.nc
```

You probably also have to run the `ncks` command as specified in `c2imp.sh`.

</details>

[conda-stackoverflow]: https://stackoverflow.com/questions/63182614/python-packaging-creating-a-dependency-on-a-conda-forge-package-in-conda-m
