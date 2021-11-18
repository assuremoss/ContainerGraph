import json


class Permissions : 
    
    def __init__(self, must, internet, files, other):
        self.must = must
        self.internet = internet
        self.files = files
        self.other = other


def create_Permissions(profile="Docker") :
    if profile == "Docker" : 
        return default_Permissions()
    else :
        return custom_Permissions(profile)

# Reference: https://github.com/moby/moby/blob/master/oci/caps/defaults.go#L6-L19
def default_Permissions() :

    must = [""]
    internet = [""]
    files = [""]
    other = [""]



    print("TODO")






    aux = Permissions(must, internet, files, other)
    return aux


def custom_Permissions() :
    print("TODO")


""" 

There are basically two options here we have to follow:

    1. Using the Docker's default profile if the user doesn't specify one and eventually and the run-time additional parameters.

    2. Parse an existing profile and create a custom Permission object for a container.

For now we only do the first one.

"""

