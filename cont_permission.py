from neo4j import GraphDatabase
import json


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def print_cont_permissions(container_id):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:

        # Query for all existing containers
        session.read_transaction(retrieve_container, container_id)
    driver.close()


def retrieve_container(tx, container_id) :
    result =  tx.run("MATCH (c:Container:Docker {name: $id})-[:CAN]->(p:Permissions) RETURN p", id=container_id)
    cont_perm = result.data("p")

    if cont_perm : 
        print(json.dumps(cont_perm[0]['p'], indent=1, sort_keys=True))
    else : 
        print("No containers found! Use --add to add one. Exiting...")

