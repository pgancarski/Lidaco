from ..core.Reader import Reader
import datetime
import numpy as np
import pandas as pd
from lidaco.variables import variables

class CSV_timeseries(Reader):

    def __init__(self):
        super().__init__(False)
        
    def init(self,output_dataset, input_filepath, parameters, appending):
        self._output_dataset = output_dataset
        self._input_filepath = input_filepath
        self._parameters = parameters
        
        self._var_dict = variables.Variables()
        self._time_sort_map = None
        
    def accepts_file(self, filename):
        return filename.endswith('.csv') or filename.endswith('.txt') 

    def output_filename(self, filename):
        return filename.split(".")[0]
    
    def roedsand_time_series(self, name_from, apply_options):
        time_data = np.array(self.wind_file_data.apply(
                    lambda x: self.create_time(x['Name'], x['scan_id']), 
                    axis=1))
        # If time dimension is not sorted, make sure to create sorting map
        self._time_sort_map = time_data.argsort()
        
        return time_data
        
    def celsius_to_kelvin(self, name_from, apply_options):
        return np.array(self.wind_file_data.apply(
                    lambda x: x[name_from] + 273.15, 
                    axis=1))
                    
    def create_time(self, Name, scan_id):
        year    = int(str(Name)[0:4])
        month   = int(str(Name)[4:6])
        day     = int(str(Name)[6:8])
        hours   = int(str(Name)[8:10])
        minutes = int(str(Name)[10:12]) 
        dt = datetime.datetime(year, month, day, hours, minutes)
        
        seconds_since = (dt - datetime.datetime(1970,1,1)).total_seconds()

        return seconds_since + 0.05 * scan_id ## + 23.20 Why the offset here?
        
    def get_parameter(self, par_name, default = None):
        if(default == None):
            # Be strict with the parameters that has to be defined
            if(par_name == 'variables'): 
                return self._parameters['parameters'][par_name]
            # define defaults of other parameters
            if(par_name == 'delimeter'): default = ','
            if(par_name == 'header'   ): default = '0'
            if(par_name == 'skip_rows'): default = '0'
        return self._parameters['parameters'].get(par_name,default)
        
    def get_var_parameter(self, var_id, par_name, default = None):
        if(default == None): 
            # Be strict with the parameters that has to be defined
            if(par_name == 'name_to' or par_name == 'name_from'): 
                return self._parameters['parameters']['variables'][var_id][par_name]
            # define defaults of other parameters
            
        return self._parameters['parameters']['variables'][var_id].get(par_name,default)  
             
    def read_wind_file_data(self):
        self.wind_file_data = pd.read_csv(self._input_filepath, 
                delimiter = self.get_parameter('delimeter'),
                header = self.get_parameter('header'),
                skiprows = self.get_parameter('skip_rows')
                )
             
    def create_time_dimension(self):
        # get to and from names
        name_from = self.get_var_parameter(0, 'name_from')
        name_to = self.get_var_parameter(0, 'name_to')
        # create dimension
        self._output_dataset.createDimension(name_to, len(self.wind_file_data))   # dimension name and length 
        # store the dimension name for future reference
        self.main_dimension = name_to
        
    def create_variable(self, var_id):
        # precompute the variable
        var_data = self.get_variable_data(var_id)
        # create the variable
        var = self._var_dict.nc_create(
                    self._output_dataset, 
                    self.get_var_parameter(var_id, 'name_to'), 
                    (self.main_dimension,))
        # assign the values
        var[:] = var_data
        return var
    def get_variable_data(self, var_id):
        
        name_from = self.get_var_parameter(var_id,'name_from')
        
        # is there a funtion to apply to the data?
        f_name = self.get_var_parameter(var_id,'apply')
        if(f_name != None):
            # fetch the funtion to apply to the data
            f = getattr(self, f_name)
            apply_options = self.get_var_parameter(var_id,'apply_options')
            
            # pass the data through the funtion
            res = f(name_from,apply_options)
        else:
            # simply pass the data from the specified column
            res = np.array(self.wind_file_data[name_from])
                    
        # if necessarry, sort the results by time dimension
        if self._time_sort_map is not None:
            res = res[self._time_sort_map]            

        return res


    def add_global_attributes(self):
         ### add global attributes which are not directly copied from the .yaml setup file
         # add start and end time
        time1970 = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        start_timestamp = self._output_dataset.variables['time'][0].__float__()
        end_timestamp   = self._output_dataset.variables['time'][-1].__float__()
        
        start_time = time1970 + datetime.timedelta(seconds=start_timestamp)
        end_time   = time1970 + datetime.timedelta(seconds=end_timestamp)
        
        setattr(self._output_dataset, 'start_time', start_time.strftime('%Y-%m-%d %H:%M:%S')) 
        setattr(self._output_dataset, 'end_time',   end_time.strftime('%Y-%m-%d %H:%M:%S')) 
        
    def read_to(self, output_dataset, input_filepath, parameters, appending): 
        
        self.init(output_dataset, input_filepath, parameters, appending)
        
        ### read the input data file
        self.read_wind_file_data()
        
        ### create time dimension
        self.create_time_dimension()

        ### iterate through and create variables
        for var_id in range(len(self.get_parameter('variables'))):
            self.create_variable(var_id)

        ### add global attributes which are not directly copied from the .yaml setup file
        self.add_global_attributes()
