from neo4j import GraphDatabase
import json


def parse_CAPS_file() :
    """
    TODO
    """

    try :
        with open('./files/permission_taxonomy.json', 'r') as perm_file :
            perm = json.load(perm_file)

            capabilities = perm['capabilities']
            syscalls = perm['syscalls']

            return capabilities, syscalls

    except FileNotFoundError as error :
        print(error)
        exit(1)


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def perm_node(NEO4J_ADDRESS, capabilities, syscalls) :
    """ 
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    
    with driver.session() as session:

        session.write_transaction(create_caps_nodes, capabilities)
        session.write_transaction(create_syscall_nodes, syscalls)
        session.write_transaction(create_ro_node)
        session.write_transaction(create_nonewpriv_node)

    driver.close()


def create_caps_nodes(tx, capabilities) :
    """ 
    TODO
    """

    for cap in capabilities :
        cap = list(cap.keys())[0]
        query = "MERGE (cap:Capability {name: '" + cap + "'})"
        tx.run(query)


def create_syscall_nodes(tx, syscalls) :
    """ 
    TODO
    """

    for syscall in syscalls :
        query = "MERGE (sysc:SystemCall {name: '" + syscall['name'] + "'})"
        tx.run(query)


def create_ro_node(tx) :
    """ 
    TODO
    """

    query = "MERGE (ro:ReadOnly {name: 'ReadOnly', value: 'False'})"
    tx.run(query)


def create_nonewpriv_node(tx) :
    """ 
    TODO
    """

    query = "MERGE (nnp:NoNewPrivileges {name: 'NoNewPriv', value: 'False'})"
    tx.run(query)
    

def perm_Neo4j(NEO4J_ADDRESS) :
    """ 
    TODO
    """

    # Retrieve list of capabilities
    capabilities, syscalls = parse_CAPS_file()
    
    # Create Permission node
    perm_node(NEO4J_ADDRESS, capabilities, syscalls)