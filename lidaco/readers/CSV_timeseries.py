from ..core.Reader import Reader
import datetime
import numpy as np
import pandas as pd
from lidaco.variables import variables

class CSV_timeseries(Reader):

    ############################################ Reader class implementation
    def __init__(self):
        super().__init__(False)
        
    def accepts_file(self, filename):
        return filename.endswith('.csv') or filename.endswith('.txt') 

    def output_filename(self, filename):
        return filename.split(".")[0]
    
    
    
    ############################################ helper functions
    
    def init(self,output_dataset, input_filepath, parameters, appending):
        self._output_dataset = output_dataset
        self._input_filepath = input_filepath
        self._parameters = parameters
        
        self._var_dict = variables.Variables()
        self._time_sort_map = None
    
#    def roedsand_time_series(self, name_from, apply_options):
#        time_data = np.array(self.wind_file_data.apply(
#                    lambda x: self.create_time(x['Name'], x['scan_id']), 
#                    axis=1))
#        # If time dimension is not sorted, make sure to create sorting map
#        self._time_sort_map = time_data.argsort()
#        
#        return time_data
    
    
    #    def create_time(self, Name, scan_id):
#        year    = int(str(Name)[0:4])
#        month   = int(str(Name)[4:6])
#        day     = int(str(Name)[6:8])
#        hours   = int(str(Name)[8:10])
#        minutes = int(str(Name)[10:12]) 
#        dt = datetime.datetime(year, month, day, hours, minutes)
#        
#        seconds_since = (dt - datetime.datetime(1970,1,1)).total_seconds()
#
#        return seconds_since + 0.05 * scan_id ## + 23.20 Why the offset here?
        
    def celsius_to_kelvin(self, name_from, apply_options):
        return np.array(self.wind_file_data.apply(
                    lambda x: x[name_from] + 273.15, 
                    axis=1))
                              
    def read_wind_file_data(self):
        self.wind_file_data = pd.read_csv(self._input_filepath, 
                delimiter = self.get_parameter('delimeter'),
                header = self.get_parameter('header'),
                skiprows = self.get_parameter('skip_rows')
                )  
        
#######################################################################  GET
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
    def get_variable_data(self, var_name):
        res = np.empty((self.n_sensors,self.n_time))
        res[:] = np.nan
        for i_sensor in range(self.n_sensors):
            sensor_data = self._parameters['parameters']['sensors'][i_sensor]
            
            for variable in sensor_data['variables']:
                if variable['name_to'] == var_name:
                    name_from = variable['name_from']
                    res[i_sensor] = np.array(self.wind_file_data[name_from])

### TODO add apply option         
#        # is there a funtion to apply to the data?
#        f_name = self.get_var_parameter(var_id,'apply')
#        if(f_name != None):
#            # fetch the funtion to apply to the data
#            f = getattr(self, f_name)
#            apply_options = self.get_var_parameter(var_id,'apply_options')
#            
#            # pass the data through the funtion
#            res = f(name_from,apply_options)
#        else:
#            # simply pass the data from the specified column
#            res = np.array(self.wind_file_data[name_from])
#                    
        # if necessarry, sort the results by time dimension
        if self._time_sort_map is not None:
            for i_sensor in range(self.n_sensors):
                res[i_sensor] = res[i_sensor][self._time_sort_map]            

        return res
    def get_variables_list(self):
        variables = set()
        for sensor_data in self._parameters['parameters']['sensors']:
            for variable in sensor_data['variables']:
                variables.add(variable['name_to'])
        return variables
        
#################################################################### CREATE

        
   
    def create_time(self):
        # get to and from names
        name_from = self._parameters['parameters']['time_from']
        name_to = 'time'
        
        # is there a funtion to apply to the data?
        f = self._parameters['parameters']['time_apply']
        if(f != None):

            # pass the data through the funtion
            time_data = np.array(self.wind_file_data.apply(
                    lambda x: f(x), 
                    axis=1))    
        else:
            # simply pass the data from the specified column
            time_data = np.array(self.wind_file_data[name_from])
        
        # create dimension
        self.n_time = len(time_data)
        self._output_dataset.createDimension(name_to, self.n_time)   # dimension name and length 
        
        # create the variable
        var = self._var_dict.nc_create(
                    self._output_dataset, 
                    'time', 
                    ('time',))
        
        # If time dimension is not sorted, make sure to create sorting map
        self._time_sort_map = time_data.argsort()
        
        # assign the values
        var[:] = time_data

        
    def create_sensor_variable(self,name_to):
        name_from = name_to
        var = self._var_dict.nc_create(self._output_dataset,name_to,('sensor',))
        for i in range(len(self._parameters['parameters']['sensors'])):
            ### TODO add apply option  
            var[i] = self._parameters['parameters']['sensors'][i][name_from]

    def create_sensors(self):
        # create dimension
        self.n_sensors = len(self._parameters['parameters']['sensors'])
        self._output_dataset.createDimension('sensor',self.n_sensors)
        
        ### create variables
        self.create_sensor_variable('id')
        self.create_sensor_variable('type')
        self.create_sensor_variable('long_name')
        self.create_sensor_variable('latitude')
        self.create_sensor_variable('longitude')
        self.create_sensor_variable('altitude')
    
    def create_variable(self, variable_name):
        # precompute the variable
        var_data = self.get_variable_data(variable_name)
        # create the variable
        var = self._var_dict.nc_create(
                    self._output_dataset, 
                    variable_name,
                    ('sensor','time'))
        # assign the values
        var[:] = var_data
        return var
    
    def create_timeseries(self):
        varialbles = self.get_variables_list()
        for variable_name in varialbles:
            self.create_variable(variable_name)     

    def create_global_attributes(self):
         ### add global attributes which are not directly copied from the .yaml setup file
         # add start and end time
        time1970 = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        start_timestamp = self._output_dataset.variables['time'][0].__float__()
        end_timestamp   = self._output_dataset.variables['time'][-1].__float__()
        
        start_time = time1970 + datetime.timedelta(seconds=start_timestamp)
        end_time   = time1970 + datetime.timedelta(seconds=end_timestamp)
        
        setattr(self._output_dataset, 'start_time', start_time.strftime('%Y-%m-%d %H:%M:%S')) 
        setattr(self._output_dataset, 'end_time',   end_time.strftime('%Y-%m-%d %H:%M:%S')) 
        

        
################################################################################## MAIN   
    def read_to(self, output_dataset, input_filepath, parameters, appending): 
        """ 
        
        
        
        The main function for processing the data
        
        
        
        """
        
        self.init(output_dataset, input_filepath, parameters, appending)
        
        ### read the input data file
        self.read_wind_file_data()
        
        ### create time dimension
        self.create_time()
        ### create sensor dimension and metadata
        self.create_sensors()
        
        ### create timeseries data
        self.create_timeseries()

        ### add global attributes which are not directly copied from the .yaml setup file
        ### all the attributes from setting files are copied later on 
        self.create_global_attributes()
