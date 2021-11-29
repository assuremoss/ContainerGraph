from XML_sec_chart import update_XML_chart
from container_builder import already_existing, build_Container
from Neo4J_sec_chart import add_node_property
import docker
import os


"""

    --network="bridge, none, host"
        --network container:<name|id> (--network=container:<name|id>)
        --network="<network-name>|<network-id>"

    --security-opt
        --security-opt="label=user:USER"
        --security-opt="label=role:ROLE"
        --security-opt="label=type:TYPE"
        --security-opt="label=level:LEVEL"
        --security-opt="label=disable"
        --security-opt="apparmor=PROFILE"
        --security-opt="no-new-privileges:true"
        --security-opt="seccomp=unconfined"
        --security-opt="seccomp=profile.json"
    --
    --
    -u="", --user=""
    --userns
    -v, --volume
    --volumes-from

"""


def cap_add_op(capabilities) : 
    print(capabilities)
def cap_drop_op(capabilities) : 
    print(capabilities)


def cpus_op(n) : print("MAYBE")
def device_op(dev) : print("MAYBE")


def env_op(env) : print("TODO")
def expose_op(expo) : print("TODO")


def memory_op(mem) : print("MAYBE")


def mount_op(mount) : print("TODO")
def network_op() : print("TODO")
def all_p_op() : print("TODO")
def port_op() : print("TODO")
def pid_op() : print("TODO")
def privileged_op() : print("TODO")
def publish_op() : print("TODO")
def readonly_op() : print("TODO")
def security_opt_op() : print("TODO")
def user_op() : print("TODO")
def tmpfs_op() : print("TODO")
def userns_op() : print("TODO")
def volume_op() : print("TODO")
def volumesfrom_op() : print("TODO")


def parse_docker_option(options, i) :

    # Check for dashes and strip them
    option = options[i].strip('-')
    # If '=' in the string, split the string
    if '=' in option : 
        option = option.split('=')[0]

    switcher = {
        "cap-add": cap_add_op,
        "cap-drop": cap_drop_op,
        "c": cpus_op,
        "cpus": cpus_op,
        "device": device_op,
        # --dns
        "e": env_op,
        "env": env_op,
        "expose": expose_op,
        "m": memory_op,
        "memory": memory_op,
        "mount": mount_op,
        "network": network_op,
        "P": all_p_op,
        "p": port_op,
        "pid": pid_op,
        "privileged": privileged_op,
        "publish": publish_op,
        "readonly": readonly_op,
        "securityopt": security_opt_op,
        "u": user_op,
        "user": user_op,
        "userns": userns_op,
        "tmpfs": tmpfs_op,
        "v": volume_op,
        "volume": volume_op,
        "volumesfrom": volumesfrom_op,
    }
    func = switcher.get(option)

    option = options[i].strip('-')
    
    # Case 1: only --option, no value
    if func and option == 'privileged' or option == 'readonly' :
        func() 
    # Case 2: --option=value
    elif func and '=' in option : 
        value = option.split('=')[1]

        # TODO
        # eventually strip =, "", [], etc.

        func(value)
    # Case 3: --option value
    elif func : 
        value = options[i+1]

        # TODO
        # eventually strip =, "", [], etc.

        func(value)


def update_container_info(cont_id) :

    # Connect to the Docker daemon
    client = docker.from_env()
    cont = client.containers.get(cont_id)

    # Container Info
    img_id = cont.image.id[7:19]
    name = cont.name
    status = cont.status

    if not already_existing(img_id) :
        build_Container(img_id)

    # Update the XML Security Chart
    update_XML_chart(img_id, "name", name)
    update_XML_chart(img_id, "status", status)
    update_XML_chart(img_id, "cont_id", cont_id)

    # Update the Neo4J Security Chart
    add_node_property()




# Run the container using the Docker API
def docker_run(options) :
            
    # TESTING: 
    # - python main.py --run --rm -d -it ea335eea17ab
    # - python main.py --run -d --env mysecret='MY_SECRET' --mount source=my-vol,target=$HOME --privileged ea335eea17ab
    
    try:
        # Run the container
        options_str = ' '.join([str(c) for c in options[0]])
        # stream = os.popen('docker run ' + options_str)

        # TODO
        # Check if the run was successful and then parse the options
        # Test with detach and without

        # output = stream.read()
        # Store the container id
        # container_id = output[:12]

        # TESTING #
        container_id = "9c663759aba2b4ca6a3a8e95ebb4f8a11e79f8a71c5936430b22c2b6ccac05e4"

        print(container_id)
        update_container_info(container_id[:12])

        # Parse Docker run Options and update the charts
        for i, o in enumerate(options[0]) :
            parse_docker_option(options[0], i)

    # TODO
    # Check and extend exceptions

    except docker.errors.NullResource as e:
        print(e)
        exit(1)


def run_container(options) :
    
    # Run the Docker container
    docker_run(options)


