

import sys


class Permission :
    """
    TODO
    """

    def __init__(self, profile, capabilities, syscalls, read_only, AppArmor_profile, Seccomp_profile) :
        self.profile = profile
        self.capabilities = capabilities
        self.syscalls = syscalls
        self.read_only = read_only
        self.AppArmor_profile = AppArmor_profile
        self.Seccomp_profile = Seccomp_profile


# List of default Docker Linux Capabilities
capabilities_default = ["audit_write", "chown", "dac_override", "fowner", "fsetid", "kill", "mknod", "net_bind_service", "net_raw", "setfcap", "setgid", "setpcap", "setuid", "sys_chroot"]

all_capabilities = ["audit_write", "chown", "dac_override", "fowner", "fsetid", "kill", "mknod", "net_bind_service", "net_raw", "setfcap", "setgid", "setpcap", "setuid", "sys_admin", "sys_chroot", "sys_module"]


# List of default Docker (allowed) system calls
syscalls_default = ["accept", "access", "bind", "capget", "chmod", "chown", "close", "connect", "creat", "execve", "exit", "fork", "ioctl", "kill", "mkdir", "open", "read", "rename", "send", "socket", "time", "uname", "write"]

all_syscalls = ["accept", "access", "bind", "capget", "chmod", "chown", "close", "connect", "creat", "execve", "exit", "fork", "ioctl", "kill", "mkdir", "mount", "open", "read", "rename", "send", "socket", "time", "uname", "write", "unshare"]


def compare_Permissions(permission1, permission2) :
    """
    TODO
    """

    if permission1.profile == permission2.profile :
        if permission1.capabilities == permission2.capabilities :
            if permission1.syscalls == permission2.syscalls :
                if permission1.read_only == permission2.read_only :
                    if permission1.AppArmor_profile == permission2.AppArmor_profile :
                        if permission1.Seccomp_profile == permission2.Seccomp_profile :
                            return True

    return False


def build_permissions(cont_id, run_args) :
    """
    TODO
    """

    profile = 'docker-default'
    capabilities = capabilities_default
    syscalls = syscalls_default
    read_only = 'False'
    AppArmor_profile = 'docker-default'
    Seccomp_profile = 'docker-default'

    # parse docker run arguments and check for permissions parameters
    for i in range(len(run_args)) :

        # continue only if the current arg is a docker flag
        if run_args[i][:1] == '-' :

            if run_args[i] == '--cap-drop' :
                profile = cont_id + '_custom'
                if run_args[i+1] == 'all' :
                    capabilities = []
                else :
                    capabilities.remove(run_args[i+1])

            if run_args[i] == '--cap-add' :
                profile = cont_id + '_custom'
                if run_args[i+1] == 'all' :
                    capabilities = all_capabilities
                else :
                    capabilities = list(set(capabilities + [run_args[i+1]]))

            if run_args[i] == '--security-opt' :
                profile = cont_id + '_custom'
                if run_args[i+1] == 'apparmor=unconfined' :
                    AppArmor_profile = 'unconfined'
                    ### TO CHECK
                    # capabilities & syscalls
                    capabilities = all_capabilities
                    syscalls = all_syscalls

                elif run_args[i+1] == 'seccomp=unconfined' :
                    Seccomp_profile = 'unconfined'
                    ### TO CHECK
                    # capabilities & syscalls
                    capabilities = all_capabilities
                    syscalls = all_syscalls

                if 'apparmor=unconfined' in run_args and 'seccomp=unconfined' in run_args :
                    AppArmor_profile = 'unconfined'
                    Seccomp_profile = 'unconfined'
                    ### TO CHECK
                    capabilities = all_capabilities
                    syscalls = all_syscalls
                    ###

                ### TODO: apparmor=custom_profile

                ### TODO: seccomp=custom_profile

            if run_args[i] == '--privileged' :
                profile = 'docker-privileged'
                capabilities = all_capabilities
                syscalls = all_syscalls
                AppArmor_profile = 'unconfined'
                Seccomp_profile = 'unconfined'

            if run_args[i] == '--read-only' :
                profile = 'docker-read-only'
                read_only = 'True'

    perm = Permission(profile, capabilities, syscalls, read_only, AppArmor_profile, Seccomp_profile)
    return perm


def parse_AppArmor() :
    """
    TODO
    """
    print("TODO")


def parse_Seccomp() :
    """
    TODO
    """
    print("TODO")