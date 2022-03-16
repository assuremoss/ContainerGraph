from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def img_already_existing(img_id) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:
        result = session.read_transaction(query_image, img_id)
    driver.close()
    
    return result


def query_image(tx, img_id) :  
    """
    TODO
    """

    result = tx.run("MATCH (i:Image:Docker {img_id: $img_id}) RETURN COUNT(i) > 0", img_id=img_id)

    result = result.single()[0]
    return result


def infra_exist(tx, hostname) :  
    """
    TODO
    """

    result = tx.run("MATCH (h:Host {hostname: $hostname}) RETURN COUNT(h) > 0", hostname=hostname)

    result = result.single()[0]
    return result


def image_Neo4j_chart(img, infra) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    
    with driver.session() as session:

        session.write_transaction(create_image_node, img)
        session.write_transaction(create_dockerfile_node, img)

        if not session.read_transaction(infra_exist, infra.host.hostname) : 
            session.write_transaction(create_engine_node, infra)
            session.write_transaction(create_host_node, infra)
            session.write_transaction(create_host_relationship, infra)
            
        session.write_transaction(create_relationships, img, infra)

    driver.close()


def create_image_node(tx, img) :
    """
    TODO
    """

    ### TO UPDATE WITH ALL THE FIELDS

    tx.run("CREATE (i:Image:Docker {name: $name, img_id: $img_id})", name = img.name, img_id = img.img_id)


def create_dockerfile_node(tx, img) :
    """
    TODO
    """

    ### TO UPDATE WITH ALL THE FIELDS

    tx.run("CREATE (df:Dockerfile {name: 'Dockerfile', img_id: $img_id})", img_id = img.img_id)


def create_engine_node(tx, infra) :
    """
    TODO
    """

    tx.run("CREATE (de:DockerEngine {name: 'DockerEngine', docker_v: $docker_v, containerd_v: $containerd_v, runc_v: $runc_v, storage: $storage, registry: $registry})", docker_v = infra.docker_v, containerd_v = infra.containerd_v, runc_v = infra.runc_v, storage = infra.storage, registry = infra.registry)


def create_host_node(tx, infra) :
    """
    TODO
    """

    tx.run("CREATE (h:Host {name: 'Host', hostname: $hostname, os: $os, architecture: $architecture, kernel_v: $kernel_v, cpus: $cpus, mem: $mem})", hostname = infra.host.hostname, os = infra.host.os, architecture = infra.host.architecture, kernel_v = infra.host.kernel_v, cpus = infra.host.cpus, mem = infra.host.mem)


def create_host_relationship(tx, infra) :
    """
    TODO
    """

    tx.run("MATCH (h:Host {hostname: $hostname}) "
           "MATCH (de:DockerEngine {docker_v: $docker_v}) "
           "CREATE (de)-[:RUNS_ON_TOP]->(h) "
           , hostname = infra.host.hostname, docker_v = infra.docker_v)


def create_relationships(tx, img, infra) :
    """
    TODO
    """

    tx.run("MATCH (i:Image:Docker {img_id: $img_id}) "
           "MATCH (de:DockerEngine {docker_v: $docker_v}) "
           "CREATE (de)-[:MANAGES]->(i) "
           "UNION "
           "MATCH (i:Image:Docker {img_id: $img_id}) "
           "MATCH (df:Dockerfile {img_id: $img_id}) "
           "CREATE (i)-[:BUILT_FROM]->(df) "
           , docker_v = infra.docker_v, img_id = img.img_id)



# def import_graph(tx, img_id) :
#     """
#     Add comments
#     """

#     # Copy the GraphML file into the Neo4J import directory
#     # CAREFULL: Neo4J graphml import does not parse the '_' underscore char in file's name!
#     src = "./charts/" + img_id + "_chart.graphml"

#     ### TO CHECK: how to automatically find the import dir of the neo4j dbms
#     dst = "/Users/francescominna/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/dbms-58a0642f-74c7-4d4a-a80b-53e06c50abc4/import/" + img_id + ".graphml"
#     shutil.copyfile(src, dst)

#     tx.run("CALL apoc.import.graphml('file://" + img_id + ".graphml', {readLabels: true});")
