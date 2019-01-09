from ..core.Reader import Reader
import datetime
import numpy as np
import pandas as pd
from lidaco.variables import variables

class Roedsand2(Reader):

    def __init__(self):
        super().__init__(False)

    def accepts_file(self, filename):
        return filename.startswith('Roedsand2_')

    def output_filename(self, filename):
        return filename[10:18]
    
    def create_time(self, Name, scan_id):
        year    = int(str(Name)[0:4])
        month   = int(str(Name)[4:6])
        day     = int(str(Name)[6:8])
        hours   = int(str(Name)[8:10])
        minutes = int(str(Name)[10:12]) 
        dt = datetime.datetime(year, month, day, hours, minutes)
        
        seconds_since = (dt - datetime.datetime(1970,1,1)).total_seconds()

        return seconds_since + 0.05 * scan_id + 23.20
    
    def read_to(self, output_dataset, input_filepath, parameters, appending): 
        """ 
        TODO lat lon should come from setting file. Altitude probably as well...
        """

        wind_file_data = pd.read_csv(input_filepath, sep=';')
        var_dict = variables.Variables()
        
        ### create the dimensions - 'time','altitude','latitude','longitude'
        output_dataset.createDimension('time', len(wind_file_data))   # dimension name and length 
        output_dataset.createDimension('altitude', 2)
        output_dataset.createDimension('latitude', 1)
        output_dataset.createDimension('longitude', 1)


        ### create variables
        #time
        time = var_dict.nc_create(output_dataset, 'time', ('time',))
        time[:] = np.array(wind_file_data.apply(
                    lambda x: self.create_time(x['Name'], x['scan_id']), 
                    axis=1))

        #height, altitude
        altitude = var_dict.nc_create(output_dataset, 'altitude', ('altitude',))
        altitude[:] = np.array([40, 57])

        #lat
        lat = var_dict.nc_create(output_dataset, 'latitude', ('latitude',))
        lat[:] = np.array([54.555]) 

        #lon
        lon = var_dict.nc_create(output_dataset, 'longitude', ('longitude',))
        lon[:] = np.array([11.549]) 


        #air_temperature
        t = var_dict.nc_create(output_dataset, 'air_temperature', ('time','altitude','latitude','longitude'))
        t[:,0,0,0] = np.array(wind_file_data['Ts_40'])
        t[:,1,0,0] = np.array(wind_file_data['Ts_57'])

        # x, 
        xs = var_dict.nc_create(output_dataset, 'eastward_wind', ('time','altitude','latitude','longitude'))
        xs[:,0,0,0] = np.array(wind_file_data['Ux_40'])
        xs[:,1,0,0] = np.array(wind_file_data['Ux_57'])

        # y
        ys = var_dict.nc_create(output_dataset, 'northward_wind', ('time','altitude','latitude','longitude'))
        ys[:,0,0,0] = np.array(wind_file_data['Uy_40'])
        ys[:,1,0,0] = np.array(wind_file_data['Uy_57'])

        # z, upward_air_velocity
        zs = var_dict.nc_create(output_dataset, 'upward_air_velocity', ('time','altitude','latitude','longitude'))
        zs[:,0,0,0] = np.array(wind_file_data['Uz_40'])
        zs[:,1,0,0] = np.array(wind_file_data['Uz_57'])
