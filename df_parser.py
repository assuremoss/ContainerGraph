from pprint import pprint
from dockerfile_parse import DockerfileParser
import json

# Reference
# dockerfile-parse: https://github.com/containerbuildsystem/dockerfile-parse
# Python library for parsing Dockerfile files. 


class Dockerfile :

    def __init__(self, uri):
        self.uri = uri
        self.dfp = DockerfileParser(uri)

    # Get instruction arguments
    def get_df_instruction(self, instruction) :
        ist_list = []
        obj = json.loads(self.dfp.json)
        
        for field in obj : 
            key, value = list(field.items())[0]
            if key == instruction : 
                ist_list.append(value)

        if not ist_list : 
            ist_list = ["n/a"]

        return ist_list

    def print_df_instruction(self, instruction) :
        """ 
        Description

        Parameters
        ---------
        name: type
            Description

        Returns
        -------
        type:
            Description
        """
        obj = json.loads(self.dfp.json)
        
        for field in obj : 
            key, value = list(field.items())[0]
            if key == instruction : 
                print(json.dumps(field, indent=1))

    # Print (original) Dockerfile
    def print_df(self) :
        print(self.dfp.content)
    
    # Print the Dockerfile uri
    def print_df_uri(self) :
        print(self.uri)

    # Print the parsed structure
    def print_df_structure(self) :
        pprint(self.dfp.structure)

    # Print JSON-like Dockerfile
    def print_df_json(self) :
        obj = json.loads(self.dfp.json)
        print(json.dumps(obj, indent=1))


# Parse a Dockerfile file and returns a Dockerfile object
def parse_Dockerfile(uri=".") :

    # Create a Dockerfile object
    df = Dockerfile(uri)
    return df

