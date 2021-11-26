import docker

# Run a container
"""
Network type: "type": ["bridge", "host", "overlay", "macvlan"]

Same as for the Dockerfile, also at this step we can alert
for dangerous parameters (e.g. privileged).

 - Eventually change/update the Permissions class of the Container object
 - Update security charts based on docker run parameters

Get the container PID:
    $ docker run ... > /dev/null& --> gives us the container PID? TO CHECK

    $ docker inspect -f '{{.State.Pid}}' <container id>
     - using cgroups systemd-cgls
     - child process of containerd-shim (pgrep containerd-shim, pgrep -P)
    https://stackoverflow.com/questions/34878808/finding-docker-container-processes-from-host-point-of-view
"""



# Connect to the Docker daemon
client = docker.from_env()

"""
Docker run Options

[the flags can also be merged, e.g. docker run -dp ...]

Security-wise:
    --cap-add
    --cap-drop
    --dns
    --env
    --expose
    --memory
    --network="bridge, host, container, overlay, macvlan"
    --mount
    --no-healthcheck
    --pid
    --privileged
    --publish
    --read-only
    --security-opt

    https://docs.docker.com/engine/reference/run/#security-configuration

    --user
    --tmpfs
    --userns
    --volume
    --volumes-from


Operational-wise:
    --detach
    --device
    --name
    --rm
    --detach
    -it

"""

# To get the overall container execution time we don't have to start the containerwith the --rm flag. we can run inspect once the container is killed and then remove it by ourself. 

# Run the container using the Docker API
def docker_run(options) :

    try:
        options_list = options[0]
        
        # for o in options_list :
        #     print(o)
        # client.containers.run()


        # TODO
        ### ONLY FOR TESTING ###
        # docker run -d --env mysecret='MY_SECRET' --mount source=my-vol,target=$HOME ea335eea17ab

        # python main.py --run -d --env mysecret='MY_SECRET' --mount source=my-vol,target=$HOME --privileged ea335eea17ab

        aux = client.containers.run("ea335eea17ab", detach=True, privileged=True, environment=["ysecret=MY_SECRET"])

        # Print container id
        print(aux.id)
        #print(aux.image)
        #print(aux.status)


    except docker.errors.ContainerError as e:
        print(e)
        print("Error while running the container! Exiting...")
        exit(1)
    except docker.errors.ImageNotFound as e:
        print(e)
        print("The image does not exist! Add one using the --add option. Exiting...")
        exit(1)
    except docker.errors.APIError as e:
        print(e)
        print("Error from the API Server! Exiting...")
        exit(1)








# Update the XML chart
def update_XML_chart() :
    print("TODO")


# Update the Neo4j chart
def update_Neo4j_chart() :
    print("TODO")


def run_container(options) :
    
    # Run the Docker container
    docker_run(options)

    # Update the XML chart
    #update_XML_chart()

    # Update the Neo4j chart
    #update_Neo4j_chart() 

