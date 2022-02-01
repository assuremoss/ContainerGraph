from build_image import img_already_existing, build_one_image
from build_infrastructure import get_Infrastructure
from build_XML import image_XML_chart
from build_GraphML import generate_GraphML_chart
from build_Neo4J import generate_Neo4J_chart
import argparse


parser = argparse.ArgumentParser(description="ContainerGraph - A tool to generate security charts (in XML and Neo4J) and detect drift of Docker containers.")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--add", metavar="<image_id>", help="add a new image")
group.add_argument("--can-i", metavar="<image_id | container_id>", help="list image | container permissions")
group.add_argument("--list-images", action="store_true", help="list added images")
# group.add_argument("--list-containers", action="store_true", help="list added containers")
group.add_argument("--remove-image", metavar="<image_id>", help="remove an existing image")
group.add_argument("--remove-all-images", action="store_true", help="remove all images")
group.add_argument("--run", action='append', nargs=argparse.REMAINDER, help="run a container")

args = parser.parse_args()


### COMMENTING CODE ###
#
# https://pandas.pydata.org/docs/development/contributing_docstring.html
# https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
#
#######################


def add_option(img_id) :
    
    if img_already_existing(img_id) :
        print("The image with ID " + img_id + " already exists! Exiting...")
        exit(0)

    # Build the Container Image
    img = build_one_image(img_id)
    # As an alternative, img_id can also be a list of IDs
    
    # Retrieve the underlying infrastructure
    infra = get_Infrastructure(img_id)

    # Generate Security Charts
    image_XML_chart(img, infra)
    generate_GraphML_chart(img, infra)
    generate_Neo4J_chart(img.img_id)

    print("Successfully added the image with ID " + img_id)


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