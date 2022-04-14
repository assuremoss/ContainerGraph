from cProfile import run
from neo4j import GraphDatabase
import json


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


#
# IMPORTANT
#
# For container engines (e.g. docker, runc), we do not consider "Release Candidate" (beta) versions, 
# but only stable releases
# For example, we consider v1.0.0, but not v1.0.0-rc2.
#

# docker releases
# all releases: https://github.com/docker/docker-ce/tags
# current release: https://docs.docker.com/engine/release-notes/
# previous releases: https://docs.docker.com/engine/release-notes/19.03/

# containerd releases
# https://github.com/containerd/containerd/tags

# runc releases
# https://github.com/opencontainers/runc/tags

# Linux Kernel
# https://kernelnewbies.org/LinuxVersions
# https://mirrors.edge.kernel.org/pub/linux/kernel/

def parse_init_file() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    try :
        with open('./files/permission_taxonomy.json', 'r') as perm_file :
            perm = json.load(perm_file)

            capabilities = perm['capabilities']
            syscalls = perm['syscalls']

            kernel_v = perm['kernel_v']

            docker_v = perm['docker_v']
            containerd_v = perm['containerd_v']
            runc_v = perm['runc_v']

            result = {
                'capabilities': capabilities, 
                'syscalls': syscalls, 
                'kernel_v': kernel_v, 
                'docker_v': docker_v, 
                'containerd_v': containerd_v, 
                'runc_v': runc_v
            }

            return result

    except FileNotFoundError as error :
        print(error)
        exit(1)


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
        cap = list(cap.keys())[0]
        query = "MERGE (cap:Capability {name: '" + cap + "'})"
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
    result = parse_init_file()

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
    print("Added " + str(len(result['runc_v'])) + " runc engine versions.\n")

