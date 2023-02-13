import docker
import socket, sys, platform, os, subprocess


class Host:
    """
    Create a class to represent the host running a (one or more) container engines.    
    """

    def __init__(self, name, h_platform, hostname, processor, kernel_v, cpus, mem) :
        self.name = name
        self.h_platform = h_platform
        self.hostname = hostname
        self.processor = processor
        self.kernel_v = kernel_v
        self.cpus = cpus
        self.mem = mem

    def print_host(self) :
        print("name: " + self.name)
        print("h_platform: " + self.h_platform)
        print("hostname: " + self.hostname)
        print("processor: " + self.processor)
        print("kernel_v: " + self.kernel_v)
        print("cpus: " + self.cpus)
        print("mem: " + self.mem)


class DockerHost:
    """
    Create a class to represent the host running the Docker container engine.    
    """

    def __init__(self, host, docker_v, containerd_v, runc_v, storage, Registry="https://index.docker.io/v1/"):
        self.name = "DockerEngine"
        self.host = host
        self.docker_v = docker_v
        self.containerd_v = containerd_v
        self.runc_v = runc_v
        self.storage = storage
        self.registry = Registry

    def print_docker_host(self) :
        self.host.print_host()
        print(self.name)
        print("docker_v: " + self.docker_v)
        print("containerd_v: " + self.containerd_v)
        print("runc_v: " + self.runc_v)
        print("storage: " + self.storage)
        print("registry: " + self.registry)


class LXCHost:
    """
    Create a class to represent the host running the Linux container.    
    """

    def __init__(self, host) :
        self.host = host


class PodmanHost:
    """
    Create a class to represent the host running the Podman container engine.    
    """

    def __init__(self, host) :
        self.host = host



def connect_to_Docker() : 
    return docker.from_env()


def build_DockerHost(host):
    """ 
    Description
    """

    try:
        client = connect_to_Docker()

        # Equivalent to run `docker info`
        info = client.info()

        # Equivalent to run `docker version`
        version = client.version()

        docker_v = version["Components"][0]["Version"]
        containerd_v = version["Components"][1]["Version"]
        runc_v = version["Components"][2]["Version"]

        kernel_v = version["Components"][0]["Details"]["KernelVersion"].split('.')
        # host.kernel_v = str(kernel_v[0]) + '.' + str(kernel_v[1])
        temp_v = str(kernel_v[0]) + '.' + str(kernel_v[1])
        if len(kernel_v) > 2 :
            temp_v += '.' + str(kernel_v[2]).split('-')[0]
        else :
            temp_v += '.0'
        host.kernel_v = temp_v

        #######################################
        ### HARDCODED LOWEST KERNEL VERSION ###
        
        host.kernel_v = '3.16.0'
        docker_v = '1.5.0'
        containerd_v = '0.0.1'
        runc_v = '0.0.1'
        
        #######################################
        
        return DockerHost(host, 
                docker_v,
                containerd_v, 
                runc_v, 
                info["Driver"],
                info["IndexServerAddress"])

    except docker.errors.DockerException as error :
        print(error)
    except subprocess.CalledProcessError as error :
        print(error)
        exit(1)


def build_PodmanHost(host) :
    """
    TODO
    """

    return
    

def build_LXCHost(host) :
    """
    TODO
    """

    return
    

def detect_cont_engine() :
    """
    TODO
    """
    
    if is_docker() :
        return "Docker"

    # elif is_lxc() :
    #     return "LXC"

    # elif is_podman() :
    #     return "Podman"


def is_docker() :
    """
    TODO
    """

    os.popen("docker -v")
    result = int(os.popen("echo $?").readline())

    if result == 0 : return True
    else : return False


def build_host(os_platform) :
    """
    TODO
    """

    if os_platform == "Linux" :

        name = "LinuxHost"
        h_platform = "Linux"
        hostname = socket.gethostname()
        processor = platform.machine()
        kernel_v = platform.release()
        cpus = os.popen("cat /proc/cpuinfo | grep processor | wc -l").readline()
        mem = os.popen("grep MemTotal /proc/meminfo").readline()[17:-3]
        mem = round(int(mem) / (1024*1024), 2)
        mem = str(mem) + "GB"

    elif os_platform == "MacOS" :
        
        name = "MacOSHost"
        h_platform = "MacOS"
        hostname = socket.gethostname()
        processor = platform.machine()
        kernel_v = ''
        cpus = os.popen("sysctl -n hw.ncpu").readline()
        mem = os.popen("sysctl -n hw.physmem").readline()
        mem = round(int(mem) / (1024*1024), 2)
        mem = str(mem) + "GB"

    elif os_platform == "Windows" :

        print("Change OS :)")
        exit(1)

    return Host(name, h_platform, hostname, processor, kernel_v, cpus, mem)


def detect_os() :
    """
    TODO
    """

    # Linux
    if sys.platform == "linux" or sys.platform == "linux2" :
        return "Linux"
    
    # OS X
    elif sys.platform == "darwin" :
        return "MacOS"
    
    # Windows
    elif sys.platform == "win32 ":
        return "Windows"


def get_Infrastructure() :
    """
    TODO
    """

    # Detect OS
    os_platform = detect_os()

    # Build the Host object
    host = build_host(os_platform)

    # Detect Container Engine
    cont_eng = detect_cont_engine()

    if cont_eng == "Docker" :
        return build_DockerHost(host)

    # elif cont_eng == "Podman" :
    #     return build_PodmanHost(host)

    # elif cont_eng == "LXC" :
    #     return build_LXCHost(host)
