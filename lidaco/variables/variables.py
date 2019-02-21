import jsonschema
import simplejson as json
import datetime

class Variables:
    """
    Database of variables and related metadata
    """
    def __init__(self):
        ## Read the schema file 
        with open('./lidaco/variables/schema.json', 'r') as f:
            schema_file = f.read()
        schema = json.loads(schema_file)

        dictionaries = ["IEC_Met.json","CENER.json"]
        self.dictionary = []

        for file_name in dictionaries:
            ## Read variables definitions
            with open('./lidaco/variables/' + file_name, 'r') as f:
                json_file = f.read()
            variables_json_obj = json.loads(json_file)
            
            # Validate the variables definitions
            jsonschema.validate(variables_json_obj, schema)

            # Add to the global dictionary
            self.dictionary = self.dictionary + variables_json_obj

    def lookup(self, variable_name):
        """
        Finds a variable metadata based on its standardised name
        TODO Need an index for variables names to get results in O(1)
        """
        res = {}
        for obj in self.dictionary:
            if (obj['name']['default'] == variable_name):
                res = obj
                break
        
        if (len(res) == 0):
            print("ERROR: Unrecognised variable name " + variable_name)
            print("If using for the first time, then you should add the metadata of the variable to an appropriate .json file in the lidaco/variables folder")
            print("Exiting")
            exit()     
        return res

    def nc_create(self, output_dataset, name, dimensions, standard_name = ""):
        """
        Creates a variable based on a standardised variable name in an nc object 
        and returns a reference to that variable.
        TODO Choice of naming conventions for variables names
        TODO copy other properties
        """
        if(standard_name == ""):
            standard_name = name

        metadata = self.lookup(name)
        var = output_dataset.createVariable(standard_name, metadata["netcdf"]["var_type"], dimensions)
        var.units = metadata["units"]
        var.long_name = metadata["name"]["default"]
        var.comment = metadata["description"]
        #var.accuracy = metadata["accuracy"]
        #var.accuracy_info = metadata["accuracy_info"]
        return var

