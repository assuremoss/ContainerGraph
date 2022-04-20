import json


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
        all_caps.append(cap['name'])

    return all_caps
