"""Script that generates netCDF files used to test the modules."""

import os
import shutil
from typing import Literal

import netCDF4
import numpy as np


class Dataset:
    def __init__(self) -> None:
        if (
            here := os.path.basename(abs_path := os.path.abspath("."))
        ) == "cesm-helper-scripts":
            self.path = os.path.join("tests", "data")
        elif here == "tests":
            self.path = "data"
        else:
            raise OSError(
                "You are in the wrong path or something. I tried to find ./tests/data,"
                f" but could only find absolute path {abs_path}, and that ends in the"
                f" {here} directory."
            )
        self.clean()
        self.format: Literal[
            "NETCDF3_CLASSIC",
            "NETCDF4",
            "NETCDF4_CLASSIC",
            "NETCDF3_64BIT_OFFSET",
            "NETCDF3_64BIT_DATA",
        ] = "NETCDF3_64BIT_OFFSET"
        self.num_files = 10

    def set_variables(self) -> None:
        self.variables: dict[str, dict] = {
            "T": {
                "dims": ("time", "lev", "lat", "lon"),
                "type": "f4",
                "units": "K",
                "mdims": 1,
                "long_name": "Temperature",
                "cell_methods": "time: mean",
            },
            "TREFHT": {
                "dims": ("time", "lat", "lon"),
                "type": "f4",
                "units": "K",
                "long_name": "Reference height temperature",
                "cell_methods": "time: mean",
            },
            "FLNT": {
                "dims": ("time", "lat", "lon"),
                "type": "f4",
                "Sampling_Sequence": "rad_lwsw",
                "units": "W/m2",
                "long_name": "Net longwave flux at top of model",
                "cell_methods": "time: mean",
            },
            "FSNT": {
                "dims": ("time", "lat", "lon"),
                "type": "f4",
                "Sampling_Sequence": "rad_lwsw",
                "units": "W/m2",
                "long_name": "Net solar flux at top of model",
                "cell_methods": "time: mean",
            },
            "AODVISstdn": {
                "dims": ("time", "lat", "lon"),
                "type": "f4",
                "_FillValue": 1e36,
                # "missing_value": 1e36,
                "long_name": "Stratospheric aerosol optical depth 550 nm, day night",
                "cell_methods": "time: mean",
            },
        }

    def clean(self) -> None:
        """Clean up the data directory for generated data sets."""
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)

    def make_datasets(self) -> None:
        for i in range(self.num_files):
            i_ = "0" * (2 - len(str(i))) + str(i)
            file_name = f"simulation.cam.h0.1852-{i_}.nc"
            self.set_variables()
            self.create_dataset(file_name, i * 30)

    def create_dataset(self, file_name: str, time_stamp: int) -> None:
        ds = netCDF4.Dataset(
            os.path.join(self.path, file_name), mode="w", format=self.format
        )
        ds.description = "Example description"
        ds.creator = (
            "Example creator. Here, we make the line so long that it has to wrap."
            " Notice that the line in this case will start on the next line, as opposed"
            " to the 'description' variable above. Newlines inside the description is"
            " indented with four spaces, while lines that have been wrapped are"
            " indented with eight spaces. This is also printed with a dim colour where"
            " the variable name is. Can you see it?\n It is not so easy to see, but"
            " that is also the point, since it does not really provide any useful"
            " information; you only need to know about it and then it should be"
            " unobtrusive othervise. At this point I dont have anything more to say, I"
            " am just making sure the line is long enough to get some wrapping."
        )
        ds.title = ""
        ds.description = "Example dataset"
        ds.creator = "\n"
        ds.time_period_freq = "month_1"
        ds.createDimension("lat", 96)  # latitude axis
        ds.createDimension("lon", 144)  # longitude axis
        ds.createDimension("lev", 32)  # level axis
        ds.createDimension("ilev", 33)  # interfaces levels
        ds.createDimension("chars", 8)  # KeyError: No variable information
        ds.createDimension("nbnd", 2)  # KeyError: No variable information
        ds.createDimension("time")  # unlimited axis (can be appended to).
        lat = ds.createVariable("lat", "f8", ("lat",), fill_value=-900)
        lat.units = "degrees_north"
        lat.long_name = "latitude"
        lon = ds.createVariable("lon", float, ("lon",), fill_value=-900)
        lon.units = "degrees_east"
        lon.long_name = "longitude"
        lev = ds.createVariable("lev", float, ("lev",))
        lev.units = "hPa"
        lev.positive = "down"
        lev.long_name = "hybrid level at midpoints (1000*(A+B))"
        lev.standard_name = "atmosphere_hybrid_sigma_pressure_coordinate"
        lev.formula_terms = "a: hyam b: hybm p0: P0 ps: PS"
        ilev = ds.createVariable("ilev", float, ("ilev",))
        ilev.units = "hPa"
        ilev.positive = "down"
        ilev.long_name = "hybrid level at interfaces (1000*(A+B))"
        ilev.standard_name = "atmosphere_hybrid_sigma_pressure_coordinate"
        ilev.formula_terms = "a: hyai b: hybi p0: P0 ps: PS"
        time = ds.createVariable("time", float, ("time",))
        time.units = "days since 1850-01-01 00:00:00"
        time.long_name = "time"
        time.calendar = "noleap"
        time.bounds = "time_bnds"

        nlats = ds.dimensions["lat"].size
        nlons = ds.dimensions["lon"].size
        nlevs = ds.dimensions["lev"].size
        # Populate variables with data
        ds.variables["lat"]
        ds.variables["lon"]
        time_ = ds.variables["time"]
        time_[:] = time_stamp  # Days since 1850
        lat[:] = -90.0 + (180.0 / nlats) * np.arange(nlats)
        lon[:] = (180.0 / nlats) * np.arange(nlons)  # Greenwich meridian eastward
        for var_name, var_dict in self.variables.items():
            if "_FillValue" in var_dict:
                dims_length = len(dims_ := var_dict.pop("dims"))
                var = ds.createVariable(
                    var_name,
                    var_dict.pop("type"),
                    dims_,
                    fill_value=var_dict.pop("_FillValue"),
                )
            else:
                dims_length = len(dims_ := var_dict.pop("dims"))
                var = ds.createVariable(var_name, var_dict.pop("type"), dims_)
            for meta in var_dict.items():
                setattr(var, meta[0], meta[1])
            data_slice = np.random.uniform(low=280, high=330, size=(nlats, nlons))
            data_slice = data_slice[np.newaxis, :]
            if dims_length == 3:
                var[:, :, :] = np.asarray(data_slice) * (
                    np.random.randint(0, 2) * 2 - 1
                )
            elif dims_length == 4:
                for levs in range(nlevs):
                    var[:, levs, :, :] = np.asarray(data_slice) * levs


def main():
    creator = Dataset()
    creator.make_datasets()


if __name__ == "__main__":
    main()
