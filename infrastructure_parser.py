import docker

# Create a class to represent the Docker Host
class Host:

    def __init__(self, node_id, docker_v, OS, kernel_v, CPUs, Mem, Registry="https://index.docker.io/v1/"):
        self.node_id = node_id
        self.docker_v = docker_v
        # OPTION: StorageDriver
        self.OS = OS
        self.kernel_v = kernel_v
        self.CPUs = CPUs
        self.Mem = Mem
        self.Registry = Registry


# First, we need to connect to the Docker daemon
# This returns a client configured from environment variables.
client = docker.from_env()
# Alternatives: docker.DockerClient


def get_Infrastructure():

    # Equivalent to run docker info
    info = client.info()

    # Convert bytes to GB
    MemTotal = round(info["MemTotal"]/1000000000, 2)

    ### TODO ###
    # Get the (default) Registry

    aux = Host("node_0", info["ServerVersion"], info["OperatingSystem"], info["KernelVersion"], info["NCPU"], MemTotal)
    return aux

