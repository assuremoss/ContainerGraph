from build_image import build_image, retrieve_img_id
from build_container import build_container
from build_infrastructure import get_Infrastructure
from build_cont_Neo4j import cont_already_existing, cont_Neo4j_chart
from build_img_Neo4j import img_already_existing, image_Neo4j_chart
from remove_all import data_remove_all
from analyze import analyze_cont
import argparse


parser = argparse.ArgumentParser(description="ContainerGraph - A tool to generate security charts (in XML and Neo4J) and detect drift of Docker containers.")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--add", metavar="<image_id>", help="add a new image")
group.add_argument("--run", action='append', nargs=argparse.REMAINDER, help="run a container")
# group.add_argument("--restart", action='append', nargs=argparse.REMAINDER, help="restart a container")
group.add_argument("--analyze", metavar="<container_id>", help="analyze container's vulnerabilities/misconfiguration")
group.add_argument("--remove-all", action="store_true", help="remove all running containers and clean Neo4J graph")

args = parser.parse_args()


# Add a container image
def add_option(img_id) :
    """
    TODO
    """

    img_id = retrieve_img_id(img_id)
    
    if img_already_existing(img_id) :
        print("The image with ID " + img_id + " already exists!")

    else :
        # Build the Container Image
        img = build_image(img_id)
        img_id = img.img_id
        
        # Retrieve the underlying infrastructure
        infra = get_Infrastructure(img_id)

        # Generate Image Security Charts
        # image_XML_chart(img, infra)
        # image_GraphML_chart(img, infra)
        image_Neo4j_chart(img, infra)

        print("Successfully added the image with ID " + img_id)


# Run a new container
def run_option(options) :

    # Build the Container 
    cont = build_container(options)

    # Update Security Charts
    if not cont_already_existing(cont.cont_id) :
        
        # eventually add the container image
        add_option(cont.img_id)
        
        infra = get_Infrastructure(cont.img_id)
        cont_Neo4j_chart(cont, infra) 

        print("Successfully added the container with ID " + cont.cont_id)

    else :
        print("The container with ID " + cont.cont_id + " already exists! Exiting...")
        exit(0)


# Analyze the container's vulnerabilities/misconfigurations
def analyze_option(cont_id) :
    analyze_cont(cont_id)


def remove_all_option() :
    data_remove_all()
    print("Everything was cleaned up!")


# Remove all containers and clean up Neo4J
def main() :

    if args.add :
        add_option(args.add)

    elif args.run :
        run_option(args.run)

    elif args.analyze :
        analyze_option(args.analyze)

    elif args.remove_all :
        remove_all_option()


if __name__ == "__main__" :

    main()

