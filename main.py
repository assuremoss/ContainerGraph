from build_image import build_image, retrieve_img_id
from build_container import build_container
from build_cont_Neo4j import cont_Neo4j_chart
from build_img_Neo4j import image_Neo4j_chart
from remove_all import data_remove_all, remove_container
from analyze import analyze_cont
from initialize_Neo4J import initialize_Neo4j_db
import argparse
import os


parser = argparse.ArgumentParser(description="ContainerGraph - A tool to generate security charts (in XML and Neo4J) and detect drift of Docker containers.")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--add", metavar="<image_id>", help="add a new image")
group.add_argument("--run", action='append', nargs=argparse.REMAINDER, help="run a container")
# group.add_argument("--restart", action='append', nargs=argparse.REMAINDER, help="restart a container")
group.add_argument("--remove", metavar="<container_id>", help="remove and delete a container")
group.add_argument("--analyze", metavar="<container_id>", help="analyze container's vulnerabilities/misconfiguration")
group.add_argument("--remove-all", action="store_true", help="remove all running containers and clean Neo4J graph")

args = parser.parse_args()


# Define Neo4J Default address
NEO4J_ADDRESS = "localhost"


# Add a container image
def add_option(img_id, NEO4J_ADDRESS) :
    
    # Standardize the Image ID lenght to 7 chars.
    img_id = retrieve_img_id(img_id)
    
    # Build the Container Image
    img = build_image(img_id)

    # Generate Image Security Charts
    image_Neo4j_chart(NEO4J_ADDRESS, img)

    print("Successfully added the image with ID " + img_id)


# Run a new container
def run_option(options, NEO4J_ADDRESS) :

    # Build the Container 
    cont = build_container(options)

    # Eventually add the container image
    add_option(cont.img_id, NEO4J_ADDRESS)
    
    cont_Neo4j_chart(NEO4J_ADDRESS, cont) 

    print("Successfully added the container with ID " + cont.cont_id)


# Analyze the container's vulnerabilities/misconfigurations
def analyze_option(cont_id, NEO4J_ADDRESS) :
    analyze_cont(cont_id)

# Remove the specified container
def remove_option(cont_id, NEO4J_ADDRESS) :
    remove_container(NEO4J_ADDRESS, cont_id)

# Remove all containers and clean up Neo4J
def remove_all_option(NEO4J_ADDRESS) :
    data_remove_all(NEO4J_ADDRESS)
    print("Everything was cleaned up!")


def main() :

    if 'NEO4J_ADDRESS' in os.environ:
        global NEO4J_ADDRESS
        NEO4J_ADDRESS = os.environ.get('NEO4J_ADDRESS')

    initialize_Neo4j_db(NEO4J_ADDRESS)

    if args.add :
        add_option(args.add, NEO4J_ADDRESS)

    elif args.run :
        run_option(args.run, NEO4J_ADDRESS)

    elif args.analyze :
        analyze_option(args.analyze, NEO4J_ADDRESS)

    elif args.remove :
        remove_option(args.remove, NEO4J_ADDRESS)

    elif args.remove_all :
        remove_all_option(NEO4J_ADDRESS)


if __name__ == "__main__" :

    main()

