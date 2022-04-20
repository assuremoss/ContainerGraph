from neo4j import GraphDatabase
from build_infrastructure import get_Infrastructure
from build_host_Neo4j import host_Neo4j
from init_Neo4j import init_Neo4j


def connect_to_neo4j(uri, user, password) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


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

        # Initialize CAPs & syscalls, engines and kernel versions.
        init_Neo4j(NEO4J_ADDRESS)

        # Retrieve Host info
        host = get_Infrastructure()

        # Initialize Host
        host_Neo4j(NEO4J_ADDRESS, host)

        #
        # MATCH (n)-[r]->() RETURN COUNT(r)
        # MATCH (n) RETURN COUNT(n)
        # print('Total: 411 nodes and 6 relationships.\n')

        # Initialize Vulnerabilities
        # vuln_Neo4j(NEO4J_ADDRESS)

        # Print TOTAL info
        # # of nodes
        # # of edges
        # ...

