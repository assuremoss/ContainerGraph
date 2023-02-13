from Neo4j_connection import connect_to_neo4j


def get_kernel_v():
    driver = connect_to_neo4j()
    with driver.session() as session:
        result = session.read_transaction(query_kernel_v)
    driver.close()
    return result

def query_kernel_v(tx) :
    return tx.run("MATCH (d:Host)-[:HAS_PROPERTY]->(kv:KernelVersion) RETURN kv.name").single().value()


def host_node(host) :
    """Description ...
    """
    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(create_host_node, host)
        session.write_transaction(create_host_relationship, host)
    driver.close()


def create_host_node(tx, host) :
    """Description ...
    
    Parameters
    ----------
    param1 : desc ...

    Return
    ----------
    object
    """

    # Create Host node
    query = "MERGE (h:Host:" + host.host.name + " {name: $hostname, processor: $processor, cpus: $cpus, mem: $mem})"
    tx.run(query, hostname = host.host.hostname, processor = host.host.processor, cpus = host.host.cpus, mem = host.host.mem)

    # Create ContainerEngine and Deployment nodes
    if host.name == "DockerEngine" :

        query = "MERGE (ce:ContainerEngine:DockerEngine {name: $name, storage: $storage, registry: $registry})"
        tx.run(query, name = host.name, storage = host.storage, registry = host.registry)

        query = "MERGE (dd:DockerDeployment {name: 'DockerDeployment'})"
        tx.run(query)

    
def host_exploits(tx) : 

    # Retrieve all leaves to which the DockerEngine is connected, that are an assumption
    # of at least one CVE
    leaves_IDs = tx.run("""
            MATCH (ce:ContainerEngine:DockerEngine {name: 'DockerEngine'})-[:HAS_PROPERTY*1..2]->(l {tree: 'leaf'}) 
            WHERE EXISTS( (l)-[:AND]->(:AND_NODE) ) OR EXISTS( (l)-[:OR]->(:OR_NODE) )
            WITH COLLECT(ID(l)) AS children RETURN children
        """).value()[0]
        
    for leaf_id in leaves_IDs : 
        # Retrieve all parent nodes of the current leaf
        parent_list = tx.run("""
            MATCH (l) WHERE ID(l)=$leaf_id
            MATCH (l)-[:OR]->(p:OR_NODE) 
            WITH DISTINCT p 
            RETURN {nodeID: ID(p), type: p.name}
            UNION
            MATCH (l) WHERE ID(l)=$leaf_id
            MATCH (l)-[:AND]->(p:AND_NODE) 
            WITH DISTINCT p 
            RETURN {nodeID: ID(p), type: p.name}
        """, leaf_id=leaf_id).value()

        # Iterate over the leaf's parent nodes
        for parent in parent_list : 
            if parent['type'] == 'OR_NODE' :
                tx.run("""
                MATCH (ce:ContainerEngine:DockerEngine {name: 'DockerEngine'})
                MATCH (l) WHERE ID(l)=$leaf_id
                MERGE (ce)-[:EXPLOITS]->(l)
                """, leaf_id=leaf_id)

            else : # AND_node
                all_connected = tx.run("""
                MATCH (parent) WHERE ID(parent)=$parent_id
                CALL {
                    WITH parent
                    MATCH (ce:ContainerEngine:DockerEngine {name: 'DockerEngine'})-[:HAS_PROPERTY*1..2]->(leaf {tree: 'leaf'})-[:AND]->(parent)
                    RETURN COUNT(leaf) AS cont_c
                }
                CALL {
                    WITH parent
                    MATCH (leaf {tree: 'leaf'})-[:AND]->(parent)
                    RETURN COUNT(leaf) AS childr
                }
                RETURN cont_c = childr
                """, parent_id=parent['nodeID']).value()[0]

                # If all AND_node children are connected to the container
                # create the exploit edge.
                if all_connected :
                    tx.run("""
                        MATCH (l)-[:AND]->(p) WHERE ID(p)=$parent_id
                        MATCH (ce:ContainerEngine:DockerEngine {name: 'DockerEngine'})
                        MERGE (ce)-[:EXPLOITS]->(l)
                    """, parent_id=parent['nodeID'])


def create_host_relationship(tx, host) :
    """Description ...
    
    Parameters
    ----------
    param1 : desc ...

    Return
    ----------
    object
    """

    tx.run("""
        MATCH (h:Host {name: $hostname}) 
        MATCH (kv:KernelVersion {name: $kernel_v}) 
        SET kv.weight = 1 
        MERGE (h)-[:HAS_PROPERTY]->(kv) 
        UNION 
        MATCH (h:Host {name: $hostname}) 
        MATCH (ce:ContainerEngine {name: $name}) 
        MERGE (ce)-[:RUNS_ON_TOP]->(h) 
        UNION 
        MATCH (ce:ContainerEngine {name: $name}) 
        MATCH (kv:KernelVersion {name: $kernel_v}) 
        MERGE (ce)-[:HAS_PROPERTY]->(kv) 
        """, hostname = host.host.hostname, kernel_v = host.host.kernel_v, name = host.name
    )

    if host.name == "DockerEngine" :
        tx.run("""
            MATCH (ce:ContainerEngine:DockerEngine) 
            MATCH (dv:DockerVersion {name: $docker_v}) 
            SET dv.weight = 1 
            MERGE (ce)-[:HAS_PROPERTY]->(dv) 
            UNION 
            MATCH (dv:DockerVersion {name: $docker_v}) 
            MATCH (cv:containerdVersion {name: $containerd_v}) 
            SET cv.weight = 1 
            MERGE (dv)-[:HAS_PROPERTY]->(cv) 
            UNION 
            MATCH (dv:DockerVersion {name: $docker_v}) 
            MATCH (rv:runcVersion {name: $runc_v}) 
            SET rv.weight = 1 
            MERGE (dv)-[:HAS_PROPERTY]->(rv) 
            """, docker_v = host.docker_v, containerd_v = host.containerd_v, runc_v = host.runc_v
        )

        tx.run("""
            MATCH (AllD:AllDeployments {name: 'AllDeployments'})
            MATCH (dd:DockerDeployment {name: 'DockerDeployment'})
            MERGE (AllD)-[:CONTAINS]->(dd)
            UNION
            MATCH (AllD:AllDeployments {name: 'AllDeployments'})
            MATCH (ce:ContainerEngine:DockerEngine {name: 'DockerEngine'})
            MERGE (AllD)-[:CONTAINS]->(ce)
        """)


def host_Neo4j(host) :
    """Description ...
    
    Parameters
    ----------
    param1 : desc ...

    Return
    ----------
    object
    """

    # Print Host info
    # host.print_docker_host()

    # Create Host, Container Engine, and Deployment nodes
    host_node(host)

    # Debug info
    print('Added the host and Docker nodes.\n')

