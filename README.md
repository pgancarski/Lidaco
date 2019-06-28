[![PyPI version](https://badge.fury.io/py/lidaco.svg)](https://badge.fury.io/py/lidaco)

# Widaco 

Widaco (**Wi**nd **Da**ta **Co**nverter) is a data converter build on top of the Lidaco library (Wind **Li**dar **Da**ta **Co**nverter) https://github.com/e-WindLidar/Lidaco . 


## Getting started - WORK IN PROGRESS
Download the repository, and try running the ALEX17 example samples/ALEX17_csv_timeseries/run.ipynb
Install any missing dependencies.

## Inputs

#### Input datasets

Widaco is currently designed to process CSV timeseries data compatible with `pandas.read_csv()`


#### Config files

The converter is usually called with a path to a config file in `.yaml` format. As an option, it is also possible to provide parts or the full config object as an argument. This is especially usefull when dealing with files containing many variables (so we can generate the variables setup automatically), or when we want to pass a function to be applied to a specific variable.


## Variables dictionary

Widaco uses a variables dictionary to support different naming convention, provide a comfortable mechanism for defining quality variables metadata, and to support standardisation. Widaco expects every output variable to be defined first in a `.json` file https://github.com/pgancarski/Lidaco/tree/master/lidaco/variables


## Output files structure

The outputs are structured as a 3D arrays of timeseries, "position", and variables.
Position can stand for anything that is defined by its position and type, usally it stands for a wind turbine or a specific altitude of a met mast.
