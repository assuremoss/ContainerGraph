from neo4j_connection import connect_to_neo4j


def cont_Neo4j_chart(cont) :
    """Description ...
    
    Parameters
    ----------
    param1 : desc ...

    Return
    ----------
    object
    """

    driver = connect_to_neo4j()
    with driver.session() as session:

        # Create container and configuration nodes
        session.write_transaction(create_cconfig_nodes, cont)

        if cont.permissions.profile == 'docker-privileged' :
            session.write_transaction(create_perm_relationships, cont) 

        else :
            session.write_transaction(create_sec_prof_nodes, cont)
            session.write_transaction(create_prof_relationships, cont) 

        session.write_transaction(create_cconfig_relationships, cont)
        session.write_transaction(create_cont_properties_rel, cont) 
        session.write_transaction(create_cont_exploit_rel, cont.cont_id)

    driver.close()


def create_cconfig_nodes(tx, cont) :
    """Description ...
    """

    # Create Container node
    tx.run("MERGE (c:Container:Docker {name: $name, cont_id: $cont_id, img_id: $img_id, start_t: $start_t, status: $status})", cont_id = cont.cont_id, img_id = cont.img_id, name = cont.name, start_t = cont.start_t, status = cont.status) 
   
    # For each docker run arg (e.g. user, volume, etc.) create a node 
    for key, value in cont.cconfig.fields.items() :

        # Do not add a node for the container name
        if key != 'name' :
            if type(value) == list :
                tx.run("CREATE (cc:ContainerConfig {name: $key, value: $value, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})", key=key, value=value)

            else :
                if key == 'user' and value != 'root' :
                    query = "CREATE (cc:ContainerConfig {name: $value, type: $type, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
                    tx.run(query, type=key, value=value)

                # elif key == 'pid_ns' : 
                #     query = "MERGE (cc:ContainerConfig {name: 'PidNamespace', type: 'host', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
                #     tx.run(query, type=key, value=value)


def create_cconfig_relationships(tx, cont) :
    # For each docker run arg (e.g. user, volume, etc.) create a node 
    for key, value in cont.cconfig.fields.items() :

        if key != 'name' :
            if type(value) == list :

                tx.run("""
                MATCH (p:Permissions {container: $cont_id}) 
                MATCH (cc:ContainerConfig {name: $key, value: $value})
                SET cc.weight = 1 
                MERGE (p)-[:HAS_PROPERTY]->(cc) 
                """, cont_id = cont.cont_id, key = key, value = value)
                
            else :
                if key == 'pid_ns' :
                    tx.run("""
                    MATCH (cc:ContainerConfig {name: 'PidNamespace', type: 'host'})
                    MATCH (p:Permissions {container: $cont_id}) 
                    SET cc.weight = 1 
                    MERGE (p)-[:HAS_PROPERTY]->(cc) 
                    """, cont_id = cont.cont_id)

                else :
                    tx.run("""
                    MATCH (p:Permissions {container: $cont_id}) 
                    MATCH (cc:ContainerConfig {name: $value, type: $type}) 
                    SET cc.weight = 1 
                    MERGE (p)-[:HAS_PROPERTY]->(cc) 
                    """, cont_id = cont.cont_id, type = key, value = value)


def create_sec_prof_nodes(tx, cont) :
    """Description ...
    
    Parameters
    ----------
    param1 : desc ...

    Return
    ----------
    object
    """
   
    tx.run("MERGE (p:Permissions {name: 'Permissions', container: $cont_id, profile: $profile, object: 'Container'})", profile = cont.permissions.profile, cont_id=cont.cont_id) 
    tx.run("MERGE (aa:AppArmor {name: 'AppArmor', container: $cont_id, object: 'Container'})", cont_id=cont.cont_id)
    tx.run("MERGE (sc:SecComp {name: 'SecComp', container: $cont_id, object: 'Container'})", cont_id=cont.cont_id)


def create_prof_relationships(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    tx.run("""
        MATCH (c:Container:Docker {cont_id: $cont_id}) 
        MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
        MERGE (c)-[:HAS]->(p) 
    """, cont_id = cont.cont_id)

    tx.run("""
        MATCH (p:Permissions {name: 'Permissions', container: $cont_id})  
        MATCH (aa:AppArmor {name: 'AppArmor', container: $cont_id}) 
        MERGE (p)-[:HAS_PROPERTY]->(aa) 
    """, cont_id = cont.cont_id)

    tx.run("""
        MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
        MATCH (sc:SecComp {name: 'SecComp', container: $cont_id})
        MERGE (p)-[:HAS_PROPERTY]->(sc) 
    """, cont_id = cont.cont_id)

    for cap in cont.permissions.caps :
        tx.run("MATCH (aa:AppArmor {name: 'AppArmor', container: $cont_id}) "
           "MATCH (cap:Capability {name: '" + cap + "'})"
           "SET cap.weight = 1 "
           "MERGE (aa)-[:HAS_PROPERTY]->(cap) "
           , cont_id = cont.cont_id
        )

    for syscall in cont.permissions.syscalls :
        tx.run("MATCH (sc:SecComp {name: 'SecComp', container: $cont_id}) "
           "MATCH (sysc:SystemCall {name: '" + syscall + "'})"
           "SET sysc.weight = 1 "
           "MERGE (sc)-[:HAS_PROPERTY]->(sysc) "
           , cont_id = cont.cont_id
        )

    if cont.permissions.read_only == False :
        tx.run("""
        MATCH (ro:NotReadOnly) 
        SET ro.weight = 1 
        UNION
        MATCH (ro:NotReadOnly) 
        MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
        MERGE (p)-[:HAS_PROPERTY]->(ro)  
        """
            , cont_id = cont.cont_id
        )

    if cont.permissions.no_new_priv == False :
        tx.run("MATCH (np:NewPriv {name: 'NewPriv', object: 'Container'}) "
            "MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) "
            "SET np.weight = 1 "
            "MERGE (p)-[:HAS_PROPERTY]->(np)  "
            , cont_id = cont.cont_id
        )


def create_perm_relationships(tx, cont) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    tx.run("MERGE (p:Permissions {name: 'Permissions', container: $cont_id, profile: $profile, object: 'Container'})", profile = cont.permissions.profile, cont_id = cont.cont_id) 

    tx.run("""
    MATCH (p:Permissions {container: $cont_id}) 
    MATCH (priv:Permissions:Privileged {name: 'Privileged'})
    SET priv.weight = 5
    MERGE (p)-[:HAS_PROPERTY]->(priv) 
    """, cont_id = cont.cont_id)

    tx.run("""
        MATCH (c:Container:Docker {cont_id: $cont_id}) 
        MATCH (p:Permissions {container: $cont_id}) 
        SET p.weight = 1
        MERGE (c)-[:HAS]->(p)
        """, cont_id = cont.cont_id)

    for cap in cont.permissions.caps :
        tx.run("MATCH (p:Permissions {container: $cont_id}) "
               "MATCH (cap:Capability {name: '" + cap + "'}) "
               "SET cap.weight = 1 "
               "MERGE (p)-[:HAS_PROPERTY]->(cap) "
            , cont_id = cont.cont_id)

    for syscall in cont.permissions.syscalls :
        tx.run("MATCH (p:Permissions {container: $cont_id}) "
            "MATCH (sysc:SystemCall {name: '" + syscall + "'}) "
            "SET sysc.weight = 1 "
            "MERGE (p)-[:HAS_PROPERTY]->(sysc) "
           , cont_id = cont.cont_id) 

    if cont.permissions.read_only == False :
        tx.run("""
            MATCH (ro:NotReadOnly {name: 'NotReadOnly', object: 'Container'}) 
            MATCH (p:Permissions {container: $cont_id}) 
            SET ro.weight = 1 
            MERGE (p)-[:HAS_PROPERTY]->(ro)  
            """, cont_id = cont.cont_id)

    if cont.permissions.no_new_priv == False :
        tx.run("""
            MATCH (np:NewPriv {name: 'NewPriv', object: 'Container'}) 
            MATCH (p:Permissions {container: $cont_id}) 
            SET np.weight = 1 
            MERGE (p)-[:HAS_PROPERTY]->(np)
            """, cont_id = cont.cont_id)


def create_cont_properties_rel(tx, cont) :

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
    MATCH (dd:DockerDeployment {name: 'DockerDeployment'})
    MATCH (c:Container:Docker {cont_id: $cont_id})
    MERGE (dd)-[:HAS]->(c)
    """, cont_id = cont.cont_id)


def create_cont_exploit_rel(tx, cont_id) :
    # Retrieve all leaves to which the container is connected, that are an assumption
    # of at least one CVE
    leaves_IDs = tx.run("""
            MATCH (c:Container:Docker {cont_id:$cont_id})-[*1..3]->(l {tree: 'leaf'}) 
            WHERE EXISTS( (l)-[:AND]->(:AND_NODE) ) OR EXISTS( (l)-[:OR]->(:OR_NODE) )
            WITH COLLECT(ID(l)) AS children RETURN children
        """, cont_id=cont_id).value()[0]

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
                MATCH (c:Container:Docker {cont_id:$cont_id})
                MATCH (l) WHERE ID(l)=$leaf_id
                MERGE (c)-[:EXPLOITS]->(l)
                """, cont_id=cont_id, leaf_id=leaf_id)

            else : # AND_node
                all_connected = tx.run("""
                MATCH (parent) WHERE ID(parent)=$parent_id
                CALL {
                    WITH parent
                    MATCH (p:Permissions {container: $cont_id})-[:HAS_PROPERTY*1..2]->(leaf {tree: 'leaf'})-[:AND]->(parent)
                    RETURN COUNT(leaf) AS cont_c
                }
                CALL {
                    WITH parent
                    MATCH (leaf {tree: 'leaf'})-[:AND]->(parent)
                    RETURN COUNT(leaf) AS childr
                }
                RETURN cont_c = childr
                """, parent_id=parent['nodeID'], cont_id=cont_id).value()[0]

                # If all AND_node children are connected to the container
                # create the exploit edge.
                if all_connected :
                    tx.run("""
                        MATCH (l)-[:AND]->(p) WHERE ID(p)=$parent_id
                        MATCH (c:Container {cont_id:$cont_id})
                        MERGE (c)-[:EXPLOITS]->(l)
                    """, parent_id=parent['nodeID'], cont_id=cont_id)

