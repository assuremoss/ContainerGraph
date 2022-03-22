from neo4j import GraphDatabase
from build_infrastructure import get_Infrastructure
from build_host_Neo4j import host_Neo4j
from build_perm_Neo4j import perm_Neo4j


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def is_db_initialize(NEO4J_ADDRESS) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")

    with driver.session() as session:
        result = session.read_transaction(query_db)
    driver.close()
    
    return result


def query_db(tx) :
    """
    TODO
    """

    result = tx.run("MATCH (n) RETURN COUNT(n) > 0")

    result = result.single()[0]
    return result


def vuln_Neo4j(NEO4J_ADDRESS) :
    """
    TODO
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
    """
    TODO
    """

    # if Neo4J is empty
    if not is_db_initialize(NEO4J_ADDRESS) :

        # Initialize Host
        host = get_Infrastructure()

        # Initialize Host
        host_Neo4j(NEO4J_ADDRESS, host)

        # Initialize Permissions
        perm_Neo4j(NEO4J_ADDRESS)

        # Initialize Vulnerabilities
        vuln_Neo4j(NEO4J_ADDRESS)

