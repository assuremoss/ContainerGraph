from dockerfile_parser import build_Dockerfile
from permission_taxonomy import create_Permissions
import docker
import os.path


class Container:

    def __init__(self, ID, Dockerfile, fs, permissions):
        self.ID = ID
        self.Dockerfile = Dockerfile # other Class
        self.fs = fs # uri
        self.permissions = permissions # other Class


# Connect to the Docker daemon
client = docker.from_env()


# Ask the user to provide an image ID
def get_Image(img_id):

    try:
        image = client.images.get(img_id)
        return image

    # Raise an exception if the image doesn't exist
    except docker.errors.ImageNotFound :
        print("Image not found! Exiting...")
        exit(1)
    except docker.errors.APIError :
        print("Image not found! Exiting...")
        exit(1)


def reconstruct_Dockerfile(img_hst) :

    # Create a Dockerfile file
    f = open("Dockerfile", "w+")

    # Iterate over the image commands and save them into the file
    for cmd in reversed(img_hst) :

        field = cmd.get("CreatedBy")
        if field != None : f.write(field[18:].lstrip() + "\n")
    
    # Close the file
    f.close()


# Check whether the new container already exist
def already_existing(img_id) :
    chart_uri = 'charts/' + img_id + '_chart.xml'
    return os.path.exists(chart_uri)


def build_Container(img_id):

    if already_existing(img_id) :
        print("The image with ID " + img_id + " already exists! Exiting...")
        exit(0)

    # Get image
    img = get_Image(img_id)
    
    try:

        # Build Dockerfile
        img_hst = img.history()

        # Reconstruct the Dockerfile and save it to disk
        reconstruct_Dockerfile(img_hst)

        # Parse Dockerfile
        df = build_Dockerfile()
        # print(df.EXPOSE)

        # Add container filesystem location
        fs = "/"

        # Add container's permissions
        # Before docker run, we grant the docker default capabilities
        perm = create_Permissions()

        # Build the container
        aux = Container(img_id, df, fs, perm)
        return aux

    except docker.errors.APIError :
        print("Error while retrieving the image history! Exiting...")
        exit(1)

