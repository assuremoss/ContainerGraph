from neo4j import GraphDatabase
from build_infrastructure import get_Infrastructure
from build_host_Neo4j import host_Neo4j
from init_Neo4j import init_Neo4j
import json


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


def vuln_Neo4j(NEO4J_ADDRESS, vuln) :
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(create_vuln, vuln)
    driver.close()


def create_vuln(tx, vuln) : 

    # Create vuln nodes.
    tx.run("")

    # Create vuln relationships.
    tx.run("")




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


def init_vuln(NEO4J_ADDRESS) : 
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    # Get 3 lists of dicts, each representing a vuln.
    container_attacks, kernel_attacks, engine_attacks = parse_vuln_file()

    for ca in container_attacks : 
        # Get CVE name
        cve = list(ca.keys())[0]

        cve_dict = ca[cve][0]

        # Iterate over the other CVE fields
        for k in cve_dict.keys() : 

            if k == 'engine' : 
                pass

            elif k == 'mitre_tactic' : 
                # Create MITRE tactic node
                #
                #
                # vuln_Neo4j(NEO4J_ADDRESS, vuln)
                #
                # (m:MITRE:TACTIC {name: cve_dict[k]})
                #

                pass
                

            elif k == 'mitre_technique' :
                # Create MITRE technique node
                pass
        
            elif k == 'pre_conditions' : 
                pass

            elif k == 'post_conditions' : 
                pass


# init_vuln('192.168.2.5')


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
        init_vuln(NEO4J_ADDRESS)

        # Print graph info
        n_nodes, n_edges = graph_info(NEO4J_ADDRESS)
        print('Total: ' + str(n_nodes) + ' nodes and ' + str(n_edges) + ' relationships.\n')

