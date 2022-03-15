from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def cont_already_existing(cont_id) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:
        result = session.read_transaction(query_cont, cont_id)
    driver.close()

    return result


def query_cont(tx, cont_id) :  
    """
    TODO
    """

    result = tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) RETURN COUNT(c) > 0", cont_id=cont_id)

    result = result.single()[0]
    return result


def cont_Neo4j_chart(cont, infra) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    
    with driver.session() as session:

        session.write_transaction(create_cont_node, cont)
        session.write_transaction(create_cconfig_node, cont)

        if not session.read_transaction(perm_exist, cont) :
            session.write_transaction(create_permissions_node, cont)

        session.write_transaction(create_cont_relationships, cont, infra)

    driver.close()


def perm_exist(tx, cont) :
    """
    TODO
    """

    result = tx.run("MATCH (p:Permissions {profile: $profile}) RETURN COUNT(p) > 0 ", profile = cont.permissions.profile)

    result = result.single()[0]
    return result


def create_cont_node(tx, cont) :
    """
    TODO
    """

    tx.run("CREATE (c:Container:Docker {name: 'Container', cont_id: $cont_id})", cont_id = cont.cont_id) 


def create_cconfig_node(tx, cont) :
    """
    TODO
    """

    tx.run("CREATE (cc:ContainerConfig {name: 'ContainerConfig', c_name: $c_name})", c_name = cont.cconfig.c_name) 


def create_permissions_node(tx, cont) :
    """
    TODO
    """

    tx.run("CREATE (p:Permissions {name: 'Permissions', profile: $profile})", profile = cont.permissions.profile) 


def create_cont_relationships(tx, cont, infra) :
    """
    TODO
    """

    tx.run("MATCH (de:DockerEngine {docker_v: $docker_v}) "
           "MATCH (c:Container:Docker {cont_id: $cont_id}) "
           "CREATE (de)-[:RUNS]->(c) "
           "UNION "
           "MATCH (c:Container:Docker {cont_id: $cont_id}) "
           "MATCH (i:Image:Docker {img_id: $img_id})  "
           "CREATE (c)-[:INSTANCIATE]->(i) "
           "UNION "
           "MATCH (c:Container:Docker {cont_id: $cont_id}) "
           "MATCH (cc:ContainerConfig {c_name: $c_name}) "
           "CREATE (c)-[:HAS]->(cc) "
           "UNION "
           "MATCH (c:Container:Docker {cont_id: $cont_id}) "
           "MATCH (p:Permissions {profile: $profile}) "
           "CREATE (c)-[:CAN]->(p) "
           , docker_v = infra.docker_v, cont_id = cont.cont_id, img_id = cont.img_id, c_name = cont.cconfig.c_name, profile = cont.permissions.profile)

