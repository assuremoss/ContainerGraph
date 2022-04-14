import json


class Permission :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    def __init__(self, profile, capabilities, syscalls, read_only, no_new_priv, AppArmor_profile, Seccomp_profile) :
        self.profile = profile
        self.capabilities = capabilities
        self.syscalls = syscalls
        self.read_only = read_only
        self.no_new_priv = no_new_priv
        self.AppArmor_profile = AppArmor_profile
        self.Seccomp_profile = Seccomp_profile

    def print_perm(self) :
        print('profile: ' + self.profile)
        print(self.capabilities)
        print(self.syscalls)
        print('read_only: ' + self.read_only)
        print('no_new_priv: ' + self.no_new_priv)
        print('AppArmor_profile: ' + self.AppArmor_profile)
        print('Seccomp_profile: ' + self.Seccomp_profile)


# class AppArmor :
#     """
#     TODO
#     """

#     def __init__():
#         print()


# class SecComp :
#     """
#     TODO
#     """

#     def __init__():
#         print()


def parse_CAPS_file() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    try :
        with open('./files/permission_taxonomy.json', 'r') as perm_file :
            perm = json.load(perm_file)

            capabilities = perm['capabilities']
            syscalls = perm['syscalls']

            return capabilities, syscalls

    except FileNotFoundError as error :
        print(error)
        exit(1)


def get_all_syscalls() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """
    
    _, syscalls = parse_CAPS_file()

    all_syscalls = []
    for syscall in syscalls :
        all_syscalls.append(syscall['name'])

    return all_syscalls


def get_all_caps() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """
    
    capabilities, _ = parse_CAPS_file()

    all_caps = []
    for cap in capabilities : 
        all_caps.append(list(cap.keys())[0])

    return all_caps


def build_permissions(cont_id, run_args) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    all_caps = get_all_caps()
    all_syscalls = get_all_syscalls()
    default_cap = []
    default_syscall = []
    
    # Default Docker Profile
    profile = 'docker-default'
    capabilities = default_cap
    syscalls = default_syscall
    read_only = 'False'
    no_new_priv = 'False'
    AppArmor_profile = 'docker-default'
    Seccomp_profile = 'docker-default'

    # parse docker run arguments and check for permissions parameters
    for i in range(len(run_args)) :

        arg = run_args[i]

        # Drop Capabilities
        if arg.startswith('--cap-drop') or arg.startswith('--CAP-DROP'):
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            profile = cont_id + '_custom'

            if value == 'all' or value == 'ALL' : 
                capabilities = []
                continue

            # Standardize (CAP) value
            elif not value.startswith('CAP_') : 
                value = 'CAP_' + value.upper()
            else : value = value.upper()
                      
            capabilities.remove(value)

        # Add Capabilities
        if arg.startswith('--cap-add') or arg.startswith('--CAP-ADD'):
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            profile = cont_id + '_custom'

            if value == 'all' or value == 'ALL' : 
                capabilities = all_caps
                continue

            # Standardize (CAP) value
            elif not value.startswith('CAP_') : 
                value = 'CAP_' + value.upper()
            else : value = value.upper()
                      
            capabilities = list(set(capabilities + [value]))

        # Privileged Profile
        if run_args[i] == '--privileged' :
                profile = 'docker-privileged'
                capabilities = all_caps
                syscalls = all_syscalls
                AppArmor_profile = 'unconfined'
                Seccomp_profile = 'unconfined'

        # Mount the container's root filesystem as read only
        if run_args[i] == '--read-only' :
            profile = 'docker-read-only'
            read_only = 'True'
            ### CAPs ###
            ### SYSCALLs ###

        # Docker Security Options
        if arg.startswith('--security-opt') :

            # REFERENCE
            # https://docs.docker.com/engine/reference/run/#security-configuration

            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            profile = cont_id + '_custom'

            if value.startswith('no-new-privileges') :
                aux = value.split(':')[1]
                if aux == 'true' : 
                    no_new_priv = 'True'
                    ### TO CHECK
                    # capabilities & syscalls
                    ###

            elif value == 'apparmor=unconfined' :
                AppArmor_profile = 'unconfined'
                ### TO CHECK
                # capabilities & syscalls
                ###
                capabilities = all_caps
                syscalls = all_syscalls

            elif value == 'seccomp=unconfined' :
                Seccomp_profile = 'unconfined'
                ### TO CHECK
                # capabilities & syscalls
                ###
                capabilities = all_caps
                syscalls = all_syscalls

            ### TODO: apparmor=custom_profile
            # elif value.startswith('apparmor=') :

            ### TODO: seccomp=custom_profile
            # elif value.startswith('seccomp=') :

    # Sort Capabilities and Systemcalls
    capabilities.sort()
    syscalls.sort()

    perm = Permission(profile, capabilities, syscalls, read_only, no_new_priv, AppArmor_profile, Seccomp_profile)
    return perm


def parse_AppArmor() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """
    print("TODO")


def parse_Seccomp() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """
    print("TODO")