# cesm-helper-scripts

## Install

Clone with `git clone https://github.com/engeir/cesm-helper-scripts.git`.

Inside a virtual environment, run:

```sh
poetry install
poetry build
```

This give two executable pakages provided the virtual environment is activated:

-   `cplt`: attribute plots using an aggregated `.nc` file as input, i.e. output of the
    `gen_agg` script. See `cplt --help`.
-   `nc2np`: generate an `.npz` file from an aggregated `.nc` file, output of the
    `gen_agg` script. See `nc2np --help`.
