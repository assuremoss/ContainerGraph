import time
import docker
import json
from neo4j import GraphDatabase
from ahp import apply_ahp, parse_ahp_weights
from colorama import Fore, Style


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))

def connect_to_Docker() : 
    return docker.from_env()


def get_all_cves(NEO4J_ADDRESS) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        return session.read_transaction(get_cves_names)

    
def get_cves_names(tx) :
    results = tx.run("MATCH (c:CVE) RETURN c.name ").data()

    CVEs = []
    for r in results : CVEs.append(r['c.name'])
    return CVEs


def evaluate_and(NEO4J_ADDRESS, and_node, cont_id) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    result = []
    for child in and_node['children'] : 
        result.append(evaluate_tree(NEO4J_ADDRESS, child, cont_id))
    
    for r in result :

        # Single chil
        if r and type(r[1]) == bool :
            if r[1] == False :
                return False
        
        # List of children
        elif r == False : 
            return False
        
    return and_node['nodeID'], (and_node['children'], True)


def evaluate_or(NEO4J_ADDRESS, or_node, cont_id) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    result = []
    for child in or_node['children'] : 
        result.append(evaluate_tree(NEO4J_ADDRESS, child, cont_id))
    
    aux = []
    for r in result :

        # Single child
        if r and type(r[1]) == bool :
            if r[1] == True :
                aux.append(r)
        
        # List of children
        elif r and True in r[1] : 
            aux.append(r)
        
    # If no child = True, return False
    return (or_node['nodeID'], aux) if aux else False


def evaluate_tree(NEO4J_ADDRESS, node_id, cont_id) :
    """  Check whether at least one valid path exists in the AND/OR tree
    
    Arguments:
    root_id - ID(CVE Neo4j root node)
    cont_id - ID(container)

    Description:
    Given the ID of the root node of an AND/OR tree, this function traverses the tree to check whether
    (at least one) valid path exists. By valid path we mean a set of leaves (one or more) that satisfy
    all the AND or OR conditions in the tree, up to the root node. If such a valid path exists, this 
    function returns true, false otherwise.
    """
    
    # Get the current node in the nodes dictionary
    current_node = get_node_dict(NEO4J_ADDRESS, node_id, cont_id)   

    # Skip ROOT node
    if current_node['type'] == 'CVE' : 
        return evaluate_tree(NEO4J_ADDRESS, current_node['children'][0], cont_id)

    # Process an AND_NODE
    elif current_node['type'] == 'AND_NODE' : 
        return evaluate_and(NEO4J_ADDRESS, current_node, cont_id)

    # Process an OR_NODE
    elif current_node['type'] == 'OR_NODE' : 
        return evaluate_or(NEO4J_ADDRESS, current_node, cont_id)

    # Process a leaf
    else : 
        if current_node['property'] : 
            return current_node['nodeID'], current_node['property']
        
        else : return False


def get_node_dict(NEO4J_ADDRESS, node_id, cont_id) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        return session.read_transaction(query_node, node_id, cont_id)

    
def query_node(tx, node_id, cont_id):
    """  brief title.
    
    Arguments:
    node_id - Neo4J node ID of the AND/OR vulnerability tree 

    Description:
    blablabla
    """

    # node_dict = tx.run(
    #     "MATCH (n) WHERE ID(n)=$node_id "
    #     "OPTIONAL MATCH (c)-[*1]->(n) "
    #     "WITH n, COLLECT(ID(c)) AS children "
    #     "RETURN {nodeID: ID(n), type: labels(n)[0], children: children} AS node_dict "
    #     , node_id=node_id).single().value()

    node_dict = tx.run(
        "MATCH (n) WHERE ID(n)=$node_id "
        "OPTIONAL MATCH (c)-[*1]->(n) "
        "WITH n, COLLECT(ID(c)) AS children "
        "RETURN {nodeID: ID(n), type: labels(n)[0], children: children, property: n.property='GREEN'} AS node_dict "
        , node_id=node_id).single().value()


    # # The 'property' is null for nodes that are not leaves
    # if node_dict['type'] == 'CVE' or \
    #     node_dict['type'] == 'AND_NODE' or \
    #      node_dict['type'] == 'OR_NODE' :
    #         node_dict['property'] = None

    # # otherwise, for leaves, retrieve the property value
    # else : 

    #     # Software version leaf
    #     if node_dict['type'] == 'KernelVersion' : 
    #         pass

    #     elif node_dict['type'] == 'DockerVersion' :
    #         pass

    #     elif node_dict['type'] == 'containerdVersion' :
    #         pass

    #     elif node_dict['type'] == 'runcVersion' :
    #         pass

    #     # Container field leaf
    #     else :
    #         node_dict['property'] = tx.run(
    #             "MATCH (c:Container {cont_id: $cont_id}) "
    #             "MATCH (n) WHERE ID(n)=$node_id "
    #             "RETURN EXISTS((c)-[:HAS*1..2]->(n)) ",
    #             cont_id=cont_id, node_id=node_id
    #             ).single().value()

    return node_dict


def get_cve_nodes(NEO4J_ADDRESS, cve) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        return session.read_transaction(query_cve_node, cve)


def query_cve_node(tx, cve) :  
    try:  
        return tx.run("MATCH (c:CVE {name: $cve}) RETURN ID(c) ", cve=cve).single().value()

    # Throw an error if the CVE name/id is does not exist in the graph
    except AttributeError as error:
        # print(error)
        print(cve + ' does not exist in the database! Exiting...')
        exit(1)


def query_vulnerability(NEO4J_ADDRESS, cont_id, cve) :
    """  brief title.
    
    Arguments:
    root_id - Neo4J node ID of the AND/OR vulnerability tree root node 

    Description:
    blablabla
    """

    try :
        # Standardize container ID
        # client = connect_to_Docker()
        # cont_id = client.containers.get(cont_id).short_id
        
        # Get the CVE node ID
        root_id = get_cve_nodes(NEO4J_ADDRESS, cve)

        # Traverse and evaluate the AND/OR vulnerability tree
        start = time.time()
        result = evaluate_tree(NEO4J_ADDRESS, root_id, cont_id)
        end = time.time()

        # The container is vulnerable
        if result : 
            print("The container is vulnerable to " + Fore.RED + cve + Style.RESET_ALL + "!")
            result = (root_id, result)
        else : 
            print(Fore.GREEN + "The container configuration is safe!" + Style.RESET_ALL)
        
        # Return algorithm execution time
        # print('Execution time: ' + str(round(end-start, 5)) + ' seconds.')

        return result
        
    # Raise an exception if the container doesn't exist
    except docker.errors.NotFound as error :
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)


def extract_path(result) : 
    """  brief title.
    
    Arguments:
    result - list of one or more valid paths extract from a vulnerability AND/OR tree

    Description:
    blablabla
    """

    # List of all valid paths (sublists)
    all_path = []

    # Current valid path to append to all_path list
    path = []

    for r in result :
        
        # If node, append to path list
        if type(r) == int :
            path.append(r)

        elif type(r) == tuple :
            path.append(r[0])
            
            if type(r[1]) == list : 
                # Single leaf
                if len(r[1]) == 1 : 
                    all_path.append(path + [r[1][0][0]])

                # Iterate over the list of leaves
                else :
                    for l in r[1] : 
                        all_path.append(path + [l[0]])

            elif r[1][1] == True : 
                all_path.append(path + [r[1][0]])
                         
    return all_path


def weight_path(NEO4J_ADDRESS, path) :
    """  Computes and returns the weight of an AND/OR tree valid path
    
    Arguments:
    path - list of node IDs representing a valid path in an AND/OR tree

    Description:
    blablabla
    """

    sum = 0

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        for node_id in path : 

            if type(node_id) == list : 
                for n_id in node_id : 
                    sum += session.read_transaction(query_node_weight, n_id)
            else :
                sum += session.read_transaction(query_node_weight, node_id)

    return sum
    

def query_node_weight(tx, node_id) : 

    # TODO
    # if the node is the root node, return CVSS 

    aux = tx.run("OPTIONAL MATCH (n) WHERE ID(n)=$node_id RETURN n.weight ", 
                    node_id=node_id).single().value()
    return aux if aux else 0


def get_leaf_type(NEO4J_ADDRESS, leaf_id) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
    with driver.session() as session:
        return session.read_transaction(retrieve_leaf_type, leaf_id)

def retrieve_leaf_type(tx, leaf_id) : 
    aux = tx.run("MATCH (n) WHERE ID(n)=$leaf_id RETURN labels(n)[0], n.name", leaf_id=leaf_id).values()[0]
    return aux[0], aux[1]


def print_fix(fix) : 

    if fix['fix'] == 'version_upgrade' :
        print(Fore.GREEN + "Upgrade " + Style.RESET_ALL + fix['value'] + " to a newer version.")

    elif fix['fix'] == 'not_privileged' : 
        print("Do not run the container with the privileged option: " + Fore.RED + "--privileged" + Style.RESET_ALL)

    elif fix['fix'] == 'not_root' :
        print("Run the container with the user option: " + Fore.GREEN + "--user UID:GID" + Style.RESET_ALL)

    elif fix['fix'] == 'not_capability' :
        print("Run the container with the option: " + Fore.GREEN + "--cap-drop " + fix['value'] + Style.RESET_ALL)

    elif fix['fix'] == 'not_syscall' :
        print("Add the following line to the container AppArmor profile: " + Fore.GREEN + "deny " + fix['value'] + Style.RESET_ALL)

    elif fix['fix'] == 'read_only_fs' :
        print("Run the container with the option: " + Fore.GREEN + "--read-only" + Style.RESET_ALL)

    elif fix['fix'] == 'no_new_priv' :
        print("Run the container with the option: " + Fore.GREEN + "--security-opt=no-new-privileges:true" + Style.RESET_ALL)


def suggest_fix(NEO4J_ADDRESS, all_results) : 
    """  Computes and returns the weight of an AND/OR tree valid path
    
    Arguments:
    path - list of node IDs representing a valid path in an AND/OR tree

    Description:
    blablabla
    """

    # Only one valid path
    if len(all_results) == 1 : 

        leaves = all_results[0]['path_0'][-1]

        # Single leaf
        if type(leaves) == int : 

            # Retrieve ``type'' of the leaf
            leaf_type, leaf_value = get_leaf_type(NEO4J_ADDRESS, leaves)

            # Based on the type, suggest the only possible fix
            if leaf_type == 'DockerVersion' or \
                leaf_type == 'containerdVersion' or \
                  leaf_type == 'runcVersion' or \
                      leaf_type == 'KernelVersion' :

                        # TODO
                        # Specify the minimum version to which you should upgrade
                        value = leaf_type[:-7]
                        fix = {'fix': 'version_upgrade', 'value': value}
                        print_fix(fix)

            elif leaf_value == 'PrivPermissions' :
                fix = {'fix': 'not_privileged'}
                print_fix(fix)

            else :
                # TODO
                print('TODO')

        # Multiple leaves - AND node
        elif type(leaves) == list :

            ahp_weights = parse_ahp_weights()
            ahp_fixes = []

            # Remove not relevant fixes
            for l in leaves : 
                leaf_type, leaf_value = get_leaf_type(NEO4J_ADDRESS, l)
                aux = {'type': leaf_type, 'value': leaf_value}
                
                if leaf_type == 'Privileged' : 
                    aux['weight'] = ahp_weights['not_privileged']
                    aux['fix'] = 'not_privileged'
                elif leaf_type == 'Capability' : 
                    aux['weight'] = ahp_weights['not_capability']
                    aux['fix'] = 'not_capability'
                elif leaf_type == 'SystemCall' : 
                    aux['weight'] = ahp_weights['not_syscall']
                    aux['fix'] = 'not_syscall'
                elif leaf_type == 'NotReadOnly' : 
                    aux['weight'] = ahp_weights['read_only_fs']
                    aux['fix'] = 'read_only_fs'
                elif leaf_type == 'NoNewPriv' : 
                    aux['weight'] = ahp_weights['no_new_priv']
                    aux['fix'] = 'no_new_priv'
                elif leaf_type == 'ContainerConfig' : 
                    # TODO
                    pass
                    
                ahp_fixes.append(aux)

            # Sort fixes by weights (returns a list)
            ahp_fixes = sorted(ahp_fixes, key=lambda d: d['weight'], reverse=True) 

            aws = 'n'
            # Iterate possible fixes
            for f in ahp_fixes : 

                if f['type'] == 'SystemCall' : 
                    aws = input("Accept " + f['fix'] + ' ' + f['value'] + " (y/n) ? ")

                elif f['type'] == 'Capability' : 
                    aws = input("Accept " + f['fix'] + ' ' + f['value'] + " (y/n) ? ")
                
                else :
                    aws = input("Accept " + f['fix'] + " (y/n) ? ")
                
                if aws == '' or aws == 'y' : 
                    print_fix(f)
                    break 

            if aws == 'n' : 
                print(Fore.RED + 'No fix has been choosen! ' + Style.RESET_ALL + 'Exiting...')        

    # AHP : Multiple valid paths with multiple possible fixes
    else :
        fix = apply_ahp(all_results)
        # print(fix)


def fix_deployment(NEO4J_ADDRESS, cve) :
    """  Computes and returns the weight of an AND/OR tree valid path
    
    Arguments:
    path - list of node IDs representing a valid path in an AND/OR tree

    Description:
    blablabla
    """

    result = query_vulnerability(NEO4J_ADDRESS, '', cve)

    if not result : 
        return

    # TODO Fix this function
    # make it recursive
    all_path = extract_path(result)

    all_results = []
    for i, path in enumerate(all_path) : 
        w = weight_path(NEO4J_ADDRESS, path)
        aux = {'cve': cve, 'path_' + str(i): path, 'risk': w}
        all_results.append(aux)

    print(all_results)
    suggest_fix(NEO4J_ADDRESS, all_results)


### CUSTOM FUNCTION ###
NEO4J_ADDRESS = '192.168.2.5'
cve = 'CVE_1'
fix_deployment(NEO4J_ADDRESS, cve)
