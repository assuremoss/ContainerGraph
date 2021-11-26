from neo4j import GraphDatabase

# Storing permissions as strings instead of single properties in the permission node.
"""
https://stackoverflow.com/questions/41714434/neo4j-storing-multiple-values-as-property-and-matching-nodes-based-on-that-prope
"""


def connect_to_neo4j(uri, user, password) :
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def generate_Neo4J_sec_chart(cont, infra) :

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

    tx.run("CREATE (c:Container:Docker {name: $id, status: $status, start_t: 0, stop_t: 0})", id=cont.ID, status=cont.status)


def create_fields_node(tx, cont) :

    # TODO
    # Add $base_image

    id_fields = cont.ID + "_fields"
    tx.run("CREATE (f:ContainerFields {name: $id_fields, user: $user, env: $env, volume: $volume, net_adapt_type: 'bridge', expose: $expose, entrypoint: $entrypoint, cmd: $cmd})", id_fields=id_fields, user=cont.Dockerfile.USER, env=cont.Dockerfile.ENV, volume=cont.Dockerfile.VOLUME, expose=cont.Dockerfile.EXPOSE, entrypoint=cont.Dockerfile.ENTRYPOINT, cmd=cont.Dockerfile.CMD)


def create_infra_node(tx, infra) :
    tx.run("CREATE (i:Infrastructure:Host {name: $hostname, docker_v: $docker_v, os: $os, kernel_v: $kernel_v, cpus: $cpus, mem: $mem, registry: $registry})", hostname=infra.hostname, docker_v=infra.docker_v, os=infra.os, kernel_v=infra.kernel_v, cpus=infra.cpus, mem=infra.mem, registry=infra.registry)


def create_perm_node(tx, cont) :

    tx.run("CREATE (p:Permissions:DefaultP {name: 'default_perm', files: $files_p, network: $network_p, processes: $processes_p, adminop: $adminop_p})", files_p=cont.permissions.files, network_p=cont.permissions.network, processes_p=cont.permissions.processes, adminop_p=cont.permissions.adminop)


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

