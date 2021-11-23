import json

# This class represents a JSON-like object containing the privileges binded to a container.
class Permissions : 
    
    def __init__(self, profile, files, network, processes, adminop) :
        self.profile = profile
        self.files = files
        self.network = network
        self.processes = processes
        self.adminop = adminop

    def add_Permission(self, cap_list) :
        print("TODO")

    def remove_Permission(self, cap_list) :
        print("TODO")


"""

For now, we implemented this:
 - cap-drop=ALL 
 - docker default capabilities
 - cap-add=ALL (or --privileged, although not equivalent, but only for now);
 - --read-only (filesystem)

"""

def get_none_profile() :

    pp = {"files": ["read", "write"], # TO CHECK
        "network": ["none"], # TO CHECK
        "processes": ["none"], # TO CHECK
        "adminop": ["none"] 
        }

    aux = Permissions("none", pp["files"], pp["network"], pp["processes"], pp["adminop"])
    return aux


def get_default_profile() :
    pp = {"files": ["read", "write", "execute"],
        "network": ["connection"], 
        "processes": ["new_process", "kill_process"], # TO CHECK 
        "adminop": ["apt", "chmod", "adduser", "mount"]}

    aux = Permissions("default", pp["files"], pp["network"], pp["processes"], pp["adminop"])
    return aux


def get_all_profile() :
    pp = {"files": ["read", "write", "execute"],
        "network": ["connection"], 
        "processes": ["new_process", "kill_process"], # TO CHECK 
        "adminop": ["apt", "chmod", "adduser", "mount", "mount_dev"]}

    aux = Permissions("all", pp["files"], pp["network"], pp["processes"], pp["adminop"])
    return aux





def create_Permissions(profile="Docker") :

    # Docker parameter: --cap-drop=all
    if profile == "None" :
        return get_none_profile()

    # Default Docker capabilities list
    elif profile == "Docker" : 
        return get_default_profile()

    # Docker parameter: --cap-add=all or --privileged
    elif profile == "All" :
        return get_all_profile()
    
    else : 
        print("Wrong permission set! Exiting...")
        exit(1)

