from pathlib import Path
import json
from build_cont_permissions import get_all_syscalls


class SecComp_Profile : 

    def __init__(self, name, uri, syscalls):
        self.name = name
        self.uri = uri
        self.syscalls = syscalls  # List of ALLOWED system calls


def parse_seccomp_file(uri) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    try :
        with open(uri, 'r') as profile :
            return json.load(profile)

    except FileNotFoundError as error :
        print(error)
        exit(1)


def get_syscalls(profile) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    syscalls = []
    
    syscalls = get_all_syscalls()
    for n in syscalls:
        if syscalls.count(n)>1:
            print("Repeated number: ",n)

    for key in profile :
        
        # Analyze the profile defaultAction
        if key == 'defaultAction' :
            # Syscalls denied
            if profile[key] == "SCMP_ACT_KILL_THREAD" or \
               profile[key] == "SCMP_ACT_TRAP" or \
               profile[key] == "SCMP_ACT_ERRNO" or \
               profile[key] == "SCMP_ACT_KILL_PROCESS" :
                syscalls = []
            # Syscalls allowed
            elif profile[key] == "SCMP_ACT_ALLOW" or \
                 profile[key] == "SCMP_ACT_LOG" :
                syscalls = get_all_syscalls()

        elif key == 'syscalls' :
            sysc_list = profile['syscalls']
            # Iterate over syscalls dictionaries
            for sysc in sysc_list :

                if sysc['action'] == "SCMP_ACT_ALLOW" :
                    
                    # "includes"
                        # - minKernel --> dict
                        # - arches --> skip
                        # - caps --> dict
                    
                    # "excludes" ??? - what does it mean ...
                    
                    # Single system call
                    if 'name' in sysc :
                        syscalls.append(sysc['name'])
                        syscalls = list(set(syscalls))
                    # Multiple system calls
                    elif 'names' in sysc :
                        syscalls = list(set(syscalls + sysc['names']))

                elif sysc['action'] == "SCMP_ACT_ERRNO" :
                    # Single system call
                    if 'name' in sysc :
                        if sysc['name'] in syscalls :
                            syscalls.remove(sysc['name'])
                    # Multiple system calls
                    elif 'names' in sysc :
                        for s in sysc['names']:
                            try:
                                print(s)
                                syscalls.remove(s)
                            except ValueError : pass

    print(syscalls)
    return syscalls


def parse_seccomp(uri='./files/Seccomp/example.json') :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # Parse profile and retrieve the allowed system calls
    profile = parse_seccomp_file(uri)
    syscalls = get_syscalls(profile)

    # Strip path and .json
    p = Path(uri)
    name = p.parts[-1].strip('.json')

    return SecComp_Profile(name, uri, syscalls)

