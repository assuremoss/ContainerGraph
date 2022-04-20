from pathlib import Path
import json
from parse_Apparmor import get_all_syscalls


class SecComp_Profile : 

    def __init__(self, name, uri, syscalls):
        self.name = name
        self.uri = uri
        self.syscalls = syscalls  # List of dict of ALLOWED system calls


def analyze_syscalls(Seccomp_p, caps=[], minKernel="") :
    """  brief title.
    
    Arguments:
    uri - path to the seccomp profile

    Description:
    blablabla
    """
  
    a_syscalls = []
    d_syscalls = []

    for s in Seccomp_p.syscalls :

        # Skip syscalls that require specific architectures
        if s['arches'] :
            continue

        # Allowed syscalls with CAP
        elif s['caps'] :

            # if s['minKernel'] :
                # TODO

            if s['caps'][0] in caps :
                a_syscalls.extend(s['syscalls'])

        # Allowed syscalls without CAP
        elif 'syscalls' in s :
        
            if not s['caps'] :

            # if s['minKernel'] :
                # TODO

                a_syscalls.extend(s['syscalls'])

    a_syscalls = list(set(a_syscalls))
    a_syscalls.sort()

    d_syscalls = list(set(d_syscalls))
    d_syscalls.sort()

    return a_syscalls, d_syscalls


def parse_seccomp_file(uri) :
    """  brief title.
    
    Arguments:
    uri - path to the seccomp profile

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

    # List of dict
    syscalls = []

    # All system calls
    all_sysc = get_all_syscalls()
    
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
                aux = {'syscalls': all_sysc, 'minKernel': '', 'caps': '', 'arches': ''}
                syscalls.append(aux)

        elif key == 'syscalls' :
            sysc_list = profile['syscalls']

            # Iterate over syscalls dictionaries
            for sysc in sysc_list :

                if sysc['action'] == "SCMP_ACT_ALLOW" :

                    # Single system call
                    if 'name' in sysc and sysc['name'] in all_sysc :
                        aux = {'syscalls': sysc['name'], 'minKernel': '', 'caps': '', 'arches': ''}

                    # Multiple system calls
                    elif 'names' in sysc : 
                        # Keep only the system calls that we have in our perm file
                        aux = [s for s in sysc['names'] if s in all_sysc]
                        aux = {'syscalls': aux, 'minKernel': '', 'caps': '', 'arches': ''}

                    # if 'args' in sysc :
                        # For now, we ignore the args options.
                    
                    # if 'comment' in sysc :
                        # For now, we ignore the args options.

                    # Additional options
                    if 'includes' in sysc :
                        
                        if 'minKernel' in sysc['includes'] :
                            aux['minKernel'] = sysc['includes']['minKernel']

                        if 'caps' in sysc['includes'] :
                            aux['caps'] = sysc['includes']['caps']
                        
                        if 'arches' in sysc['includes'] :
                            aux['arches'] = sysc['includes']['arches']
                    
                    # if 'excludes' in sysc :
                        # TODO

                    if not aux in syscalls :
                        # Append new value/s
                        syscalls.append(aux)
                    
                # Remove syscalls
                elif sysc['action'] == "SCMP_ACT_ERRNO" :

                    for aux in syscalls :
                        # Single system call
                        if 'name' in sysc :
                            if aux['syscalls'] == sysc['name'] :
                                syscalls.remove(aux)

                        # Multiple system calls
                        elif 'names' in sysc :
                            if aux['syscalls'] == sysc['names'] :
                                syscalls.remove(aux)

    return syscalls


def seccomp_parser(profile_name='', uri='./files/Seccomp/docker-default.json') :
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

    if not profile_name :
        # Strip path and .json
        p = Path(uri)
        name = p.parts[-1].strip('.json')
    else : name = profile_name

    return SecComp_Profile(name, uri, syscalls)

