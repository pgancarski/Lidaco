[![PyPI version](https://badge.fury.io/py/lidaco.svg)](https://badge.fury.io/py/lidaco)

# Lidaco 

Lidaco (Wind **Li**dar **Da**ta **Co**nverter) is a library and executable that enables a modular writing of data converters. 

Following the configurations that are specified by the user on a config.yml(s), a Reader module is selected to import the data from input files.
Similarly, a Writer is also selected to write the output file(s).

  
Lidaco works on datasets that can be described using the unidata [Common Data Model](https://www.unidata.ucar.edu/software/thredds/current/netcdf-java/CDM/). It can be used to process single files or entire folders. 


##### Available Readers
    * AQ500
    * Galion
    * WLS70
    * Windcubev1
    * Windcubev2
    * Windscanner
    * ZephIR300
    * Triton
    
##### Available Writers
    * MetadataCard
    * NcML
    * NetCDF4


## Getting started

##### Install
```bash
pip install lidaco
```

##### Run
```bash
lidaco --config-file=samples/Windscanner/config.yaml
```

##### In code
```python
from lidaco.core.Builder import Builder

builder = Builder(config_file = 'path/to/config.yaml')
builder.build()
```

## Converting data

####



#### Writing conversion files

Each conversion requires a configuration file written in [YAML](http://yaml.org/). This file contains four (optional) main groups of configurations:
###### Parameters

This section allows you to specify the parameters for the converter itself, the selected reader and or writer.
The converter parameters are: 
```yaml
parameters:
  input: 
    path: ./path/to/input/folder/
    format: Windscanner
  output: 
    format: NetCDF4 
```

To know each specific reader/writer parameter read the respective documentation available, or try to take a look at its source code.
 
###### Attributes
This section specify the global attributes that will be added to the dataset. You can add all attributes you desire. 
```yaml
attributes:
  # e.g.,
  lidar_technology: 'pulsed'
  lidar_scanning_type: 'vertical profiling'
  data_processing_history: 'data taken from .scn files generated by ...'
```
###### Variables

This section is similar to *Attributes* but instead of reading being used to specify Attributes, it is used to specify variables.
```yaml
variables:   
  # e.g.,
  pitch:
    data_type: 'f4'
    units: 'degrees'
    long_name: 'lidar_pitch_angle'
    comment: ''
    accuracy: ''
    accuracy_info: 'No information on pitch accuracy available.'
    value: 0
```


###### Imports
Lidaco configuration system is built to motivate the configurations reusability, so each config file can import others. With this mechanism you can to split your configurations into devices, scenarios, campaigns and so on.
In case of multiple definitions of an attribute or variable, the definitions in the file prevail over the others that are imported.

```yaml
imports: # read in order
  - ./general/NEWA_Kassel_general_dataset.yaml
  - ./instruments/Windcubev2_general_instrument_description.yaml
  - ./processing/NEWA_Kassel_data_processing_history.yaml
```


For more examples on how to setup your config files, take a look at the available
[Samples](https://github.com/e-WindLidar/Lidaco/tree/master/samples).


--------------


### Contributing
If you would like to add, or see being added, some change to the converter you can:

 * [Open an issue](https://github.com/e-WindLidar/Lidaco/issues) so that it is discussed by everyone.
 * And/or also [Submit a pull request](https://github.com/e-WindLidar/Lidaco/pulls) with the desired changes. ([About pull requests](https://help.github.com/articles/about-pull-requests/))

##### To submit a new Reader/Writer
 * Create a python class at lidaco.readers or lidaco.writers, if you are writing a reader or writer respectively.
 * The file and class should have the same name, that will be used in the config files. 
 * It should extend core.reader or core.writer.
 
 Take a look at the existing [readers](https://github.com/e-WindLidar/Lidaco/blob/master/lidaco/readers/) and [writers](https://github.com/e-WindLidar/Lidaco/blob/master/lidaco/writers/). 
