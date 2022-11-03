from Neo4j_connection import connect_to_neo4j
from build_infrastructure import get_Infrastructure
from build_host_Neo4j import host_Neo4j
from init_Neo4j import init_Neo4j
from build_host_Neo4j import host_exploits
import json


def graph_info() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j()
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


def is_db_initialize() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j()
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


def vuln_Neo4j(vuln) :
    """  brief title.

    """
    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(create_vuln, vuln)
    driver.close()


def create_vuln(tx, vuln) : 
    tx.run(vuln)


def create_host_exploits() : 
    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(host_exploits)
    driver.close()


def parse_vuln_file() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    try :
        with open('./files/vulns.json', 'r') as vulns_file :
            vulns = json.load(vulns_file)

            # Return each vuln as a dictionary
            container_attacks = vulns['container_attacks']
            kernel_attacks = vulns['kernel_attacks'][0]
            engine_attacks = vulns['engine_attacks'][0]

            return container_attacks, kernel_attacks, engine_attacks

    except FileNotFoundError as error :
        print(error)
        exit(1)


def init_vuln() : 
    """  brief title.
    """
    import files.CVEs   
    
    vuln_Neo4j(files.CVEs.vuln1)
    vuln_Neo4j(files.CVEs.vuln2)
    vuln_Neo4j(files.CVEs.vuln3)


def initialize_Neo4j_db() :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # If Neo4J is not empty
    if not is_db_initialize() :

        print('Initializing the graph database...\n')

        # Retrieve Host info
        host = get_Infrastructure()

        # Initialize CAPs & syscalls, engines and kernel versions.
        init_Neo4j()

        # Initialize Host
        host_Neo4j(host)

        # Print graph info
        n_nodes, n_edges = graph_info()
        print('Total: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')

        # Initialize Vulnerabilities and the :EXPLOITS edges for the Host (engine versions)
        init_vuln()

        # Create
        create_host_exploits()

        # Print graph info
        # n_nodes, n_edges = graph_info()
        # print('Total: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')


