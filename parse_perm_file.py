import json


def parse_perm_taxonomy() :
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

            kernel_v = perm['kernel_v']

            docker_v = perm['docker_v']
            containerd_v = perm['containerd_v']
            runc_v = perm['runc_v']

            result = {
                'capabilities': capabilities, 
                'syscalls': syscalls, 
                'kernel_v': kernel_v, 
                'docker_v': docker_v, 
                'containerd_v': containerd_v, 
                'runc_v': runc_v
            }

            return result

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

    result = parse_perm_taxonomy()
    all_sysc = [ s['name'] for s in result['syscalls'] ]
    return all_sysc


def get_all_CAPs() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    result = parse_perm_taxonomy()
    all_CAPs = [ c['name'] for c in result['capabilities'] ]
    return all_CAPs

