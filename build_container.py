from tracemalloc import start
import docker
import subprocess
from build_cont_permissions import build_permissions
from build_cont_config import build_config


class Container :
    """
    TODO
    """

    def __init__(self, cont_id, img_id, name, start_t, status, cconfig, permissions) :
        self.cont_id = cont_id
        self.img_id = img_id
        self.name = name
        self.start_t = start_t
        self.status = status
        self.cconfig = cconfig
        self.permissions = permissions

    def print_cont(self) :
        print('cont_id: ' + self.cont_id)
        print('img_id :' + self.img_id)
        print('name :' + self.name)
        print('start_t :' + self.start_t)
        print('status :' + self.status)
        print('')
        self.cconfig.print_cconfig()
        print('')
        self.permissions.print_perm()


def connect_to_Docker() : 
    """ 
    Connects to the Docker daemon running on the current host

    Returns
    -------
    Docker client:
        Returns a client configured from environment variables.
    """

    # Connect to the Docker daemon
    client = docker.from_env()
    return client


def build_container(options):
    """
    TODO
    """

    # list of docker run arguments (e.g. -d, -it, --rm, etc.)
    run_args = options[0][2:]

    # run the container
    cont_id, start_t = run_cont(options[0])

    client = connect_to_Docker()

    try:
        # retrieve container object
        cont = client.containers.get(cont_id)

        # retrieve container configuration
        cconfig = build_config(run_args)

        # retrieve container permissions
        permissions = build_permissions(cont_id, run_args)



    ############################
        print('Allowed CAPs: ' + str(len(permissions.caps)))
        # print(permissions.caps)
        print('Allowed syscalls: ' + str(len(permissions.syscalls)))
        # print(permissions.syscalls)
    ############################



        # build container object
        cont = build_cont_obj(cont, start_t, cconfig, permissions)
        # cont.print_cont()
        return cont
    
    # Raise an exception if the container doesn't exist
    except docker.errors.NotFound as error :
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)


def run_cont(command) :
    """
    TODO
    """

    try:
        # run the container
        cont_id = subprocess.check_output(command)
        # the stdout is of type bytes
        cont_id = cont_id.decode('utf-8')[:5]

        start_t = subprocess.check_output(["date"])
        start_t = start_t.decode('utf-8').replace("\n", "")

        return cont_id, start_t

    # Raise an exception if docker run fails
    except subprocess.CalledProcessError as error :
        print(error)
        exit(1)
    except docker.errors.NullResource as error :
        print('Docker error: Resource ID was not provided')
        exit(1)
    except OSError as error :
        print(error)
        exit(1)


def build_cont_obj(cont, start_t, cconfig, permissions) :
    """
    TODO
    """

    # retrieve container image
    img = cont.image
    img_id = img.short_id[7:]

    cont = Container(cont.short_id, img_id, cont.name, start_t, cont.status, cconfig, permissions)
    return cont

