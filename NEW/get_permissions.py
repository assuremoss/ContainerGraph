

class Permissions : 
    """
    This class represents a JSON-like object containing the privileges belonging to a container.
    """    

    def __init__(self, profile) :

        self.profile = profile

        # Default Docker profile
        if profile == "default" :
            self.files = ["read", "write", "execute"]
            self.network = ["connection"]
            self.processes = ["new_process", "kill_process"]
            self.adminop = ["mount", "add_user"]

        # Case: --cap-add=ALL
        elif profile == "all" : 
            print("TODO_ALL_CONSTRUCTOR")

        # Case: --privileged
        elif profile == "privileged" :
            print("TODO")

        # Case: --read-only
        elif profile == "read_only" :
            print("TODO")

        # Case: --cap-drop=ALL
        elif profile == "none" :
            print("TODO")


    def add_Permission(self, cap_list) :
        print("TODO")

    def remove_Permission(self, cap_list) :
        print("TODO")


def create_Permissions(profile) :
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
    
    perm = Permissions(profile)
    return perm

