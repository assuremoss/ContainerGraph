import docker

# Create a class to represent the Docker Host
class Host:

    def __init__(self, hostname, docker_v, OS, kernel_v, CPUs, Mem, Registry="https://index.docker.io/v1/"):
        self.hostname = hostname
        self.docker_v = docker_v
        # OPTION: StorageDriver
        self.os = OS
        self.kernel_v = kernel_v
        self.cpus = CPUs
        self.mem = Mem
        self.registry = Registry


# First, we need to connect to the Docker daemon
# This returns a client configured from environment variables.
client = docker.from_env()


def get_Infrastructure():

    # Equivalent to run docker info
    info = client.info()

    # Convert bytes to GB
    MemTotal = round(info["MemTotal"]/1000000000, 2)

    aux = Host(info["Name"], 
               info["ServerVersion"], 
               info["OperatingSystem"], 
               info["KernelVersion"], 
               info["NCPU"], 
               MemTotal, 
               info["IndexServerAddress"])
    return aux

