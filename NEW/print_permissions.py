from neo4j import GraphDatabase
import json


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def print_cont_permissions(id):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    
    with driver.session() as session:
        session.read_transaction(retrieve_container, id)
    
    driver.close()


def retrieve_container(tx, id) :
    result =  tx.run("MATCH (c:Container:Docker)-[:CAN]->(p:Permissions) WHERE c.cont_id = $id RETURN p", id=id)
    cont_perm = result.data("p")

    if cont_perm : 
        print(json.dumps(cont_perm[0]['p'], indent=1, sort_keys=True))
    else : 
        print("No containers found! Use --add to add one. Exiting...")

