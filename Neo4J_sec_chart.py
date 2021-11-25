from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def insert_into_neo4j(cont, infra):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:

        session.write_transaction(create_cont_node, cont)
        session.write_transaction(create_fields_node, cont)

        # Check if perm node already exists 
        if not session.read_transaction(default_perm_exist) : 
            session.write_transaction(create_perm_node, cont)

        # Check if infra node already exists
        if not session.read_transaction(infra_exist, infra) : 
            session.write_transaction(create_infra_node, infra)

        # Create relationships
        session.write_transaction(create_relationships, cont, infra)

    driver.close()


def create_cont_node(tx, cont) :

    # TODO
    # Add $name
    # Add $filesystem

    tx.run("CREATE (c:Container:Docker {name: $id, start_t: 0, stop_t: 0})", id=cont.ID)


def create_fields_node(tx, cont) :

    # TODO
    # Add $base_image

    id_fields = cont.ID + "_fields"
    tx.run("CREATE (f:ContainerFields {name: $id_fields, user: $user, env: $env, volume: $volume, net_adapt_type: 'bridge', expose: $expose, entrypoint: $entrypoint, cmd: $cmd})", id_fields=id_fields, user=cont.Dockerfile.USER, env=cont.Dockerfile.ENV, volume=cont.Dockerfile.VOLUME, expose=cont.Dockerfile.EXPOSE, entrypoint=cont.Dockerfile.ENTRYPOINT, cmd=cont.Dockerfile.CMD)


def create_infra_node(tx, infra) :
    tx.run("CREATE (i:Infrastructure:Host {name: $hostname, docker_v: $docker_v, os: $os, kernel_v: $kernel_v, cpus: $cpus, mem: $mem, registry: $registry})", hostname=infra.hostname, docker_v=infra.docker_v, os=infra.os, kernel_v=infra.kernel_v, cpus=infra.cpus, mem=infra.mem, registry=infra.registry)


def create_perm_node(tx, cont) :

    files_p = ', '.join(cont.permissions.files)
    network_p = ', '.join(cont.permissions.network)
    processes_p = ', '.join(cont.permissions.processes)
    adminop_p = ', '.join(cont.permissions.adminop)

    tx.run("CREATE (p:Permissions:DefaultP {name: 'default_perm', files: $files_p, network: $network_p, processes: $processes_p, adminop: $adminop_p})", files_p=files_p, network_p=network_p, processes_p=processes_p, adminop_p=adminop_p)


def infra_exist(tx, infra) : 
    result = tx.run("MATCH (i:Infrastructure:Host {name: $hostname}) RETURN count(i) > 0 AS i", hostname=infra.hostname)
    return result.data('i')[0]['i']


def default_perm_exist(tx) :
    result = tx.run("MATCH (p:Permissions:DefaultP {name: 'default_perm'}) RETURN count(p) > 0 AS p")
    return result.data('p')[0]['p']


def create_relationships(tx, cont, infra):

    id_fields = cont.ID + "_fields"

    tx.run("MATCH (c:Container:Docker {name: $id}) "
           "MATCH (f:ContainerFields {name: $id_fields}) "
           "CREATE (c)-[:HAS]->(f) "
           "UNION "
           "MATCH (c:Container:Docker {name: $id}) "
           "MATCH (p:Permissions:DefaultP {name: 'default_perm'}) "
           "CREATE (c)-[:CAN]->(p) "
           "UNION "
           "MATCH (c:Container:Docker {name: $id}) "
           "MATCH (i:Infrastructure:Host {name: $hostname})"
           "CREATE (c)-[:RUNS_ON_TOP]->(i)",
           id=cont.ID, id_fields=id_fields, hostname=infra.hostname)


def generate_Neo4J_sec_chart(cont, infra) :

    insert_into_neo4j(cont, infra)




"""

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