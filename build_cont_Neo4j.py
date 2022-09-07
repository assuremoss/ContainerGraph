from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def cont_Neo4j_chart(NEO4J_ADDRESS, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:

        session.write_transaction(create_cont_node, cont)
        session.write_transaction(create_cconfig_nodes, cont)
        session.write_transaction(create_cconfig_relationships, cont)

        if cont.permissions.profile == 'docker-privileged' :
            session.write_transaction(create_perm_relationships, cont) 
        
        else :
            session.write_transaction(create_sec_prof_nodes, cont)
            session.write_transaction(create_prof_relationships, cont) 

        session.write_transaction(create_cont_relationships, cont) 

    driver.close()


def create_cconfig_nodes(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # For each docker run arg (e.g. user, volume, etc.) create a node 
    for key in cont.cconfig.fields :
        value = cont.cconfig.fields[key]

        # Do not add a node for the container name
        if not key == 'name' :
            if type(value) == list :
                tx.run("MERGE (cc:ContainerConfig {name: $key, value: $value, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})", key=key, value=value)

            else :
                if not value == 'root' and key == 'user' :
                    query = "MERGE (cc:ContainerConfig {name: $value, type: $type, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
                    tx.run(query, type=key, value=value
                    )


def create_cconfig_relationships(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # For each docker run arg (e.g. user, volume, etc.) create a node 
    for key in cont.cconfig.fields :
        value = cont.cconfig.fields[key]

        if not key == 'name' :
            if type(value) == list :
                tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) "
                       "MATCH (cc:ContainerConfig {name: $key, value: $value}) "
                       "SET cc.weight = 1 "
                       "MERGE (c)-[:HAS]->(cc) ",
                       cont_id = cont.cont_id, key = key, value = value
                )

            else :
                tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) "
                       "MATCH (cc:ContainerConfig {name: $value, type: $type}) "
                       "SET cc.weight = 1 "
                       "MERGE (c)-[:HAS]->(cc) ",
                       cont_id = cont.cont_id, type = key, value = value
                )


def create_sec_prof_nodes(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    tx.run("MERGE (p:Permissions {name: 'Permissions', profile: $profile, object: 'Container'})", profile = cont.permissions.profile) 
    tx.run("MERGE (aa:AppArmor {name: 'AppArmor', profile: $profile, object: 'Container'})", profile = cont.permissions.profile)
    tx.run("MERGE (sc:SecComp {name: 'SecComp', profile: $profile, object: 'Container'})", profile = cont.permissions.profile)


def create_prof_relationships(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) "
        "MATCH (aa:AppArmor {name: 'AppArmor', profile: $profile}) "
        "MERGE (c)-[:HAS]->(aa) ",
        cont_id = cont.cont_id, profile = cont.permissions.profile
    )

    tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) "
        "MATCH (sc:SecComp {name: 'SecComp', profile: $profile}) "
        "MERGE (c)-[:HAS]->(sc) ",
        cont_id = cont.cont_id, profile = cont.permissions.profile
    )

    for cap in cont.permissions.caps :
        tx.run("MATCH (aa:AppArmor {name: 'AppArmor', profile: $profile}) "
           "MATCH (cap:Capability {name: '" + cap + "'})"
           "SET cap.weight = 1 "
           "MERGE (aa)-[:HAS]->(cap) "
           , profile = cont.permissions.profile
        )

    for syscall in cont.permissions.syscalls :
        tx.run("MATCH (sc:SecComp {name: 'SecComp', profile: $profile}) "
           "MATCH (sysc:SystemCall {name: '" + syscall + "'})"
           "SET sysc.weight = 1 "
           "MERGE (sc)-[:HAS]->(sysc) "
           , profile = cont.permissions.profile
        )

    tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) "
        "MATCH (p:Permissions {name: 'Permissions', profile: $profile}) "
        "MERGE (c)-[:HAS]->(p) ",
        cont_id = cont.cont_id, profile = cont.permissions.profile
    )

    if cont.permissions.read_only == False :
        tx.run("""
        MATCH (ro:NotReadOnly) 
        SET ro.weight = 1 
        UNION
        MATCH (ro:NotReadOnly) 
        MATCH (p:Permissions {name: 'Permissions', profile: $profile}) 
        MERGE (p)-[:HAS]->(ro)  
        """
            , profile = cont.permissions.profile
        )

    if cont.permissions.no_new_priv == False :
        tx.run("MATCH (np:NewPriv {name: 'NewPriv', object: 'Container'}) "
            "MATCH (p:Permissions {name: 'Permissions', profile: $profile}) "
            "SET np.weight = 1 "
            "MERGE (p)-[:HAS]->(np)  "
            , profile = cont.permissions.profile
        )


def create_perm_relationships(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) "
        "MATCH (p:Permissions:Privileged {name: 'Privileged'}) "
        "SET p.weight = 5 "
        "MERGE (c)-[:HAS]->(p) ",
        cont_id = cont.cont_id
    )

    for cap in cont.permissions.caps :
        tx.run("MATCH (p:Permissions:Privileged {name: 'Privileged'}) "
           "MATCH (cap:Capability {name: '" + cap + "'})"
           "SET cap.weight = 1 "
           "MERGE (p)-[:HAS]->(cap) "
           , profile = cont.permissions.profile
        )

    for syscall in cont.permissions.syscalls :
        tx.run("MATCH (p:Permissions:Privileged {name: 'Privileged'}) "
           "MATCH (sysc:SystemCall {name: '" + syscall + "'})"
           "SET sysc.weight = 1 "
           "MERGE (p)-[:HAS]->(sysc) "
           , profile = cont.permissions.profile
        )

    if cont.permissions.read_only == False :
        tx.run("MATCH (ro:NotReadOnly {name: 'NotReadOnly', object: 'Container'}) "
            "MATCH (p:Permissions:Privileged {name: 'Privileged'}) "
            "SET ro.weight = 1 "
            "MERGE (p)-[:HAS]->(ro)  "
        )

    if cont.permissions.no_new_priv == False :
        tx.run("MATCH (np:NewPriv {name: 'NewPriv', object: 'Container'}) "
            "MATCH (p:Permissions:Privileged {name: 'Privileged'}) "
            "SET np.weight = 1 "
            "MERGE (p)-[:HAS]->(np)  "
        )


def create_cont_node(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # Create Container node
    tx.run("MERGE (c:Container:Docker {name: $name, cont_id: $cont_id, img_id: $img_id, start_t: $start_t, status: $status})", cont_id = cont.cont_id, img_id = cont.img_id, name = cont.name, start_t = cont.start_t, status = cont.status) 

    # Create Deployment node 
    tx.run("MERGE (cd:Deployment {name: 'Deployment', cont_id: $cont_id})", cont_id = cont.cont_id)


def create_cont_relationships(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # Container relationships
    tx.run("MATCH (de:DockerEngine)-[:RUNS_ON_TOP]->(h:LinuxHost) "
           "MATCH (c:Container:Docker {cont_id: $cont_id}) "
           "MERGE (de)-[:RUNS]->(c) "
           "UNION "
           "MATCH (c:Container:Docker {cont_id: $cont_id}) "
           "MATCH (i:Image:Docker {img_id: $img_id})  "
           "MERGE (c)-[:INSTANCIATE]->(i) ", 
           cont_id = cont.cont_id, img_id = cont.img_id
    )

    # Deployment relationships
    tx.run("""
    MATCH (AllD:AllDeployments {name: 'AllDeployments'})
    MATCH (cd:Deployment {name: 'Deployment', cont_id: $cont_id})
    MERGE (AllD)-[:CONTAINS]->(cd)
    UNION
    MATCH (cd:Deployment {name: 'Deployment', cont_id: $cont_id})
    MATCH (c:Container:Docker {cont_id: $cont_id}) 
    MERGE (cd)-[:PART_OF]->(c)
    UNION
    MATCH (cd:Deployment {name: 'Deployment', cont_id: $cont_id})
    MATCH (ce:ContainerEngine:DockerEngine {name: 'DockerEngine'})
    MERGE (cd)-[:PART_OF]->(ce)
    """, cont_id = cont.cont_id)

