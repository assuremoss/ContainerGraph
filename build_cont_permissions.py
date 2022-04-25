from string import capwords
from parse_Apparmor import apparmor_parser
from parse_Seccomp import seccomp_parser
from parse_perm_file import get_all_CAPs, get_all_syscalls
from parse_Seccomp import analyze_syscalls
from parse_perm_file import parse_perm_taxonomy


class Permission :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    def __init__(self, profile, Seccomp_profile, Apparmor_profile,  read_only, no_new_priv, caps, syscalls) :
        self.profile = profile
        self.Seccomp_profile = Seccomp_profile
        self.Apparmor_profile = Apparmor_profile
        self.read_only = read_only
        self.no_new_priv = no_new_priv
        self.caps = caps
        self.syscalls = syscalls


def build_permissions(cont_id, run_args, kernel_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # All CAPs and system calls
    
    all_caps = get_all_CAPs()
    all_sysc = get_all_syscalls()

    # Permission object fields
    profile = 'docker-default'
    Seccomp_p = []
    AppArmor_p = []
    read_only = False 
    no_new_priv = False

    # List of allowed capabilities
    a_caps = []
    # List of denied capabilities
    d_caps = []
    # List of allowed syscalls
    a_syscalls = []
    # List of denied syscalls
    d_syscalls = []

    # parse docker run arguments 
    for i in range(len(run_args)) :

        arg = run_args[i]

        # Drop Capabilities
        if arg.startswith('--cap-drop') or arg.startswith('--CAP-DROP'):
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            profile = cont_id + '_custom'

            if value == 'all' or value == 'ALL' : 
                d_caps = all_caps
                continue

            # Standardize (CAP) value
            elif not value.startswith('CAP_') : 
                value = 'CAP_' + value.upper()
            else : value = value.upper()
                      
            d_caps.append(value)

        # Add Capabilities
        if arg.startswith('--cap-add') or arg.startswith('--CAP-ADD'):
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            profile = cont_id + '_custom'

            if value == 'all' or value == 'ALL' : 
                a_caps = all_caps
                continue

            # Standardize (CAP) value
            elif not value.startswith('CAP_') : 
                value = 'CAP_' + value.upper()
            else : value = value.upper()
            
            a_caps = list(set(a_caps + [value]))

        # Privileged Profile
        if run_args[i] == '--privileged' :
            return Permission('docker-privileged', 'unconfined', 'unconfined', False, False, all_caps, all_sysc)

        # Mount the container's root filesystem as read only
        if run_args[i] == '--read-only' :
            profile = 'docker-read-only'
            read_only = True
            # The capabilities are the same as for the docker-default AppAmor profile (i.e., 14 caps).
            a_caps += apparmor_parser().caps     
            #
            # Forbidden system calls 
            d_syscalls += apparmor_parser().d_syscalls
            d_syscalls += ['chmod', 'chown', 'chown32', 'write', 'chroot', 'creat', 'create_module', 'delete_module', 'epoll_create', 'epoll_create1', 'allocate', 'fchmod', 'fchmodat', 'fchown', 'chown32', 'chownat', 'fsetxattr', 'init_module', 'io_destroy', 'lchown', 'lchown32', 'mkdir', 'mkdirat', 'mknod', 'mknodat', 'move_mount', 'move_pages', 'pivot_root', 'rename', 'renameat', 'rmdir', 'setdomainname', 'setfsgid', 'setfsgid32', 'setfsuid', 'setfsuid32', 'setgid', 'setgid32', 'setgroups', 'setgroups32', 'sethostname', 'setitimer', 'setns', 'setpgid', 'setpriority', 'setregid', 'setregid32', 'setresgid', 'setresgid32', 'setreuid', 'setreuid32', 'setrlimit', 'setsid', 'setsockopt', 'set_thread_area', 'set_tid_address', 'settimeofday', 'setuid', 'setuid32', 'setxattr', 'ulink', 'ulinkat', 'unshare', 'write', 'writev']
                   
        # Docker Security Options
        if arg.startswith('--security-opt') :

            # REFERENCE
            # https://docs.docker.com/engine/reference/run/#security-configuration

            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            profile = cont_id + '_custom'

            # NoNewPriv: the container can not start a process with more privileges than its own.
            # Syntax: --security-opt=no-new-privileges:true
            if value.startswith('no-new-privileges') :
                aux = value.split(':')[1]
                if aux == True : 
                    no_new_priv = True
                    # The capabilities are the same as for the docker-default AppAmor profile (i.e., 14 caps).
                    a_caps += apparmor_parser().caps
                    #
                    # TODO: which system calls are forbidden, beside default ?
                    d_syscalls += apparmor_parser().d_syscalls

            elif value == 'seccomp=unconfined' :
                Seccomp_p = 'unconfined'

            # Seccomp custom profile
            elif value.startswith('seccomp=') :
                uri = value.replace('seccomp=', '')
                Seccomp_p = seccomp_parser('', uri)

            elif value == 'apparmor=unconfined' :
                AppArmor_p = 'unconfined'
                # By default, if no other capabilities are added, with unconfined apparmor Docker will only grant the 14 default capabilities.
                a_caps += apparmor_parser().caps

            # AppArmor custom profile
            elif value.startswith('apparmor=') :
                uri = value.replace('apparmor=', '')
                AppArmor_p = apparmor_parser('', uri)
                a_caps += AppArmor_p.caps
                a_syscalls += AppArmor_p.a_syscalls
                d_syscalls += AppArmor_p.d_syscalls

    # Default profile
    if not Seccomp_p : 
        Seccomp_p = seccomp_parser()

    # Default profile
    if not AppArmor_p : 
        AppArmor_p = apparmor_parser()
        a_caps += AppArmor_p.caps
        a_syscalls += AppArmor_p.a_syscalls
        d_syscalls += AppArmor_p.d_syscalls

    # Get a list of allowed system calls, also based on granted CAPs
    if Seccomp_p == 'unconfined' :
        a_s = all_sysc
        d_s = []
    else :
        a_s, d_s = analyze_syscalls(Seccomp_p, a_caps)
    
    a_syscalls += a_s
    d_syscalls += d_s

    # List of allowed caps - list of disallowed caps
    caps = [c for c in a_caps if c not in d_caps]
    caps = list(set(caps))
    caps.sort()
    
    sysc = [s for s in a_syscalls if s not in d_syscalls]
    sysc = list(set(sysc))
    sysc.sort()

    # Remove CAPs and syscalls not supported from the current version of the kernel
    caps, sysc = remove_unsupported_perm(caps, sysc, kernel_v)

    return Permission(profile, Seccomp_p, AppArmor_p, read_only, no_new_priv, caps, sysc)


def remove_unsupported_perm(caps, sysc, kernel_v):
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    result = parse_perm_taxonomy()

    cap_dict = result['capabilities']
    sysc_dict = result['syscalls']

    for cap in caps : 
        for c in cap_dict : 
            if c['name'] == cap : 
                current_kernel_v = c['kernel_v'][:3]                
                if kernel_v < current_kernel_v :
                    caps.remove(cap)

    for s in sysc : 
        for sd in sysc_dict : 
            if sd['name'] == s : 
                current_kernel_v = sd['kernel_v'][:3]                
                if kernel_v < current_kernel_v :
                    sysc.remove(s)

    return caps, sysc

