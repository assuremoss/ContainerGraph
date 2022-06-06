from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def get_kernel_v(NEO4J_ADDRESS):
    """ This function returns the kernel version currently in use.
    
    Description:
    The Linux kernel version is returned in the format of <kernel_version>.<major_revision>.
    For example, version 4.9.
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        result = session.read_transaction(query_kernel_v)
    driver.close()
    
    return result


def query_kernel_v(tx) :
    """ Query Neo4J to return the Linux kernel version currently in use.
    
    Arguments:
    tx - desc
    
    Description:
    Returns the Linux version version.
    """

    result = tx.run("MATCH (d:Host:LinuxHost)-[:USES]->(kv:KernelVersion) RETURN kv.key")

    result = result.single()[0]
    return result


def host_node(NEO4J_ADDRESS, host) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
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
    print('Added the host and Docker nodes.\n')

