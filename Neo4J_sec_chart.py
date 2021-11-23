from dockerfile_parser import build_Dockerfile
from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def insert_into_neo4j(cont, infra):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")

    with driver.session() as session:

        # Create Infrastructure node


        # Create Permissions node


        # Create Container node
        node_id = session.write_transaction(create_node_tx, cont, infra)

    driver.close()


def create_node_tx(tx, cont, infra):
    
    result = tx.run(f"CREATE (myCont2:Container)  "
                    "SET myCont2.id = {cont.ID}")
                    
    record = result.single()


def generate_Neo4J_sec_chart(cont, infra) :
    insert_into_neo4j(cont, infra)


"""

CREATE (cont_id:Container {name: 'CAZZONESO'})
CREATE (id_fields:ContainerFields {name: 'CAZZONESO'})
CREATE (default_perm:Permissions {name: 'CAZZONESO'})
CREATE (node_0:Infrastructure {name: 'CAZZONESO'})


(cont_id)-[:HAS]->(id_fields),
(cont_id)-[:CAN]->(default_perm),
(cont_id)-[:RUN_ON_TOP]->(node_00),



To avoid replicate (permissions) nodes, we can create common nodes that reflect the main 3 configurations:
    1. Docker default capabilities
    2. --cap-add=ALL & --privileged
    3. --cap-drop=ALL

and connect every container to the corresponding node.

"""