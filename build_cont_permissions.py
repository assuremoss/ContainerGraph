

class Permission :
    """
    TODO
    """

    def __init__(self, profile, CAPs, syscalls, read_only, AppArmor_profile, Seccomp_profile) :
        self.profile = profile
        self.CAPs = CAPs
        self.syscalls = syscalls
        self.read_only = read_only
        self.AppArmor_profile = AppArmor_profile
        self.Seccomp_profile = Seccomp_profile


# List of default Docker Linux Capabilities
CAPs_default = "AUDIT_WRITE, CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL, MKNOD, NET_BIND_SERVICE, NET_RAW, SETFCAP, SETGID, SETPCAP, SETUID, SYS_CHROOT"

# List of default Docker (allowed) system calls
syscalls_default = "accept, access, bind, capget, chmod, chown, close, connect, creat, execve, exit, fork, ioctl, kill, mkdir, open, read, rename, send, socket, time, uname, write"


def compare_Permissions(permission1, permission2) :
    """
    TODO
    """

    if permission1.profile == permission2.profile :
        if permission1.CAPs == permission2.CAPs :
            if permission1.syscalls == permission2.syscalls :
                if permission1.read_only == permission2.read_only :
                    if permission1.AppArmor_profile == permission2.AppArmor_profile :
                        if permission1.Seccomp_profile == permission2.Seccomp_profile :
                            return True

    return False


def build_permissions(run_args) :
    """
    TODO
    """

    # parse docker run arguments and check for permissions parameters
    for arg in run_args :

        if arg == '--cap-drop' or arg == '--CAP-DROP' :
            # '--cap-drop=ALL --cap-drop all'
            print('TODO')

        if arg == '--cap-add' or arg == '--CAP-ADD' :
            # '--cap-add=ALL --cap-add all'
            print('TODO')

        if arg == '--security-opt' :

            # --security-opt apparmor=unconfined
            # --security-opt seccomp=unconfined

            print('ciao')

        if arg == '--privileged' :
            perm = Permission('docker-privileged', '*', '*', 'false', 'unconfined', 'unconfined')
            return perm

        if arg == '--read-only' :
            perm = Permission('docker-default', CAPs_default, syscalls_default, 'true', 'docker-default', 'docker-default')
            return perm

        # default docker run configuration
        # TRANSLATE INTO AN IF (if any of the previous ==> default profile)
        else :
            perm = Permission('docker-default', CAPs_default, syscalls_default, 'false', 'docker-default', 'docker-default')
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