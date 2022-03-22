

class ContainerConfig :
    """
    TODO
    """

    def __init__(self, fields) :
        self.fields = fields

    def print_cconfig(self) :
        print(self.fields)


def build_config(run_args) :
    """
    TODO
    """

    # Overriding Dockerfile image defaults
    # Four of the Dockerfile commands cannot be overridden at runtime: FROM, MAINTAINER, RUN, and ADD. 
    # Everything else has a corresponding override in docker run.
    fields = {'user': 'root', 'memory': 'unlimited', 'cpus': 'unlimited'}

    # parse docker run arguments and check for permissions parameters
    for i in range(len(run_args)) :

        arg = run_args[i]

        ### REFERENCES ###
        # https://docs.docker.com/engine/reference/commandline/run/
        # https://docs.docker.com/engine/reference/run/#pid-settings---pid
        ###

        # TODO: parse more arguments

        # Container Name
        if arg.startswith('--name') :
            # Syntax: --name my_container
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            fields['name'] = value

        # Container User
        elif arg.startswith('--u') or arg.startswith('--user') :
            # root (id = 0) is the default user within a container.
            # Syntax: --user UID:GID
            # Syntax: --user newuser
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            fields['user'] = value

        # Container Environment Variables
        elif arg.startswith('-e') or arg.startswith('--env') :
            # Syntax: -e env_name=value
            # Syntax: --env env_name=value
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            if 'env' in fields : fields['env'].append(value)
            else : fields['env'] = [value]

        # Container Volumes
        elif arg.startswith('-v') or arg.startswith('--volume') :
            # Syntax: -v /doesnt/exist:/foo
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')
            
            if 'volumes' in fields : fields['volumes'].append(value)
            else : fields['volumes'] = [value]

        # Container Network
        elif arg.startswith('--network') :
            # Syntax --network=my-net
            # Net types: none, bridge, host, container, custom_network
            value = run_args[i].split('=')[1]

            fields['network'] = value

        # Container Network Ports
        elif arg.startswith('-p') or arg.startswith('--publish') or arg.startswith('--expose') :
            # Syntax: -p ip_address:port:container_port/protocol
            # Example: -p 127.0.0.1:80:8080/tcp
            # This binds port 8080 of the container to TCP port 80 on 127.0.0.1 of the host machine.
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            if 'port' in fields : fields['port'].append(value)
            else : fields['port'] = [value]

        # Container PID Namespace
        elif arg.startswith('--pid') :
            # Syntax: --pid=host
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            fields['pid_ns'] = value

        # Container Kernel Memory Limit
        elif arg.startswith('--kernel-memory') :
            # By limiting kernel memory, you can prevent new processes from 
            # being created when the kernel memory usage is too high.
            # Syntax: --kernel-memory 50M
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            fields['kernel-memory'] = run_args[i+1]

        # Container Memory
        elif arg.startswith('-m') or arg.startswith('--memory') :
            # Syntax: -m 300M
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            fields['memory'] = value

        # Container CPU usage
        elif arg.startswith('--cpus') :
            # Syntax: --cpus=0.000 (0.000 means no limits)
            value = arg.split('=')[1]
            if value == 0.000 : value = 'unlimited'
            
            fields['cpus'] = value

        # Container Device Access
        elif arg.startswith('--device') :
            # Syntax: --device=/dev/snd/...
            if '=' in arg : value = arg.split('=')[1].replace('"', '')
            else : value = run_args[i+1].replace('"', '')

            if 'device' in fields : fields['device'].append(value)
            else : fields['device'] = [value]

    return ContainerConfig(fields)

    