from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def neo4j_list_containers():

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:

        # Query for all existing containers
        result = session.read_transaction(print_containers)

    driver.close()
    exit(0)


def print_containers(tx) :
    result =  tx.run("MATCH (Container:Docker) RETURN Container.name AS IMAGE_ID")
    cont_list = result.data("IMAGE_ID")

    if cont_list :
        print(cont_list)
    else : 
        print("No containers found! Use --add to add one. Exiting...")
