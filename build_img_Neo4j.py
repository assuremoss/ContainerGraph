from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def image_Neo4j_chart(NEO4J_ADDRESS, img) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    
    with driver.session() as session:

        session.write_transaction(create_image_node, img)
        session.write_transaction(create_dockerfile_node, img)
        # session.write_transaction(create_sbom_node, img)
        session.write_transaction(create_relationships, img)

    driver.close()


def create_image_node(tx, img) :
    """
    TODO
    """
    query = "MERGE (i:Image:Docker {name: $name, img_id: $img_id, repo: $repo, tag: $tag, t_created: $t_created, img_size: $img_size})"
    tx.run(query, name = img.name, img_id = img.img_id, repo = img.repo, tag = img.tag, t_created = img.t_created, img_size = img.img_size)


def create_dockerfile_node(tx, img) :
    """
    TODO
    """

    ### TO UPDATE WITH ALL THE FIELDS

    tx.run("MERGE (df:Dockerfile {name: 'Dockerfile', img_id: $img_id})", img_id = img.img_id)


def create_relationships(tx, img) :
    """
    TODO
    """

    tx.run("MATCH (i:Image:Docker {img_id: $img_id}) "
           "MATCH (de:DockerEngine)-[:RUNS_ON_TOP]->(h:LinuxHost) "
           "MERGE (de)-[:MANAGES]->(i) "
           "UNION "
           "MATCH (i:Image:Docker {img_id: $img_id}) "
           "MATCH (df:Dockerfile {img_id: $img_id}) "
           "MERGE (i)-[:BUILT_FROM]->(df) "
           , img_id = img.img_id)


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
