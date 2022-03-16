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

    if cont.permissions.profile == 'custom' :
        ### TO CHECK
        #
        # Model the case where a custom profile is equal to an already existent custom profile.
        #
        return False

    else :
        result = tx.run("MATCH (p:Permissions {profile: $profile}) RETURN COUNT(p) > 0 ", profile = cont.permissions.profile)

        result = result.single()[0]
        return result


def create_cont_node(tx, cont) :
    """
    TODO
    """

    tx.run("CREATE (c:Container:Docker {name: $name, cont_id: $cont_id, img_id: $img_id, start_t: $start_t, status: $status})", cont_id = cont.cont_id, img_id = cont.img_id, name = cont.name, start_t = cont.start_t, status = cont.status) 


def create_cconfig_node(tx, cont) :
    """
    TODO
    """

    tx.run("CREATE (cc:ContainerConfig {name: 'ContainerConfig', c_name: $c_name, user: $user})", c_name = cont.cconfig.c_name, user = cont.cconfig.user) 


def create_permissions_node(tx, cont) :
    """
    TODO
    """

    tx.run("CREATE (p:Permissions {name: 'Permissions', profile: $profile, capabilities: $capabilities, syscalls: $syscalls, read_only: $read_only, AppArmor_profile: $AppArmor_profile, Seccomp_profile: $Seccomp_profile})", profile = cont.permissions.profile, capabilities = cont.permissions.capabilities, syscalls = cont.permissions.syscalls, read_only = cont.permissions.read_only, AppArmor_profile = cont.permissions.AppArmor_profile, Seccomp_profile = cont.permissions.Seccomp_profile) 


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

