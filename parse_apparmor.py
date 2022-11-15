from pathlib import Path
from parse_perm_file import get_all_syscalls


class AppArmor_Profile : 

    def __init__(self, name, uri, caps, a_syscalls, d_syscalls):
        self.name = name
        self.uri = uri
        self.caps = caps # List of allowed capabilities
        self.a_syscalls = a_syscalls # List of allowed system calls
        self.d_syscalls = d_syscalls # List of denied system calls


def parse_apparmor_file(uri) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    try :
        with open(uri, 'r') as profile :
            return profile.readlines()

    except FileNotFoundError as error :
        print(error)
        exit(1)


def get_caps_syscalls(profile) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    ### MAN PAGE
    # https://manpages.ubuntu.com/manpages/xenial/man5/apparmor.d.5.html
    ###

    # All system calls
    all_sysc = get_all_syscalls()

    a_caps = [] 
    d_caps = [] 
    a_syscalls = []
    d_syscalls = []

    # Iterate over the profile's lines
    for line in profile :
        # Strip left white space
        line = line.strip().strip(',')

        # Ignore empty lines 
        if line : 

            # Skip profile name
            if line.startswith('profile') :
                continue

            # Other profiles
            elif line.startswith('#include') :
                # TODO
                # For now, skip parsing #include profiles.
                continue

            # Skip comments
            elif line.startswith('#') :
                continue
        
            # Skip last line
            elif line.startswith('}') :
                continue

            # File options
            elif line.startswith('/') :
                continue
        
            # File options
            elif line.startswith('file') :
                continue

            # Audit options
            elif line.startswith('audit') :
                continue

            # Network options
            elif line.startswith('network') :
                continue

            # Parse deny options
            elif line.startswith('deny') :
                aux = line.split()

                # Deny options on files
                if aux[1].startswith('/') :
                    # TODO
                    # For now, skip rwx permissions on files.
                    continue

                elif aux[1].startswith('@') :
                    # TODO
                    # For now, skip rwx permissions on files.
                    continue

                # deny network
                elif aux[1] == 'network' :
                    # deny access to all networking
                    # skip for now
                    continue

                # deny syscall
                elif aux[1] in all_sysc :
                    # TODO
                    # check for more denied systemcalls (e.g. deny mount, unshare, etc.)
                    if not aux[1] in d_syscalls : d_syscalls.append(aux[1])

                # deny cap
                elif aux[1] == 'capability' :
                    cap = aux[2].upper()
                    cap = 'CAP_' + cap  

                    # TODO
                    # check for more denied caps
                    if not cap in d_caps : d_caps.append(cap)  
            
            # Parse capabilities
            elif line.startswith('capability') :
                aux = line.split()

                if aux[0] == 'capability,' :
                    # skip for now
                    continue

                elif len(aux) > 1 :
                    cap = aux[1].upper()
                    cap = 'CAP_' + cap    

                    if not cap in a_caps : a_caps.append(cap)    

            elif line.startswith('owner') :
                # skip for now
                continue

            # check allow (e.g. mount, or pivot_root,)
            else :
                aux = line.split()

                if aux[0] in all_sysc :
                    # for now, skip options=...
                    if not aux[0] in a_syscalls : a_syscalls.append(aux[0])

    # Return the list of allowed caps - list of disallowed caps
    caps = [c for c in a_caps if c not in d_caps]
    return caps, a_syscalls, d_syscalls


def apparmor_parser(profile_name='', uri='') :
    """  Description
    """

    if not uri : 
        uri = './files/Apparmor/docker-default'

    elif not uri.startswith('/etc/apparmor.d/containers/') : 
        uri = '/etc/apparmor.d/containers/' + uri

    profile = parse_apparmor_file(uri)

    caps, a_syscalls, d_syscalls = get_caps_syscalls(profile)

    caps.sort()
    a_syscalls.sort()
    d_syscalls.sort()

    if not profile_name :
        # Strip path and .json
        p = Path(uri)
        name = p.parts[-1].strip('.json')
    else : name = profile_name

    return AppArmor_Profile(name, uri, caps, a_syscalls, d_syscalls)

