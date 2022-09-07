from lib2to3.pgen2.token import PLUSEQUAL
import docker
from neo4j import GraphDatabase
from pyparsing import empty

def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))

def connect_to_Docker() : 
    return docker.from_env()


def check_ignored(NEO4J_ADDRESS, cve, cont_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        aux = session.read_transaction(query_ignored, cve, cont_id)
    driver.close()
    return aux

def query_ignored(tx, cve, cont_id) :
    return tx.run("""
    MATCH (ign:IsIgnored {name: 'IsIgnored', cve:$cve, cont_id:$cont_id})
    MATCH (cve:CVE {name:$cve})
    MATCH (d:Deployment {cont_id:$cont_id})
    WHERE (cve)-[:IGNORE]->(ign) AND (d)-[:IGNORE]->(ign) 
    RETURN COUNT(ign)>0 
    """, cont_id=cont_id, cve=cve).single()[0]


def get_deployment_children(NEO4J_ADDRESS, cont_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        leaves = session.read_transaction(query_dep, cont_id)
    driver.close()
    return leaves

    
def query_dep(tx, cont_id):
    """  brief title.
    
    Arguments:
    cont_id - Neo4J node ID of the container node

    Description:
    blablabla
    """

    aux = tx.run("""
    MATCH (c:Container:Docker {cont_id:$cont_id})-[*1..3]->(l {tree: 'leaf'}) 
    WHERE EXISTS( (l)-[:AND]->(:AND_NODE) ) OR EXISTS( (l)-[:OR]->(:OR_NODE) )
    WITH DISTINCT l ORDER BY l.weight DESC 
    WITH COLLECT(ID(l)) AS children RETURN children
    UNION
    MATCH (d:Deployment {name: 'Deployment', cont_id:$cont_id})
    MATCH (d)-[*1..2]->(l {tree: 'leaf'}) 
    WHERE EXISTS( (l)-[:AND]->(:AND_NODE) ) OR EXISTS( (l)-[:OR]->(:OR_NODE) )
    WITH DISTINCT l ORDER BY l.weight DESC 
    WITH COLLECT(ID(l)) AS children RETURN children
    """, cont_id=cont_id).value()

    return aux[0] + aux[1]
    

def get_node(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        node = session.read_transaction(tree_node, node_id)
    driver.close()

    return node


def tree_node(tx, node_id):
    """  brief title.
    
    Arguments:
    node_id - Neo4J node ID of the AND/OR vulnerability tree 

    Description:
    blablabla
    """

    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id 
    OPTIONAL MATCH (c)-[*1]->(n) 
    WITH n, COLLECT(ID(c)) AS children 
    RETURN {nodeID: ID(n), name: n.name, type: labels(n)[0], children: children, needed: n.needed, pred: n.pred, todo: n.todo, weight: n.weight} AS node_dict 
    """, node_id=node_id).single().value()


def append_node_property(NEO4J_ADDRESS, node_id, property, value) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(append_property, node_id, property, value)
    driver.close()

def append_property(tx, node_id, key, value):
    tx.run("MATCH (n) WHERE ID(n) = $node_id SET n." + key + " = coalesce(n." + key + ", []) + $value "
    , node_id=node_id, value=value)


def set_node_property(NEO4J_ADDRESS, node_id, property, value) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(set_property, node_id, property, value)
    driver.close()

def set_property(tx, node_id, key, value):
    tx.run("MATCH (n) WHERE ID(n) = $node_id SET n." + key + " = $value"
    , node_id=node_id, value=value)


def get_OR_parents(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        OR_parent_list = session.read_transaction(OR_parents, node_id)
    driver.close()
    return OR_parent_list


def OR_parents(tx, node_id) : 
    return tx.run("""
    MATCH (n)-[:OR]->(m) WHERE ID(n)=$node_id 
    RETURN ID(m)
    """, node_id=node_id).value()


def get_AND_parents(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        AND_parent_list = session.read_transaction(AND_parents, node_id)
    driver.close()
    return AND_parent_list


def AND_parents(tx, node_id) : 
    return tx.run("""
    MATCH (n)-[:AND]->(m) WHERE ID(n)=$node_id 
    RETURN ID(m)
    """, node_id=node_id).value()


def get_weight_sum(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        temp = session.read_transaction(get_sum, node_id)
    driver.close()
    return temp


def get_sum(tx, node_id) : 
    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id 
    MATCH (m)-[*1]->(n) 
    RETURN SUM(m.weight)
    """, node_id=node_id).single().value()


def get_parent_node(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        temp = session.read_transaction(get_parent, node_id)
    driver.close()
    return temp


def get_parent(tx, node_id) : 
    temp = tx.run("""
    MATCH (n) WHERE ID(n)=$node_id 
    MATCH (n)-[*1]->(m) 
    RETURN {nodeID: ID(m), type: labels(m)[0], name: m.name}
    """, node_id=node_id).value()

    return temp[0] if temp else temp


def traverse_tree(NEO4J_ADDRESS, cont_id) : 

    # List of exploitable CVEs as dict
    CVEs = {}

    # List of tree nodes saved as dict
    tree_nodes = {}

    # Initialize Priority Queue (ordered by weights)
    pq = get_deployment_children(NEO4J_ADDRESS, cont_id)

    while len(pq) > 0 :

        current_node_id = pq.pop(0)

        # Add node to the tree dictionary
        if not current_node_id in tree_nodes : 
            tree_nodes[current_node_id] = get_node(NEO4J_ADDRESS, current_node_id)

        # If the parent node is the root, i.e., CVE node, append CVE to the list of CVEs
        parent_node = get_parent_node(NEO4J_ADDRESS, current_node_id)
        if parent_node and parent_node['type'] == 'CVE' : 
            needed = tree_nodes[current_node_id]['needed'] + [parent_node['nodeID']]
            # Check if the CVE is ignored for the current container
            ignored = check_ignored(NEO4J_ADDRESS, parent_node['name'], cont_id)
            CVEs[parent_node['name']] = {'name': parent_node['name'], 'path': needed, 'ignored': ignored}

        # If the current node has not been traversed yet
        if tree_nodes[current_node_id]['todo'] != 0 :
            # set TODO = 0
            tree_nodes[current_node_id]['todo'] = 0

            # Retrieve the list of OR parent nodes IDs
            OR_parent_list = get_OR_parents(NEO4J_ADDRESS, current_node_id)  
            for OR_parent_ID in OR_parent_list :

                if not OR_parent_ID in tree_nodes :
                    tree_nodes[OR_parent_ID] = get_node(NEO4J_ADDRESS, OR_parent_ID)

                # If the OR_parent node was not already traversed
                if tree_nodes[OR_parent_ID]['todo'] != 0 :

                    # If the path from the current node is more efficient than the previous path saved into the OR_parent
                    if tree_nodes[current_node_id]['weight'] > tree_nodes[OR_parent_ID]['weight'] :
                        tree_nodes[OR_parent_ID]['weight'] = tree_nodes[current_node_id]['weight']
                        tree_nodes[OR_parent_ID]['needed'] = tree_nodes[current_node_id]['needed'] + [current_node_id] + [tree_nodes[OR_parent_ID]['nodeID']]
                        tree_nodes[OR_parent_ID]['pred'] = current_node_id
                        # Finally, append the OR_parent to the priority queue list
                        if not OR_parent_ID in pq : pq.append(OR_parent_ID)

            # Retrieve the list of AND parent nodes
            AND_parent_list = get_AND_parents(NEO4J_ADDRESS, current_node_id)
            for AND_parent_ID in AND_parent_list :
                
                if not AND_parent_ID in tree_nodes :
                    tree_nodes[AND_parent_ID] = get_node(NEO4J_ADDRESS, AND_parent_ID)

                # Decrement AND_NODE TODO 
                tree_nodes[AND_parent_ID]['todo'] -= 1

                # If all AND_parent children have been traversed
                if tree_nodes[AND_parent_ID]['todo'] == 0 : 
                    # Needed nodes of AND_NODE are all children + all needed nodes of each children
                    needed = tree_nodes[AND_parent_ID]['children']

                    # For each child of the AND_NODE, append the needed children
                    for child in needed :
                        needed = list(set(needed + tree_nodes[child]['needed']))

                    tree_nodes[AND_parent_ID]['needed'] = needed 
                    tree_nodes[AND_parent_ID]['pred'] = current_node_id
                    tree_nodes[AND_parent_ID]['weight'] = get_weight_sum(NEO4J_ADDRESS, AND_parent_ID)

                    # Case in which the AND_node is the last node before the CVE node
                    parent_node = get_parent_node(NEO4J_ADDRESS, AND_parent_ID)
                    if parent_node and parent_node['type'] == 'CVE' : 
                        needed = tree_nodes[AND_parent_ID]['needed'] + [AND_parent_ID]
                        # Check if the CVE is ignored for the current container
                        ignored = check_ignored(NEO4J_ADDRESS, parent_node['name'], cont_id)
                        CVEs[parent_node['name']] = {'name': parent_node['name'], 'path': needed, 'ignored': ignored}

                    # Retrieve the list of OR parent nodes
                    OR_parent_list = get_OR_parents(NEO4J_ADDRESS, AND_parent_ID)
                    for OR_parent_ID in OR_parent_list :

                        if not OR_parent_ID in tree_nodes :
                            tree_nodes[OR_parent_ID] = get_node(NEO4J_ADDRESS, OR_parent_ID)

                        # If the OR_parent node was not already traversed
                        if tree_nodes[OR_parent_ID]['todo'] != 0 :

                            # Retrieve the update AND_parent Neo4J node
                            if not AND_parent_ID in tree_nodes :
                                tree_nodes[AND_parent_ID] = get_node(NEO4J_ADDRESS, AND_parent_ID)

                            if tree_nodes[AND_parent_ID]['weight'] > tree_nodes[OR_parent_ID]['weight'] :
                                # Update the OR_parent fields
                                tree_nodes[OR_parent_ID]['weight'] = tree_nodes[AND_parent_ID]['weight']
                                tree_nodes[OR_parent_ID]['needed'] = tree_nodes[AND_parent_ID]['children'] + [AND_parent_ID] + [tree_nodes[OR_parent_ID]['nodeID']]
                                tree_nodes[OR_parent_ID]['pred'] = AND_parent_ID
                                # Finally, append the OR_parent to the priority queue list
                                if not OR_parent_ID in pq : pq.append(OR_parent_ID)

    return CVEs

