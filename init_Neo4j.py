from neo4j import GraphDatabase
from parse_perm_file import parse_perm_taxonomy


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def perm_nodes(NEO4J_ADDRESS, capabilities, syscalls) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    
    with driver.session() as session:

        session.write_transaction(create_caps_nodes, capabilities)
        session.write_transaction(create_syscall_nodes, syscalls)
        session.write_transaction(create_ro_node)
        session.write_transaction(create_nonewpriv_node)

    driver.close()


def create_caps_nodes(tx, capabilities) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    for cap in capabilities :
        query = "MERGE (cap:Capability {name: '" + cap['name'] + "'})"
        tx.run(query)


def create_syscall_nodes(tx, syscalls) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    for syscall in syscalls :
        query = "MERGE (sysc:SystemCall {name: '" + syscall['name'] + "'})"
        tx.run(query)


def create_ro_node(tx) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    query = "MERGE (ro:NotReadOnly {name: 'NotReadOnly'})"
    tx.run(query)


def create_nonewpriv_node(tx) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    query = "MERGE (nnp:NewPrivileges {name: 'NewPriv'})"
    tx.run(query)


def eng_v_nodes(NEO4J_ADDRESS, docker_v, containerd_v, runc_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    
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
        query = "MERGE (dv:DockerVersion {key: '" + dv + "'})"
        tx.run(query)

    for cv in containerd_v :
        query = "MERGE (cv:containerdVersion {key: '" + cv + "'})"
        tx.run(query)

    for rv in runc_v :
        query = "MERGE (rv:runcVersion {key: '" + rv + "'})"
        tx.run(query)


def kernel_v_nodes(NEO4J_ADDRESS, kernel_v) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    
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
        query = "MERGE (kv:KernelVersion {key: '" + kv + "'})"
        tx.run(query)


def init_Neo4j(NEO4J_ADDRESS) :
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
    perm_nodes(NEO4J_ADDRESS, result['capabilities'], result['syscalls'])
    kernel_v_nodes(NEO4J_ADDRESS, result['kernel_v'])
    eng_v_nodes(NEO4J_ADDRESS, result['docker_v'], result['containerd_v'], result['runc_v'])

    # Print info
    print("Added " + str(len(result['capabilities'])) + " capabilities.")
    print("Added " + str(len(result['syscalls'])) + " system calls.")

    print("Added " + str(len(result['kernel_v'])) + " Linux kernel versions.")

    print("Added " + str(len(result['docker_v'])) + " Docker engine versions.")
    print("Added " + str(len(result['containerd_v'])) + " containerd engine versions.")
    print("Added " + str(len(result['runc_v'])) + " runc engine versions.")

