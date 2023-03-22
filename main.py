import argparse
from build_image import build_image, retrieve_img_id
from build_container import build_cont
from build_cont_neo4j import cont_Neo4j_chart
from build_img_neo4j import image_Neo4j_chart
from build_host_neo4j import get_kernel_v
from remove_cont import data_remove_all, data_remove_cont, remove_container
from initialize_neo4j import initialize_Neo4j_db, graph_info
from suggest_fix import analyze_all_deployment


parser = argparse.ArgumentParser(description="ContainerGraph - A tool for automatic detection and mitigation of vulnerabilities and misconfigurations for Docker containers.")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--add", metavar="<image_id>", help="add a new image")
group.add_argument("--run", action='append', nargs=argparse.REMAINDER, help="run a container")
group.add_argument("--remove", nargs=1, metavar="<container_id> OR <containers> OR <all>", help="remove and delete one container, all containers, or everything")
group.add_argument('--analyze', action='store_true', help='analyze all vulnerabilities/misconfigurations')

args = parser.parse_args()


# Add a container image
def add_option(img_id) :
    
    # Standardize the Image ID lenght to 7 chars.
    img_id = retrieve_img_id(img_id)
    
    # Build the Container Image
    img = build_image(img_id)

    # Generate Image Security Charts
    image_Neo4j_chart(img)

    # Print graph info
    n_nodes, n_edges = graph_info()
    print("Successfully added the image with ID " + img_id)
    print('Total: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')


# Run a new container
def run_option(options) :

    # Get the current kernel version
    kernel_v = get_kernel_v()

    # Build the Container 
    cont = build_cont(options, kernel_v)

    # Eventually add the container image
    # add_option(cont.img_id)

    cont_Neo4j_chart(cont) 

    # Print graph info
    n_nodes, n_edges = graph_info()
    print("Successfully added the container with ID " + cont.cont_id)
    print('Container: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')


# Analyze all vulnerabilities/misconfigurations
def analyze_option() :
    
    print('Analyzing current Docker deployment...\n')

    analyze_all_deployment()


# Remove container/s and clean DB
def remove_option(option) :
    # Remove everything
    if option[0] == 'all' : 
        data_remove_all()

    # Remove all containers
    elif option[0] == 'containers' :
        data_remove_cont()

    # Remove single container
    else :
        remove_container(option[0])


def main() :

    if args.remove :
        remove_option(args.remove)

    else :
        # First, make sure Neo4j is initialized
        initialize_Neo4j_db()

        if args.add :
            add_option(args.add)

        elif args.run :
            run_option(args.run)

        elif args.analyze :
            analyze_option()


if __name__ == "__main__" :
    main()

