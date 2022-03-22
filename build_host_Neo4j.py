from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def host_node(NEO4J_ADDRESS, host) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    
    with driver.session() as session:

        session.write_transaction(create_host_node, host)
        session.write_transaction(create_host_relationship, host)

    driver.close()


def create_host_node(tx, host) :
    """
    TODO
    """

    query = "MERGE (h:Host:" + host.host.name + " {name: $hostname, processor: $processor, cpus: $cpus, mem: $mem})"
    tx.run(query, hostname = host.host.hostname, processor = host.host.processor, cpus = host.host.cpus, mem = host.host.mem)

    ### CREATE 5 VERSIONS NODES ###
    query = "MERGE (k:Kernel:" + host.host.h_platform + ":Version {name: $kernel_v, kernel_v: $kernel_v})"
    tx.run(query, kernel_v = host.host.kernel_v)
    ###

    if host.name == "DockerEngine" :

        query = "MERGE (ce:ContainerEngine:" + host.name + " {name: $name, containerd_v: $containerd_v, runc_v: $runc_v, storage: $storage, registry: $registry})"
        tx.run(query, name = host.name, containerd_v = host.containerd_v, runc_v = host.runc_v, storage = host.storage, registry = host.registry)

        ### CREATE 5 VERSIONS NODES ###
        query = "MERGE (de:Engine:" + host.name + ":Version {name: $docker_v, docker_v: $docker_v})"
        tx.run(query, docker_v = host.docker_v)
        ###


def create_host_relationship(tx, host) :
    """
    TODO
    """

    tx.run("MATCH (h:Host {name: $hostname}) "
           "MATCH (k:Kernel {kernel_v: $kernel_v}) "
           "MERGE (h)-[:USES]->(k) "
           "UNION "
           "MATCH (k:Kernel {kernel_v: $kernel_v}) "
           "MATCH (ce:ContainerEngine {name: $name}) "
           "MERGE (ce)-[:RUNS_ON_TOP]->(k) "
           , hostname = host.host.hostname, kernel_v = host.host.kernel_v, name = host.name
    )

    if host.name == "DockerEngine" :
        tx.run("MATCH (ce:ContainerEngine {name: $name}) "
               "MATCH (de:DockerEngine {docker_v: $docker_v}) "
               "MERGE (ce)-[:USES]->(de) "
               , name = host.name, docker_v = host.docker_v
        )


def host_Neo4j(NEO4J_ADDRESS, host) :
    """
    TODO
    """

    # host.print_docker_host()

    # Create Host and Container Engine nodes
    host_node(NEO4J_ADDRESS, host)