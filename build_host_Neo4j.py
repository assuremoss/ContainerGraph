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

    if host.name == "DockerEngine" :

        query = "MERGE (ce:ContainerEngine:" + host.name + " {name: $name, storage: $storage, registry: $registry})"
        tx.run(query, name = host.name, storage = host.storage, registry = host.registry)


def create_host_relationship(tx, host) :
    """
    TODO
    """

    kernel_v = host.host.kernel_v[:3]

    tx.run("MATCH (h:Host {name: $hostname}) "
           "MATCH (kv:KernelVersion {key: $kernel_v}) "
           "MERGE (h)-[:USES]->(kv) "
           "UNION "
           "MATCH (h:Host {name: $hostname}) "
           "MATCH (ce:ContainerEngine {name: $name}) "
           "MERGE (ce)-[:RUNS_ON_TOP]->(h) "
           "UNION "
           "MATCH (ce:ContainerEngine {name: $name}) "
           "MATCH (kv:KernelVersion {key: $kernel_v}) "
           "MERGE (ce)-[:USES]->(kv) "
           , hostname = host.host.hostname, kernel_v = kernel_v, name = host.name
    )

    if host.name == "DockerEngine" :

        tx.run("MATCH (ce:ContainerEngine {name: $name}) "
               "MATCH (de:DockerVersion {key: $docker_v}) "
               "MERGE (ce)-[:USES]->(de) "
               "UNION "
               "MATCH (de:DockerVersion {key: $docker_v}) "
               "MATCH (cv:containerdVersion {key: $containerd_v}) "
               "MERGE (de)-[:USES]->(cv) "
               "UNION "
               "MATCH (de:DockerVersion {key: $docker_v}) "
               "MATCH (rv:runcVersion {key: $runc_v}) "
               "MERGE (de)-[:USES]->(rv) "
               , name = host.name, docker_v = host.docker_v, containerd_v = host.containerd_v, runc_v = host.runc_v
        )


def host_Neo4j(NEO4J_ADDRESS, host) :
    """
    TODO
    """

    # host.print_docker_host()

    # Create Host and Container Engine nodes
    host_node(NEO4J_ADDRESS, host)

    # Print info
    print('Added the Host and Docker nodes.\n')

    # Graph update: +2 nodes and +6 edges
    # Total: 411 nodes and 6 edges.