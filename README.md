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

This give two executable packages provided the virtual environment is activated:

-   `cplt`: attribute plots using an aggregated `.nc` file as input, i.e. output of the
    `gen_agg` script. See `cplt --help`.
-   `nc2np`: generate an `.npz` file from an aggregated `.nc` file, output of the
    `gen_agg` script. See `nc2np --help`.
