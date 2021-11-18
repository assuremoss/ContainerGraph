from dockerfile_parser import build_Dockerfile
from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def insert_into_neo4j(my_container, my_host):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")

    with driver.session() as session:
        node_id = session.write_transaction(create_node_tx, "Back-end") # CONTAINER_NAME
        print(node_id)

    driver.close()


def insert_Container(my_container) :

    # TODO 
    # Image, config.json, ...
    
    insert_Dockerfile(my_container)


def insert_Dockerfile(my_container) :
    print("TODO")


def insert_Infra_Node(my_host) :
    print("TODO")







def create_node_tx(tx, name):
    result = tx.run("CREATE (myCont2:Container)  "
                    "SET myCont2.name = $name ", name=name)
                    
    record = result.single()



if __name__ == "__main__":

    # Get Dockerfile
    # LATER IT WILL BE THE ALL CONTAINER, NOT ONLY THE DOCKERFILE
    # my_container = get_Container()
    my_container = build_Dockerfile() 

    # Retrieve infrastructure info
    #my_host = get_infrastructure("Vagrant")

    # Insert data into Neo4J
    insert_into_neo4j(my_container, my_host)







"""
Create a new Container

CREATE (myCont:Container {name: 'Front-end'})

CREATE (Dockerfile:Dockerfile {name: 'Dockerfile'})
CREATE (OCIim:OCIim {name: 'OCI image bundle', path: '/some/folder'})

CREATE (FROM:field {name: 'FROM', value:'node:12-alpine'})
CREATE (ENV:field {name: 'ENV', value:'JAVA_VERSION=8u72'})
CREATE (CMD:field {name: 'CMD', value: '["node", "src/index.js"]'})
CREATE (USER:field {name: 'USER', value: 'root'})
CREATE (EXPOSE:field {name: 'EXPOSE', value: '3000/tcp'})

CREATE (configJson:configF {name: 'config.json'})
CREATE (rootfs:rootfs {name: 'rootfs'})

CREATE
(myCont)-[:CONTAINS]->(Dockerfile),
(myCont)-[:CONTAINS]->(OCIim),
(OCIim)-[:CONTAINS]->(configJson),
(OCIim)-[:CONTAINS]->(rootfs),
(Dockerfile)-[:HAS]->(FROM),
(Dockerfile)-[:HAS]->(ENV),
(Dockerfile)-[:HAS]->(CMD),
(Dockerfile)-[:HAS]->(USER),
(Dockerfile)-[:HAS]->(EXPOSE)

"""

"""
Query examples

i) getting all the nodes
MATCH (n) RETURN n

ii) getting container running as root
MATCH (c)-[:CONTAINS]->(d)-[:HAS]-(f) WHERE f.value = 'root' RETURN c,d,f;

iii) getting a container with open port 3000
MATCH (c)-[:CONTAINS]->(d)-[:HAS]-(f) WHERE f.value = 3000 RETURN c,d,f;

MATCH (c)-[:CONTAINS]->(r)-[:RUNTIME]->(p)-[:PORT]->(f) RETURN c,r,p,f;



- delete everything: MATCH (n) DETACH DELETE n

"""
