from neo4j import GraphDatabase
import json


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def neo4j_list_containers():

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:

        # Query for all existing containers
        session.read_transaction(print_containers)

    driver.close()


def print_containers(tx) :
    result = tx.run("MATCH (c:Container:Docker) RETURN c.img_id AS Image_ID")

    cont_list = (result.data("Image_ID"))
    # Eventually, print the name and container id as well.

    if cont_list :
        print(json.dumps(cont_list, indent=1))

    else : 
        print("No image or container found! Use --add to add one. Exiting...")

