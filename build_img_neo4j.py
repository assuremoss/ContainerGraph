from neo4j_connection import connect_to_neo4j


def image_Neo4j_chart(img) :
    """
    TODO
    """

    driver = connect_to_neo4j()
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

