import docker

class Host:
    """
    Create a class to represent the host running the Docker container engine.    
    """

    def __init__(self, hostname, docker_v, containerd_v, runc_v, storage, os, kernel_v, cpus, mem, Registry="https://index.docker.io/v1/"):
        self.hostname = hostname
        self.docker_v = docker_v
        self.containerd_v = containerd_v
        self.runc_v = runc_v
        self.storage = storage
        self.os = os
        self.kernel_v = kernel_v
        self.cpus = cpus
        self.mem = mem
        self.registry = Registry


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


def get_Infrastructure():
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

    # Convert bytes to GB
    MemTotal = round(info["MemTotal"]/1000000000, 2)
    MemTotal = str(MemTotal) + "GB"

    # Equivalent to run `docker version`
    version = client.version()
    containerd_v = version["Components"][1]["Version"]

    aux = DockerHost(info["Name"], 
               info["ServerVersion"],
               containerd_v, 
               info["RuncCommit"]["ID"], 
               info["Driver"],
               info["OperatingSystem"], 
               info["KernelVersion"], 
               info["NCPU"], 
               MemTotal, 
               info["IndexServerAddress"])
    return aux

