from neo4j import GraphDatabase
from build_infrastructure import get_Infrastructure
from build_host_Neo4j import host_Neo4j
from init_Neo4j import init_Neo4j


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def graph_info(NEO4J_ADDRESS) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")

    with driver.session() as session:
        n_nodes, n_edges = session.read_transaction(query_graph_info)
    driver.close()
    
    return n_nodes, n_edges


def query_graph_info(tx) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    n_nodes = tx.run("MATCH (n) RETURN COUNT(n)")
    n_nodes = n_nodes.single()[0]

    n_edges = tx.run("MATCH (n)-[r]->() RETURN COUNT(r)")
    n_edges = n_edges.single()[0]

    return n_nodes, n_edges


def is_db_initialize(NEO4J_ADDRESS) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        result = session.read_transaction(query_db)
    driver.close()
    
    return result


def query_db(tx) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    result = tx.run("MATCH (n) RETURN COUNT(n)>0")

    result = result.single()[0]
    return result


def vuln_Neo4j(NEO4J_ADDRESS) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # parse vulns.json

    # get vuln/misc list

    # for each vuln :
        # for each precondition / postcondition :
            # create a node

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")

    # with driver.session() as session:
        # result = session.write_transaction(query_db)
    
    driver.close()









def initialize_Neo4j_db(NEO4J_ADDRESS) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # If Neo4J is not empty
    if not is_db_initialize(NEO4J_ADDRESS) :

        print('Initializing the graph database...\n')

        # Retrieve Host info
        host = get_Infrastructure()

        # Initialize CAPs & syscalls, engines and kernel versions.
        init_Neo4j(NEO4J_ADDRESS)

        # Initialize Host
        host_Neo4j(NEO4J_ADDRESS, host)

        # Print graph info
        n_nodes, n_edges = graph_info(NEO4J_ADDRESS)
        print('Total: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')

        # Initialize Vulnerabilities
        # vuln_Neo4j(NEO4J_ADDRESS)

        # Print graph info
        # n_nodes, n_edges = graph_info(NEO4J_ADDRESS)
        # print('Total: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')

