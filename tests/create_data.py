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
        ds.time_period_freq = "month_1"
        ds.createDimension("lat", 96)  # latitude axis
        ds.createDimension("lon", 144)  # longitude axis
        ds.createDimension("lev", 70)  # level axis
        ds.createDimension("ilev", 71)  # interfaces levels
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
        # nilevs = ds.dimensions["ilev"].size
        # Populate variables with data
        ds.variables["lat"]
        ds.variables["lon"]
        time_ = ds.variables["time"]
        time_[:] = time_stamp  # Days since 1850
        lat[:] = -90.0 + (180.0 / nlats) * np.arange(nlats)
        lon[:] = (180.0 / nlats) * np.arange(nlons)  # Greenwich meridian eastward
        # lev[:] = np.arange(nlevs)  # From 5.96e-06 to 992.6 hPa
        # ilev[:] = np.arange(nilevs)  # From  4.5e-06 to 1000 hPa
        # fmt: off
        ilev[:] = [
            4.500500e-06, 7.420100e-06, 1.223370e-05, 2.017000e-05, 3.325450e-05,
            5.482750e-05, 9.039800e-05, 1.490400e-04, 2.457200e-04, 4.051250e-04,
            6.679400e-04, 1.101265e-03, 1.815650e-03, 2.993500e-03, 4.963000e-03,
            8.150651e-03, 1.347700e-02, 2.231900e-02, 3.679650e-02, 6.066500e-02,
            9.915650e-02, 1.573900e-01, 2.388500e-01, 3.452000e-01, 4.751350e-01,
            6.318050e-01, 8.291550e-01, 1.082740e+00, 1.406850e+00, 1.818850e+00,
            2.339800e+00, 2.995050e+00, 3.814700e+00, 4.834450e+00, 6.096350e+00,
            7.649350e+00, 9.550100e+00, 1.186400e+01, 1.466550e+01, 1.803800e+01,
            2.207550e+01, 2.688250e+01, 3.257350e+01, 3.927300e+01, 4.711450e+01,
            5.624050e+01, 6.680050e+01, 8.070142e+01, 9.494104e+01, 1.116932e+02,
            1.314013e+02, 1.545868e+02, 1.818634e+02, 2.139528e+02, 2.517044e+02,
            2.961172e+02, 3.483666e+02, 4.098352e+02, 4.821499e+02, 5.672244e+02,
            6.523330e+02, 7.304459e+02, 7.963631e+02, 8.453537e+02, 8.737159e+02,
            9.003246e+02, 9.249645e+02, 9.474323e+02, 9.675386e+02, 9.851122e+02,
            1.000000e+03,
        ]
        lev[:] = [
            5.960300e-06, 9.826900e-06, 1.620185e-05, 2.671225e-05, 4.404100e-05,
            7.261275e-05, 1.197190e-04, 1.973800e-04, 3.254225e-04, 5.365325e-04,
            8.846025e-04, 1.458457e-03, 2.404575e-03, 3.978250e-03, 6.556826e-03,
            1.081383e-02, 1.789800e-02, 2.955775e-02, 4.873075e-02, 7.991075e-02,
            1.282732e-01, 1.981200e-01, 2.920250e-01, 4.101675e-01, 5.534700e-01,
            7.304800e-01, 9.559475e-01, 1.244795e+00, 1.612850e+00, 2.079325e+00,
            2.667425e+00, 3.404875e+00, 4.324575e+00, 5.465400e+00, 6.872850e+00,
            8.599725e+00, 1.070705e+01, 1.326475e+01, 1.635175e+01, 2.005675e+01,
            2.447900e+01, 2.972800e+01, 3.592325e+01, 4.319375e+01, 5.167750e+01,
            6.152050e+01, 7.375096e+01, 8.782123e+01, 1.033171e+02, 1.215472e+02,
            1.429940e+02, 1.682251e+02, 1.979081e+02, 2.328286e+02, 2.739108e+02,
            3.222419e+02, 3.791009e+02, 4.459926e+02, 5.246872e+02, 6.097787e+02,
            6.913894e+02, 7.634045e+02, 8.208584e+02, 8.595348e+02, 8.870202e+02,
            9.126445e+02, 9.361984e+02, 9.574855e+02, 9.763254e+02, 9.925561e+02
        ]
        # fmt: on
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
