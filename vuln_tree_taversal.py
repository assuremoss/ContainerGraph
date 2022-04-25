import time
from neo4j import GraphDatabase


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def query_leaf(tx, node_id):
    # return tx.run("MATCH (n) WHERE ID(n)=$node_id MATCH ()-[r:HAS]->(n) RETURN COUNT(r)>0", node_id=node_id).single().value()
    return tx.run("MATCH (n) WHERE ID(n)=$node_id RETURN n.property='GREEN'", node_id=node_id).single().value()
    

def evaluate_leaf(NEO4J_ADDRESS, node_id) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        result = session.read_transaction(query_leaf, node_id)
    driver.close()
    
    return result


def evaluate_and(NEO4J_ADDRESS, and_node) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    result = []
    for child in and_node['children'] : 
        result.append(evaluate_tree(NEO4J_ADDRESS, child))
    
    return all(result)


def evaluate_or(NEO4J_ADDRESS, or_node) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    result = []
    for child in or_node['children'] : 
        result.append(evaluate_tree(NEO4J_ADDRESS, child))
    
    return any(result)


def evaluate_tree(NEO4J_ADDRESS, node_id) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """
    
    # Get the current node in the nodes dictionary
    current_node = get_node_dict(NEO4J_ADDRESS, node_id)   

    # Skip ROOT node
    # if current_node['type'] == 'CVE' : 
    if current_node['type'] == 'ROOT_NODE' : 
        return evaluate_tree(NEO4J_ADDRESS, current_node['children'])

    # Process an AND_NODE
    elif current_node['type'] == 'AND_NODE' : 
        return evaluate_and(NEO4J_ADDRESS, current_node)

    # Process an OR_NODE
    elif current_node['type'] == 'OR_NODE' : 
        return evaluate_or(NEO4J_ADDRESS, current_node)

    # Process a leaf
    else : 
        return evaluate_leaf(NEO4J_ADDRESS, node_id)


def get_node_dict(NEO4J_ADDRESS, node_id) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        return session.read_transaction(query_node, node_id)

    
def query_node(tx, node_id):
    return tx.run(
        "MATCH (n) WHERE ID(n)=$node_id "
        "CALL { WITH n "
        "MATCH (c)-[*1]->(n) "
        "WITH COLLECT(ID(c)) AS children RETURN children } "
        "RETURN n{nodeID: ID(n), type: labels(n)[0], children: children} AS node_dict "
        , node_id=node_id
    ).single().value()


def get_cve_nodes(NEO4J_ADDRESS, cve) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    return 704

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        return session.read_transaction(query_cve_node, cve)


def query_cve_node(tx, cve) :    
    # Return ID(cve_node), ID(cve_child_node)
    return tx.run("MATCH (c:CVE {key: $cve}) RETURN ID(c) ", cve=cve)


def query_vulnerability(NEO4J_ADDRESS, cve) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """
    
    # Get cve node and cve child_node IDs
    _, node_id = get_cve_nodes(NEO4J_ADDRESS, cve)

    # Traverse and evaluate the AND/OR vulnerability tree
    start = time.time()
    result = evaluate_tree(NEO4J_ADDRESS, node_id)
    end = time.time()

    print(result)
    print('Execution time: ' + str(round(end-start, 5)) + ' seconds.')
    
    return result
    

query_vulnerability('192.168.2.5', 'CVE-2022-12345')