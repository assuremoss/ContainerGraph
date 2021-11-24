from dockerfile_parser import build_Dockerfile
from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def insert_into_neo4j(cont, infra):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")

    with driver.session() as session:

        # Create Infrastructure node
        ### TODO ### CHECK IF ALREADY EXISTING
        infra_id = session.write_transaction(create_node_tx, infra, "infra")

        # Create Container node
        node_id = session.write_transaction(create_node_tx, cont, "container")

        print(node_id)

    driver.close()


def create_node_tx(tx, node, node_type):
    
    aux = "CREATE (i:node_0:Infrastructure:Host {name: 'node_0', docker_v: '', OS: '', kernel_v: '', CPUs: '', Mem: '', Registry: ''})"

    if node_type == "container" :
        aux = "CREATE (c:Container:Docker {name: '" + node.ID + "', start_t: 00, stop_t: 00}) \
               CREATE (f:ContainerFields {name: '" + node.ID + "_fields', user: '" + node.Dockerfile.USER + "', env: '" + node.Dockerfile.ENV + "', volume: '', net_config: ['', '']}) \
               CREATE (p:Permissions:DefaultP {name: 'default_perm', files: 'read, write', network: 'connection', processes: 'new_process', adminop: 'apt, chmod, adduser, mount'})"
        ### TODO ### CHECK IF PERMISSIONS ALREADY EXIST

    result = tx.run(aux)
                    
    print(result.single())

    record = result.single()[0]
    return record


def generate_Neo4J_sec_chart(cont, infra) :

    insert_into_neo4j(cont, infra)




"""

### NODES ###

CREATE (c:Container:Docker {name: 'ea335eea17ab', start_t: 0, stop_t: 0})

CREATE (f:ContainerFields {name: 'ea335eea17ab_fields', user: 'root', env: 'JAVA_VERSION=2.0', volume: '', net_config: ['bridge', '80']})

CREATE (p:Permissions:DefaultP {name: 'default_perm', files: 'read, write, execute', network: 'connection', processes: 'new_process, kill_process', adminop: 'adduser, apt, chmod, mount'})

CREATE (i:Infrastructure:Host:node_0 {name: 'node_0', docker_v: '20.10.8', OS: 'Docker Desktop linux', kernel_v: ' 5.10.47-linuxkit', CPUs: '8', Mem: '2GB', Registry: 'https://index.docker.io/v1/'})


### RELATIONSHIPS ###

MATCH c = (Container:Docker {name: 'ea335eea17ab'})


MATCH (c:Container:Docker {name: 'ea335eea17ab'})
MATCH (f:ContainerFields {name: 'ea335eea17ab_fields'})
CREATE (c)-[:HAS]->(f)
UNION
MATCH (c:Container:Docker {name: 'ea335eea17ab'})
MATCH (p:Permissions:DefaultP {name: 'default_perm'})
CREATE (c)-[:CAN]->(p)
UNION
MATCH (c:Container:Docker {name: 'ea335eea17ab'})
MATCH (i:Infrastructure:Host:node_0 {name: 'node_0'})
CREATE (c)-[:RUNS_ON_TOP]->(i)


### 2 MORE CONTAINERS ###

CREATE (c:Container:Docker {name: 'cont_id0', start_t: 123, stop_t: -1})

CREATE (f:ContainerFields {name: 'id0_fields', user: '', env: '', volume: '', net_config: ['', '']})

Now create new relationships.



### QUERIES ###

 - Return everything:
MATCH p = (a)-[r]->(b)
RETURN *

 - Return all relationships of a container:
MATCH (c:Container:Docker {name: 'ea335eea17ab'})-[r]->(b)
RETURN r, c, b

 - How much does it cost to store a container
    > 4 nodes, 2 may be in common [2 (container + fields) + 1 (permissions - may be in common) + 1 (infra - may be in common)]
    > 3 relationships
    > 20 labels

 - Does the container have write/connection/mount permission?
MATCH (c:Container:Docker {name: 'cont_id'})-[:CAN]->(p:Permissions:DefaultP {network: 'connection'})
RETURN count(c) > 0 as c


### EXAMPLES ###

 - Delete everything
    match (a) -[r] -> () delete a, r
    match (a) delete a

Attaching: 
    MATCH (p:Person {name: 'Tom Hanks'})
    CREATE (m:Movie {title: 'Cloud Atlas', released: 2012})
    CREATE (p)-[r:ACTED_IN {roles: ['Zachry']}]->(m)
    RETURN p, r, m



Alternative with lists as fields: network: ['', '', '']

Example:

CREATE ()-[:ACTED_IN {roles: ['Forrest'], performance: 5}]->()

CREATE (a:Person {name: 'Jane', age: 20})
WITH a
MATCH (p:Person {name: 'Jane'})
SET p = {name: 'Ellen', livesIn: 'London'}
RETURN p.name, p.age, p.livesIn



"""