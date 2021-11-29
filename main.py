from container_builder import build_Container, already_existing
from infrastructure_parser import get_Infrastructure
from permission_taxonomy import create_Permissions
from XML_sec_chart import generate_XML_chart
from Neo4J_sec_chart import generate_Neo4J_sec_chart
from list_containers import neo4j_list_containers
from remove_all import data_remove_all
from remove_image import delete_container
from run_container import run_container
from cont_permission import print_cont_permissions
import argparse


parser = argparse.ArgumentParser(description="ContainerGraph - A tool to generate security charts (in XML and Neo4J) and detect drift of Docker containers.")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--add", metavar="<image_id>", help="add a new image")
group.add_argument("--can-i", metavar="<image_id | container_id>", help="list image | container permissions")
group.add_argument("--list", action="store_true", help="list current images and containers")
group.add_argument("--remove-image", metavar="<image_id>", help="remove an existing image and container")
group.add_argument("--remove-all", action="store_true", help="remove all images and containers")
group.add_argument("--run", action='append', nargs=argparse.REMAINDER, help="run a new container")

args = parser.parse_args()


def add_option(img_id) :
    
    # https://dockerlabs.collabnix.com/advanced/security/capabilities/

    if already_existing(img_id) :
        print("The image with ID " + img_id + " already exists! Exiting...")
        exit(0)

    cont = build_Container(img_id)

    # Retrieve the underlying infrastructure
    infra = get_Infrastructure()

    # Generate Security Charts
    generate_XML_chart(cont, infra)
    generate_Neo4J_sec_chart(cont, infra)

    print("Added the image with ID " + img_id)


# Print the container's permissions
def can_i_option(container_id) :
    print_cont_permissions(container_id)

# List existing containers
def list_option() :
    neo4j_list_containers()

# Remove a container from Neo4j and delete the corresponding XML chart file
def remove_img_option(container_id) :
    delete_container(container_id)
    print("The container with id " + container_id + " was successfully removed!")

# Delete all XML and Neo4j charts
# (does not remove running containers)
def remove_all_option() :
    data_remove_all()
    print("Everything was cleaned up!")

# Run a new container
def run_option(options) :
    run_container(options)


def main() :

    if args.add :
        add_option(args.add)
    
    elif args.can_i :
        can_i_option(args.can_i)

    elif args.list :
        list_option()

    elif args.remove_image :
        remove_img_option(args.remove_image)

    elif args.remove_all :
        remove_all_option()

    elif args.run :
        run_option(args.run)


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


### How do we keep track of new changes in the charts? 
### Entering eBPF ###

# 6. MONITOR container drift
"""
 - eBPF monitors [only] container events
 - we can use the Tracee tool from aqua to do this and just change the bpf functions.
"""

# 7. PREVENT container drift
"""
 - MAC and SELinux
 - Network Policies
"""

# 8. ATTACK KILL CHAIN
"""
Define queries that return a possible kill chain based on the current configuration.
"""