from platform import architecture
import docker


class Host:
    """
    Create a class to represent the host running a (one or more) container engines.    
    """

    def __init__(self, hostname, os, architecture, kernel_v, cpus, mem) :
        self.hostname = hostname
        self.os = os
        self.architecture = architecture
        self.kernel_v = kernel_v
        self.cpus = cpus
        self.mem = mem


class DockerHost:
    """
    Create a class to represent the host running the Docker container engine.    
    """

    def __init__(self, host, docker_v, containerd_v, runc_v, storage, Registry="https://index.docker.io/v1/"):
        self.host = host
        self.docker_v = docker_v
        self.containerd_v = containerd_v
        self.runc_v = runc_v
        self.storage = storage
        self.registry = Registry


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
    """ 
    Connects to the Docker daemon running on the current host.

    Returns
    -------
    Docker client:
        Returns a client configured from environment variables.
    """

    # Connect to the Docker daemon
    client = docker.from_env()
    return client


def build_DockerHost(host):
    """ 
    Description

    Parameters
    ---------
    name: type
        Description

    Returns
    -------
    type:
        Description
    """

    client = connect_to_Docker()

    # Equivalent to run `docker info`
    info = client.info()

    # Equivalent to run `docker version`
    version = client.version()
    containerd_v = version["Components"][1]["Version"]

    aux = DockerHost(host, 
               info["ServerVersion"],
               containerd_v, 
               info["RuncCommit"]["ID"], 
               info["Driver"],
               info["IndexServerAddress"])
    return aux


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
    

def detect_cont_engine(img_id) :
    """
    TODO
    """

    # if we don't find the image in any engine --> error

    return "Docker"


def build_host() :
    """
    TODO
    """

    # Use python to get the Host information

    hostname = "vagrant"
    os = "linux"
    architecture = "x86_64"
    kernel_v = "5.10.47-linuxkit" 
    cpus = "8" 
    mem = "1.93GB"

    h = Host(hostname, os, architecture, kernel_v, cpus, mem)
    return h


def get_Infrastructure(img_id) :
    """
    TODO
    """

    # Detect from which container engine the image is from
    cont_eng = detect_cont_engine(img_id)

    host = build_host()

    if cont_eng == "Docker" :
        return build_DockerHost(host)

    elif cont_eng == "Podman" :
        return build_PodmanHost(host)

    elif cont_eng == "LXC" :
        return build_LXCHost(host)
