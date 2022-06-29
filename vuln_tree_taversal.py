import docker
from neo4j import GraphDatabase
from pyparsing import empty

def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))

def connect_to_Docker() : 
    return docker.from_env()


def get_deployment_children(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        leaves = session.read_transaction(query_dep, node_id)
    driver.close()

    return leaves

    
def query_dep(tx, node_id):
    """  brief title.
    
    Arguments:
    node_id - Neo4J node ID of the AND/OR vulnerability tree 

    Description:
    blablabla
    """

    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id
    MATCH (n)-[*1..3]->(c {tree: 'leaf'}) 
    WHERE EXISTS((c)-[:AND]->(:AND_NODE)) OR EXISTS((c)-[:OR]->(:OR_NODE))
    WITH DISTINCT c
    ORDER BY c.weight DESC 
    WITH COLLECT(ID(c)) AS children
    RETURN children
    """, node_id=node_id).value()[0]


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
    MATCH (n) WHERE ID(n)=$node_id 
    MATCH (n)-[:OR]->(m)
    RETURN {nodeID: ID(m), needed: m.needed, pred: m.pred, todo: m.todo, weight: m.weight} 
    """, node_id=node_id).value()


def get_AND_parents(NEO4J_ADDRESS, node_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        AND_parent_list = session.read_transaction(AND_parents, node_id)
    driver.close()
    return AND_parent_list


def AND_parents(tx, node_id) : 
    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id 
    MATCH (n)-[:AND]->(m)
    MATCH (c)-[:AND]->(m) 
    WITH m, COLLECT(ID(c)) AS children
    RETURN {nodeID: ID(m), children: children, needed: m.needed, pred: m.pred, todo: m.todo, weight: m.weight} 
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


def traverse_tree(NEO4J_ADDRESS, node_id) : 

    # List of exploitable CVEs
    CVEs = []

    # Initialize Priority Queue (ordered by weights)
    pq = get_deployment_children(NEO4J_ADDRESS, node_id)

    while len(pq) > 0 :

        current_node_id = pq.pop(0)

        # Retrieve Neo4J node
        current_node = get_node(NEO4J_ADDRESS, current_node_id)

        # If the parent node is the root, i.e., CVE node, update the path and weight, and exit
        parent_node = get_parent_node(NEO4J_ADDRESS, current_node_id)
        if parent_node and parent_node['type'] == 'CVE' : 
            temp = {'CVE': parent_node['name'], 'path': current_node['needed']}
            CVEs.append(temp)

        # If the current node has not been traversed yet
        if current_node['todo'] != 0 :
            # set TODO = 0
            set_node_property(NEO4J_ADDRESS, current_node_id, 'todo', 0)

            # Retrieve the list of OR parent nodes
            OR_parent_list = get_OR_parents(NEO4J_ADDRESS, current_node_id)  
            for OR_parent in OR_parent_list :
                # If the OR_parent node was not already traversed
                if OR_parent['todo'] != 0 :
                    # If the path from the current node is more efficient than the previous path saved into the OR_parent
                    if current_node['weight'] > OR_parent['weight'] :
                        # Update the OR_parent fields
                        set_node_property(NEO4J_ADDRESS, OR_parent['nodeID'], 'weight', current_node['weight'])
                        needed = current_node['needed'] + [current_node_id]
                        set_node_property(NEO4J_ADDRESS, OR_parent['nodeID'], 'needed', needed)
                        set_node_property(NEO4J_ADDRESS, OR_parent['nodeID'], 'pred', current_node_id)
                        # Finally, append the OR_parent to the priority queue list
                        pq.append(OR_parent['nodeID'])

            # Retrieve the list of AND parent nodes
            AND_parent_list = get_AND_parents(NEO4J_ADDRESS, current_node_id)
            for AND_parent in AND_parent_list :
                # Decrement the TODO of the current AND_parent
                set_node_property(NEO4J_ADDRESS, AND_parent['nodeID'], 'todo', AND_parent['todo']-1)
                # Also, update the ``local'' weight in the Python dict of the AND_parent node
                AND_parent['todo'] -= 1

                # If all AND_parent children have been traversed
                if AND_parent['todo'] == 0 : 
                    # Update the AND_parent fields
                    set_node_property(NEO4J_ADDRESS, AND_parent['nodeID'], 'weight', get_weight_sum(NEO4J_ADDRESS, AND_parent['nodeID']))
                    set_node_property(NEO4J_ADDRESS, AND_parent['nodeID'], 'needed', AND_parent['children']) 
                    set_node_property(NEO4J_ADDRESS, AND_parent['nodeID'], 'pred', current_node_id)

                    # Case in which the AND_node is the last node before the CVE node
                    parent_node = get_parent_node(NEO4J_ADDRESS, current_node_id)
                    if parent_node and parent_node['type'] == 'CVE' : 
                        # If the parent node is the root, i.e., CVE node, update the path and weight, and exit
                        parent_node = get_parent_node(NEO4J_ADDRESS, current_node_id)
                        if parent_node and parent_node['type'] == 'CVE' : 
                            temp = {'CVE': parent_node['name'], 'path': current_node['needed']}
                            CVEs.append(temp)

                    # Retrieve the list of OR parent nodes
                    OR_parent_list = get_OR_parents(NEO4J_ADDRESS, AND_parent['nodeID'])
                    for OR_parent in OR_parent_list :
                        # If the OR_parent node was not already traversed
                        if OR_parent['todo'] != 0 :
                            # Retrieve the update AND_parent Neo4J node
                            AND_parent = get_node(NEO4J_ADDRESS, AND_parent['nodeID'])
                            if AND_parent['weight'] > OR_parent['weight'] :
                                # Update the OR_parent fields
                                set_node_property(NEO4J_ADDRESS, OR_parent['nodeID'], 'weight', AND_parent['weight'])
                                needed = AND_parent['children'] + [AND_parent['nodeID']]
                                set_node_property(NEO4J_ADDRESS, OR_parent['nodeID'], 'needed', needed)
                                set_node_property(NEO4J_ADDRESS, OR_parent['nodeID'], 'pred', AND_parent['nodeID'])
                                # Finally, append the OR_parent to the priority queue list
                                pq.append(OR_parent['nodeID'])

    # At the end of each algorithm run, re-initialize the TODOs and WEIGHTs into the graph
    reinitialize_fields(NEO4J_ADDRESS)

    return CVEs


def reinitialize_fields(NEO4J_ADDRESS) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(initialize_tree)
    driver.close()


def initialize_tree(tx) :

    # Reinitialize AND_NODEs
    tx.run("""
    MATCH (a:AND_NODE)
    MATCH (n)-[:AND]->(a) 
    WITH a, COUNT(n) as nchildren
    SET a.todo = nchildren
    SET a.weight = 0
    """)

    # Reinitialize OR_NODEs
    tx.run("""
    MATCH (o:OR_NODE)
    SET o.todo = 1
    SET o.weight = -gds.util.infinity()
    """)

    # Reinitialize leaves
    leaves = tx.run("""
    MATCH (d:Deployment)
    MATCH (d)-[*1]->(l) 
    SET l.todo = 1
    RETURN ID(l)
    """).value()

    for l in leaves : 
        aux = tx.run("""
        MATCH (n) WHERE ID(n)=$id
        RETURN EXISTS((:Container)-[:HAS*1..2]->(n)) OR EXISTS((:LinuxHost)-[:USES*1]->(n)) OR EXISTS((:DockerEngine)-[:USES*1]->(n)) OR EXISTS((:DockerVersion)-[:USES*1]->(n))
        """, id=l).single().value()

        if aux : 

            weight = tx.run("MATCH (n) WHERE ID(n)=$id RETURN n.weight", id=l).single().value()
            if weight < 0 :
                tx.run("""
                MATCH (n) WHERE ID(n)=$id
                SET n.weight = 1
                """, id=l)
        else : 
            tx.run("""
            MATCH (n) WHERE ID(n)=$id
            SET n.weight = -gds.util.infinity()
            """, id=l)

