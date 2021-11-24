from container_builder import build_Container
from infrastructure_parser import get_Infrastructure
from permission_taxonomy import create_Permissions
from XML_sec_chart import generate_XML_chart
from Neo4J_sec_chart import generate_Neo4J_sec_chart
import argparse


parser = argparse.ArgumentParser(description="ContainerGraph - A tool to generate security charts (in XML and Neo4J) and detect drift of Docker containers.")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--add", metavar="<container_id>", help="add a new container")
group.add_argument("--kill", metavar="<container_id>", help="kill a running container")
group.add_argument("--list", action="store_true", help="list current containers")
group.add_argument("--remove", metavar="<container_id>", help="remove an existing container")
group.add_argument("--removeall", action="store_true", help="remove all containers")
group.add_argument("--run", action='append', nargs=argparse.REMAINDER, help="run a new container")

args = parser.parse_args()


def add_container(container_id) :
    
    cont = build_Container(container_id)

    # Retrieve the underlying infrastructure
    infra = get_Infrastructure()

    # Generate Security Charts
    generate_XML_chart(cont, infra)
    #generate_Neo4J_sec_chart(cont, infra)

    print("Added the container with ID " + container_id)


def kill_container(container_id) :

    # Check the container exists and is running

    # Kill the container

    print("kill_TODO")


def list_containers() :

    # Connect to Neo4J and retrieve a list of containers

    print("list_TODO")


def remove_container(container_id) :

    # Remove a container from Neo4j and delete the corresponding XML chart file

    print("remove_TODO")


def remove_all() :

    # Delete all XML and Neo4j charts
    # (does not remove running containers)

    print("remove_all_TODO")


def run_container(options) :
    print(options)
    print("run_TODO")


def main() :

    if args.add :
        add_container(args.add)
    
    elif args.kill :
        kill_container(args.kill)

    elif args.list :
        list_containers()

    elif args.remove :
        remove_container(args.remove)

    elif args.removeall :
        remove_all()

    elif args.run :
        run_container(args.run)


if __name__ == "__main__" :

    main()



# Container Linux Capabilities
"""
We need to decide a granularity for this.

Linux Capabilities 
 - how to trace capabilities: https://stackoverflow.com/questions/35469038/how-to-find-out-what-linux-capabilities-a-process-requires-to-work/47991611#47991611)
 - bcc capable tool: https://www.brendangregg.com/blog/2016-10-01/linux-bcc-security-capabilities.html
 - Docker default capabilities: https://github.com/moby/moby/blob/master/oci/caps/defaults.go#L6-L19

Linux System Calls (which system calls are allowed and which not)

Difference between --cap-add=ALL and --privileged
https://stackoverflow.com/questions/66635237/difference-between-privileged-and-cap-add-all-in-docker
"""

# Run a container
"""
Network type: "type": ["bridge", "host", "overlay", "macvlan"]

Same as for the Dockerfile, also at this step we can alert
for dangerous parameters (e.g. privileged).

 - Eventually change/update the Permissions class of the Container object
 - Update security charts based on docker run parameters

From now on, we need to continuosly check if the container is alive.
    Option: https://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python

Get the container PID:
    $ docker run ... > /dev/null& --> gives us the container PID? TO CHECK

    $ docker inspect -f '{{.State.Pid}}' <container id>
     - using cgroups systemd-cgls
     - child process of containerd-shim (pgrep containerd-shim, pgrep -P)
    https://stackoverflow.com/questions/34878808/finding-docker-container-processes-from-host-point-of-view
"""

### Entering eBPF ###

# 6. MONITOR container drift
"""
 - eBPF monitors [only] container events
"""

# 7. PREVENT container drift
"""
 - MAC and SELinux
 - Network Policies
"""

