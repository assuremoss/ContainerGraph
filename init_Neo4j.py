from Neo4j_connection import connect_to_neo4j
from parse_perm_file import parse_perm_taxonomy


def perm_nodes(capabilities, syscalls) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j()
    with driver.session() as session :
        session.write_transaction(create_caps_nodes, capabilities)
        session.write_transaction(create_syscall_nodes, syscalls)
        session.write_transaction(create_perm_nodes)

        # Create the AllDeployments and AttackSurface nodes 
        session.write_transaction(create_alldep)

    driver.close()


def create_alldep(tx) :
    """  brief title.

    Description:
    blablabla
    """

    query = """
    MERGE (AllD:AllDeployments {name: 'AllDeployments'}) 
    MERGE (AS:AttackSurface {name: 'AttackSurface'})
    """

    tx.run(query)


def create_caps_nodes(tx, capabilities) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    for cap in capabilities :
        query = "CREATE (cap:Capability {name:$cap, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
        tx.run(query, cap=cap['name'])


def create_syscall_nodes(tx, syscalls) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    for syscall in syscalls :
        query = "CREATE(sysc:SystemCall {name:$syscall, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
        tx.run(query, syscall=syscall['name'])


def create_perm_nodes(tx) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    tx.run("CREATE (cc:ContainerConfig {name: 'root', type: 'user', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})")

    tx.run("""
    CREATE (ro:NotReadOnly {name: 'NotReadOnly', object: 'Container', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    """)
    
    tx.run("""
    CREATE (np:NewPriv {name: 'NewPriv', object: 'Container', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    """)

    tx.run("""
    CREATE (p:Permissions:Privileged {name: 'Privileged', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    """)


def eng_v_nodes(docker_v, containerd_v, runc_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j()
    
    with driver.session() as session:
        session.write_transaction(create_eng_node, docker_v, containerd_v, runc_v)
    driver.close()


def create_eng_node(tx, docker_v, containerd_v, runc_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    for dv in docker_v :
        query = "CREATE (dv:DockerVersion {name:$dv, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
        tx.run(query, dv=dv)

    for cv in containerd_v :
        query = "CREATE (cv:containerdVersion {name:$cv, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
        tx.run(query, cv=cv)

    for rv in runc_v :
        query = "CREATE (rv:runcVersion {name:$rv, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
        tx.run(query, rv=rv)


def kernel_v_nodes(kernel_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j()
    
    with driver.session() as session:
        session.write_transaction(create_kernel_v_node, kernel_v)
    driver.close()


def create_kernel_v_node(tx, kernel_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    for kv in kernel_v :
        query = "CREATE(kv:KernelVersion {name:$kv, tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})"
        tx.run(query, kv=kv)


def init_Neo4j() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # Retrieve data from the JSON file
    result = parse_perm_taxonomy()

    # Load the data into Neo4J
    perm_nodes(result['capabilities'], result['syscalls'])
    kernel_v_nodes(result['kernel_v'])
    eng_v_nodes(result['docker_v'], result['containerd_v'], result['runc_v'])

    # Print info
    print("Added " + str(len(result['capabilities'])) + " capabilities.")
    print("Added " + str(len(result['syscalls'])) + " system calls.")

    print("Added " + str(len(result['kernel_v'])) + " Linux kernel versions.")

    print("Added " + str(len(result['docker_v'])) + " Docker engine versions.")
    print("Added " + str(len(result['containerd_v'])) + " containerd engine versions.")
    print("Added " + str(len(result['runc_v'])) + " runc engine versions.")

