from Neo4j_connection import connect_to_neo4j
from colorama import Fore, Style
from build_host_Neo4j import host_exploits
from build_cont_Neo4j import create_cont_exploit_rel
from parse_Seccomp import seccomp_parser, analyze_syscalls
from parse_Apparmor import apparmor_parser


def get_node(node_id) :
    """Returns a dict representation of the Neo4j node with ID equal to node_id.
    
    Parameters
    ----------
    node_id : ID of the Neo4j node to be returned.

    Return
    ----------
    node : dict representing the Neo4j node (with nodeID, name, type, etc.)
    """ 

    driver = connect_to_neo4j()
    with driver.session() as session:
        node = session.read_transaction(tree_node, node_id)
    driver.close()
    return node


def tree_node(tx, node_id):

    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id AND ( EXISTS(()-[:EXPLOITS]->(n)) OR EXISTS(()-[:OR]->(n)) OR EXISTS(()-[:AND]->(n)) )
    OPTIONAL MATCH (c)-[*1]->(n) 
    WITH n, COLLECT(DISTINCT ID(c)) AS children 
    RETURN {nodeID: ID(n), name: n.name, type: labels(n)[0], children: children, needed: n.needed, pred: n.pred, todo: n.todo, weight: n.weight} AS node_dict 
    """, node_id=node_id).value()[0]


def get_parent_node(node_id) :
    """Returns the parent node of the node with ID=node_id.
    
    Parameters
    ----------
    node_id : ID of a Neo4j node.

    Return
    ----------
    parent : dict representing the Neo4j parent node (with nodeID, type, and name).
    """ 
 
    driver = connect_to_neo4j()
    with driver.session() as session:
        temp = session.read_transaction(get_parent, node_id)
    driver.close()
    return temp


def get_parent(tx, node_id) : 
    parent = tx.run("""
    MATCH (n)-[*1]->(m) WHERE ID(n)=$node_id 
    RETURN {nodeID: ID(m), type: labels(m)[0], name: m.name}
    """, node_id=node_id).value()
    return parent[0] if parent else parent


def get_OR_parents(node_id) :
    driver = connect_to_neo4j()
    with driver.session() as session:
        OR_parent_list = session.read_transaction(OR_parents, node_id)
    driver.close()
    return OR_parent_list


def OR_parents(tx, node_id) : 
    return tx.run("""
    MATCH (n)-[:OR]->(m) WHERE ID(n)=$node_id 
    RETURN ID(m)
    """, node_id=node_id).value()


def get_AND_parents(node_id) :
    driver = connect_to_neo4j()
    with driver.session() as session:
        AND_parent_list = session.read_transaction(AND_parents, node_id)
    driver.close()
    return AND_parent_list


def AND_parents(tx, node_id) : 
    return tx.run("""
    MATCH (n)-[:AND]->(m) WHERE ID(n)=$node_id 
    RETURN ID(m)
    """, node_id=node_id).value()


def get_weight_sum(node_id) :
    driver = connect_to_neo4j()
    with driver.session() as session:
        temp = session.read_transaction(get_sum, node_id)
    driver.close()
    return temp


def get_sum(tx, node_id) : 
    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id 
    MATCH (m)-[:AND*1]->(n) 
    RETURN SUM(m.weight)
    """, node_id=node_id).single().value()


def get_leaves_list(tx, path) :
    leaves = []
    for node in path : 
        temp_dict = tx.run("""
        MATCH (n) WHERE ID(n)=$node_id
        RETURN {nodeID: ID(n), name: n.name, tree: n.tree, type: labels(n)[0]}
        """, node_id=node).value()[0]

        if temp_dict['tree'] == 'leaf' : 
            leaves.append(temp_dict)
    return leaves


def get_vulnerable_cont(tx, leaves_list) :

    cont_dict = {}
    for leaf in leaves_list : 
        temp =  tx.run("""
        MATCH (c:Container:Docker)-[:EXPLOITS]->(l)
        WHERE ID(l)=$leaf_id
        RETURN {nodeID: ID(c), cont_id: c.cont_id} 
        """, leaf_id=leaf['nodeID']).value()
        
        for n in temp : 
            if n['nodeID'] not in cont_dict : 
                cont_dict[n['nodeID']] = n

    return cont_dict


def check_ignored(tx, node_id, cve_name) :
    return tx.run("""
    MATCH (n) WHERE ID(n)=$node_id
    MATCH (cve:CVE {name:$cve_name})
    RETURN EXISTS( (n)-[:IGNORES]->(cve) )
    """, node_id=node_id, cve_name=cve_name).single().value()


def create_ignore_node(node_id, cve_name) : 
    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(create_ignore, node_id, cve_name)
    driver.close()


def create_ignore(tx, node_id, cve_name) :
    tx.run("""
    MATCH (n) WHERE ID(n)=$node_id
    MATCH (cve:CVE {name:$cve_name})
    MERGE (n)-[:IGNORES]->(cve)
    """, node_id=node_id, cve_name=cve_name)


def remove_engine_edge(tx, leaf_id, fix_dict) :
    # Remove *_v-[:EXPLOITS :HAS_PROPERTY]-(leaf) edge
    tx.run("""
    MATCH (eng)-[r:HAS_PROPERTY]->(l) 
    WHERE ID(l)=$leaf_id AND EXISTS( (eng)-[:EXPLOITS]->(l) )
    DELETE r 
    """, leaf_id=leaf_id)

    engine_id = tx.run("""
    MATCH (eng)-[r:EXPLOITS]->(l) WHERE ID(l)=$leaf_id
    DELETE r RETURN ID(eng)
    """, leaf_id=leaf_id).single().value()

    # Create new edge to the new selected version
    fix = fix_dict[list(fix_dict.keys())[0]]
    query = "MATCH (eng) WHERE ID(eng)=$engine_id "
    query += "MATCH (l:" + fix['type'] + 'Version' +" {name: $new_v}) "
    query += "MERGE (eng)-[:HAS_PROPERTY]->(l) " 
    tx.run(query, engine_id=engine_id, new_v=fix['new_version'])  

    new_v_id = tx.run("MATCH (l:" + fix['type'] + 'Version' +" {name: $new_v}) RETURN ID(l)", new_v=fix['new_version'])

    # Check whether the new selected version is supported in Neo4J
    if not new_v_id.peek() : 
        print('The new selected version is not currently supported! Exiting...')
        exit(1)
    
    return engine_id, new_v_id.single().value()


def remove_cont_edge(tx, node_id, list_of_fixes) :

    cont_id = tx.run("MATCH (n) WHERE ID(n)=$node_id RETURN n.cont_id", node_id=node_id).single().value()
    fix_dict = {'perm': [], 'syscalls': [], 'caps': [], 'cont_id': cont_id}
    
    for leaf in list_of_fixes : 
        leaf_id = list(leaf.keys())[0]
        tx.run("""
            MATCH (c {cont_id: $cont_id})-[r:EXPLOITS]->(l)
            WHERE ID(l)=$leaf_id
            DELETE r
            """, cont_id=cont_id, leaf_id=leaf_id)

        if leaf[leaf_id]['fix'] == 'not_syscall' :
            tx.run("""
            MATCH (p {container: $cont_id})-[r:HAS_PROPERTY]->(l)
            WHERE ID(l)=$leaf_id
            DELETE r
            """, cont_id=cont_id, leaf_id=leaf_id)
            fix_dict['syscalls'].append(leaf_id)
        
        elif leaf[leaf_id]['fix'] == 'not_capability' :
            tx.run("""
            MATCH (p {container: $cont_id})-[r:HAS_PROPERTY]->(l)
            WHERE ID(l)=$leaf_id
            DELETE r
            """, cont_id=cont_id, leaf_id=leaf_id)
            fix_dict['caps'].append(leaf_id)
        
        else : # standard properties (e.g., root, read-only)
            tx.run("""
            MATCH (p:Permissions {container: $cont_id})-[r:HAS_PROPERTY]->(l)
            WHERE ID(l)=$leaf_id
            DELETE r
            """, cont_id=cont_id, leaf_id=leaf_id)
            fix_dict['perm'].append(leaf_id)

    return fix_dict


def remove_privcont_edge(tx, node_id, fix) :

    priv_id = list(fix.keys())[0]
    
    tx.run("""
    MATCH (c)-[r:EXPLOITS]->()
    WHERE ID(c)=$node_id 
    DELETE r
    UNION
    MATCH (c)-[:HAS]->(:Permissions)-[r:HAS_PROPERTY]->()
    WHERE ID(c)=$node_id
    DELETE r
    """, node_id=node_id, priv_id=priv_id)
    
    cont_id = tx.run("MATCH (c) WHERE ID(c)=$node_id RETURN c.cont_id", node_id=node_id).single().value()

    Seccomp_p = seccomp_parser()
    AppArmor_p = apparmor_parser()

    a_s, _ = analyze_syscalls(Seccomp_p, AppArmor_p.caps)
    a_syscalls = a_s + AppArmor_p.a_syscalls
    
    # Unsupported or not-default system calls
    d_syscalls = ['mount', 'close_range', 'faccessat2', 'openat2']
    a_syscalls = list(filter(lambda s : s not in d_syscalls, a_syscalls))
    
    tx.run("""
    MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
    SET p.profile = 'docker-default'
    """, cont_id=cont_id)

    tx.run("""
    MERGE (aa:AppArmor {name: 'AppArmor', container: $cont_id, object: 'Container'})
    MERGE (sc:SecComp {name: 'SecComp', container: $cont_id, object: 'Container'})
    UNION
    MATCH (p:Permissions {name: 'Permissions', container: $cont_id})  
    MATCH (aa:AppArmor {name: 'AppArmor', container: $cont_id}) 
    MERGE (p)-[:HAS_PROPERTY]->(aa)
    UNION
    MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
    MATCH (sc:SecComp {name: 'SecComp', container: $cont_id})
    MERGE (p)-[:HAS_PROPERTY]->(sc)
    """, cont_id=cont_id)

    for cap in AppArmor_p.caps :
        tx.run("""
        MATCH (aa:AppArmor {name: 'AppArmor', container: $cont_id}) 
        MATCH (c:Capability {name: $name})
        MERGE (aa)-[:HAS_PROPERTY]->(c)
        """, cont_id=cont_id, name=cap)

    for syscall in a_syscalls : 
        tx.run("""
        MATCH (sc:SecComp {name: 'SecComp', container: $cont_id}) 
        MATCH (s:SystemCall {name: $name})
        MERGE (sc)-[:HAS_PROPERTY]->(s)
        """, cont_id=cont_id, name=syscall)   

    tx.run("""
    MATCH (ro:NotReadOnly) 
    MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
    MERGE (p)-[:HAS_PROPERTY]->(ro)  
    UNION
    MATCH (np:NewPriv {name: 'NewPriv', object: 'Container'}) 
    MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
    MERGE (p)-[:HAS_PROPERTY]->(np)  
    UNION
    MATCH (cc:ContainerConfig {name: 'root'})
    MATCH (p:Permissions {name: 'Permissions', container: $cont_id})
    MERGE (p)-[:HAS_PROPERTY]->(cc)  
    """, cont_id=cont_id)   

    # Return the container ID
    return cont_id


def implement_fixes(node_id, list_of_fixes) :
    removed_edges_dict = {}
    cont_id = ''

    driver = connect_to_neo4j()
    with driver.session() as session:

        # Remove the :EXPLOITS and :HAS_PROPERTY edges to each leaf to which the container/engine is connected
        # Eventually, create a new :HAS_PROPERTY edge and check for :EXPLOITS
        for leaf in list_of_fixes : 
            leaf = leaf[list(leaf.keys())[0]]
            if leaf['type'] == 'Docker' or \
                leaf['type'] == 'containerd' or \
                leaf['type'] == 'runc' or \
                    leaf['type'] == 'Kernel' :
                        engine_id, new_v = session.write_transaction(remove_engine_edge, node_id, list_of_fixes[0])
                        session.write_transaction(host_exploits)
                        removed_edges_dict[node_id] = {'engine_id': engine_id, 'old_v_id': node_id, 'new_v_id': new_v, 'type': 'engine'}
                            
            # Remove the Privileged node and create a default permission configuration
            elif leaf['type'] == 'Privileged' :
                fix = list_of_fixes[0] # there is only one possible fix, i.e., removing the --privileged flag
                cont_id = session.write_transaction(remove_privcont_edge, node_id, fix)
                removed_edges_dict[node_id] = {'cont_id': cont_id, 'type': 'privileged'}
            
            else : # Remove edge between container and leaf
                temp_dict = session.write_transaction(remove_cont_edge, node_id, list_of_fixes)
                temp_dict = {**temp_dict, 'type': 'container'}
                removed_edges_dict[node_id] = temp_dict
                cont_id = temp_dict['cont_id']
    driver.close()

    with driver.session() as session:
        session.write_transaction(create_cont_exploit_rel, cont_id)
    driver.close()

    return removed_edges_dict


def suggest_fix(leaves_list, cont_id) : 
    # Keep track of which leaves and fixes were selected
    choosen_fixes =[]
    for leaf in leaves_list :
        temp_d = None

        if leaf['type'] == 'DockerVersion' or \
            leaf['type'] == 'containerdVersion' or \
            leaf['type'] == 'runcVersion' or \
                leaf['type'] == 'KernelVersion' :
                    aws = input('Do you want to upgrade the ' + leaf['type'].strip('Version') + ' version [Y/n] ? ')
                    if aws == 'Y' : 
                        new_v = input('Insert the new version (e.g., 5.5): ')
                        output = "Upgrade the " + leaf['type'][:-7] + " to version " + new_v
                        temp_d = {leaf['nodeID']: {'fix': 'version_upgrade', 'type': leaf['type'].strip('Version'), 'version': leaf['name'], 'new_version': new_v, 'output': output}}
                        
        elif leaf['type'] == 'Permissions' and leaf['name'] == 'Privileged' :
            aws = input('Do you want to run the container as privileged [y/N] ? ')
            if aws == 'N' : 
                temp_d = {'fix': 'not_privileged', 'type': 'Privileged'}
                output_d = {'output': print_fix(temp_d, cont_id)}
                temp_d.update(output_d)
                temp_d = {leaf['nodeID']: temp_d}
        
        elif leaf['type'] == 'SystemCall' : 
            aws = input('Do you need the ' + leaf['name'] + ' system call [y/N] ? ')
            if aws == 'N' : 
                temp_d = {'fix': 'not_syscall', 'type': leaf['name']}
                output_d = {'output': print_fix(temp_d, cont_id)}
                temp_d.update(output_d)
                temp_d = {leaf['nodeID']: temp_d}

        elif leaf['type'] == 'Capability' : 
            aws = input('Do you need the ' + leaf['name'] + ' capability [y/N] ? ')
            if aws == 'N' : 
                temp_d = {'fix': 'not_capability', 'type': leaf['name']}
                output_d = {'output': print_fix(temp_d, cont_id)}
                temp_d.update(output_d)
                temp_d = {leaf['nodeID']: temp_d}

        elif leaf['type'] == 'ContainerConfig' : 
            if leaf['name'] == 'root' :
                aws = input('Do you want to run the container as root [y/N] ? ')
                if aws == 'N' : 
                    temp_d = {'fix': 'not_root', 'type': ''}
                    output_d = {'output': print_fix(temp_d, cont_id)}
                    temp_d.update(output_d)
                    temp_d = {leaf['nodeID']: temp_d}

                # elif
                # TODO
                # volumes, env, etc.

        elif leaf['type'] == 'NewPriv' : 
            aws = input('Do you want the container to gain additional privileges [y/N] ? ')
            if aws == 'N' : 
                temp_d = {'fix': 'no_new_priv', 'type': ''}
                output_d = {'output': print_fix(temp_d, cont_id)}
                temp_d.update(output_d)
                temp_d = {leaf['nodeID']: temp_d}

        elif leaf['type'] == 'NotReadOnly' : 
            aws = input('Do you need write access to the filesystem [y/N] ? ')
            if aws == 'N' : 
                temp_d = {'fix': 'read_only_fs', 'type': ''}
                output_d = {'output': print_fix(temp_d, cont_id)}
                temp_d.update(output_d)
                temp_d = {leaf['nodeID']: temp_d}

        if temp_d : choosen_fixes.append(temp_d)

    return choosen_fixes


def print_fix(fix, cont_id) : 
    if fix['fix'] == 'not_privileged' : 
        return "Do not run container " + cont_id + " with the privileged option: --privileged"

    elif fix['fix'] == 'not_root' :
        return "Run container " + cont_id + " with the user option: --user UID:GID"

    elif fix['fix'] == 'not_capability' :
        return "Run container " + cont_id + " with the option: --cap-drop " + fix['type']

    elif fix['fix'] == 'not_syscall' :
        return "Add the following line to container " + cont_id + " AppArmor profile: deny " + fix['type']

    elif fix['fix'] == 'read_only_fs' :
        return "Run container " + cont_id + " with the option: --read-only"

    elif fix['fix'] == 'no_new_priv' :
        return "Run container " + cont_id + " with the option: --security-opt=no-new-privileges:true"


def fix_vuln(cve_name, leaves_list, node_id, cont_id=0) :

    # Provide the user a list of possible fixes for the current CVE
    list_of_fixes = suggest_fix(leaves_list, str(cont_id))

    # If no fix was choosen
    if not list_of_fixes : 
        create_ignore_node(node_id, cve_name)
        print(Fore.RED + cve_name + " will be ignored! Continuing..." + Style.RESET_ALL)

    # Implement the selected fixes, i.e., removing the :EXPLOITS edge 
    removed_edges_dict = implement_fixes(node_id, list_of_fixes)

    return list_of_fixes, removed_edges_dict


def update_new_v(tx, label, new_v) : 
    tx.run("MATCH (v:" + label + " {name:$new_v}) SET v.weight=1", new_v=new_v)

def get_v_ID(tx, label, new_v) : 
    return tx.run("MATCH (v:" + label + " {name:$new_v}) RETURN ID(v)", new_v=new_v).single().value()
                
def get_version_ID(label, new_v) : 
    driver = connect_to_neo4j()
    with driver.session() as session:
        session.read_transaction(get_v_ID, label, new_v)
    driver.close()


def reached_CVE(cve_name, path) : 
    """Desc ...
    """ 
    driver = connect_to_neo4j()
    with driver.session() as session:

        fix_dict = {}
        removed_edges_dict = {}
        
        # Get list of leaves dictionaries from the path
        leaves_list = session.read_transaction(get_leaves_list, path)
        # Retrieve vulnerable container configurations
        vulnerable_cont = session.read_transaction(get_vulnerable_cont, leaves_list)

        # Retrieve, if exists, the Engine leaf
        eng_dict = list(filter(lambda item : item['type'][-7:] == 'Version', leaves_list))
        if eng_dict :
            eng_dict = eng_dict[0]
            eng = eng_dict['type'][:-7]
            leaves_list.remove(eng_dict)

            # Check whether the engine ignores this CVE
            if session.read_transaction(check_ignored, eng_dict['nodeID'], cve_name) :
                print(Fore.RED +"This " + eng + " (v. " + eng_dict['name'] + ") ignores " + cve_name + "! Continuing..." + Style.RESET_ALL)
                session.write_transaction(create_ignore, eng_dict['nodeID'], cve_name)

            # Otherwise, ask to fix it
            else : 
                if eng == 'Kernel' : eng = 'the Linux Kernel'

                if vulnerable_cont :
                    qst = "Do you want to fix " + cve_name + " affecting " + eng + " (and container config.) [Y/n] ? "
                else : 
                    qst = "Do you want to fix " + cve_name + " affecting " + eng + " [Y/n] ? "

                aws = input(qst)
                if aws == 'Y' : 
                    list_of_fixes, removed_edges_dict = fix_vuln(cve_name, [eng_dict], eng_dict['nodeID'])
                    if list_of_fixes : # If the engine was fixes, return
                        driver.close()
                        session.write_transaction(update_new_v, eng_dict['type'], list_of_fixes[0][eng_dict['nodeID']]['new_version'])
                        new_v_ID = session.read_transaction(get_v_ID, eng_dict['type'], list_of_fixes[0][eng_dict['nodeID']]['new_version'])
                        return list_of_fixes, removed_edges_dict, new_v_ID
                
                else :
                    session.write_transaction(create_ignore, eng_dict['nodeID'], cve_name)
                    print(Fore.RED + cve_name + " will be ignored! Continuing..." + Style.RESET_ALL)

        # Check if the CVE is a false positive
        if not vulnerable_cont : 
            driver.close()
            return fix_dict, removed_edges_dict, ''

        # Otherwise, iterate over the vulnerable containers
        for cont in vulnerable_cont :            
            cont = vulnerable_cont[cont]           
            # Check if this container ignores this CVE
            if session.read_transaction(check_ignored, cont['nodeID'], cve_name) :
                print(Fore.RED +"The container with ID " + cont['cont_id'] + " ignores " + cve_name + "! Continuing..." + Style.RESET_ALL)
                continue
            
            aws = input("Do you want to fix " + cve_name + " for container " + cont['cont_id'] + " [Y/n] ? ")
            if aws == 'Y' : 
                list_of_fixes, removed_edges_dict = fix_vuln(cve_name, leaves_list, cont['nodeID'], cont['cont_id'])
                if list_of_fixes :
                    fix_dict.update(list_of_fixes)
                  
            else :
                session.write_transaction(create_ignore, cont['nodeID'], cve_name)
                print(Fore.RED + cve_name + " will be ignored! Continuing..." + Style.RESET_ALL)

    driver.close()
    return fix_dict, removed_edges_dict, ''


def updateTree(leaf_id, path, tree_nodes) :
    tree_nodes = tree_nodes
    
    # Initialize the PQ
    PQ = [leaf_id]

    while len(PQ) > 0 :
        current_node_id = PQ.pop(0)

        if tree_nodes[current_node_id]['type'] == 'CVE' : 
            break

        # Update the current node properties
        tree_nodes[current_node_id]['todo'] = 1 
        tree_nodes[current_node_id]['needed'] = [] 
        tree_nodes[current_node_id]['pred'] = float("NaN")
        tree_nodes[current_node_id]['weight'] = -float('Inf')

        # Traverse OR_parent nodes
        OR_parent_list = get_OR_parents(current_node_id)  
        for OR_parent_ID in OR_parent_list :

            if OR_parent_ID in path and not OR_parent_ID in PQ :
                PQ.append(OR_parent_ID)

        # Traverse AND_parent nodes
        AND_parent_list = get_AND_parents(current_node_id)
        for AND_parent_ID in AND_parent_list :

            if AND_parent_ID in path :
                
                tree_nodes[AND_parent_ID]['todo'] += 1 
                tree_nodes[AND_parent_ID]['needed'] = [] 
                tree_nodes[AND_parent_ID]['pred'] = float("NaN")
                tree_nodes[AND_parent_ID]['weight'] = 0

                # Case in which the AND_node is the last node before the CVE node
                parent_node = get_parent_node(AND_parent_ID)
                if parent_node and parent_node['type'] == 'CVE' :
                    break

                # Retrieve the list of OR parent nodes
                OR_parent_list = get_OR_parents(AND_parent_ID)
                for OR_parent_ID in OR_parent_list :

                    if OR_parent_ID in path and not OR_parent_ID in PQ :
                        PQ.append(OR_parent_ID)

    return tree_nodes


def traverse_tree(PQ) :
    """Traverses all CVE trees, bottom-up, to check whether a path from a set of leaves
    up to the CVE root node exists (i.e., given the current configuration, that CVE is exploitable).

    If such a path is found, it will ask the user whether he/she wants to fix the CVE or not.
    
    Parameters
    ----------
    PQ : priority queue, implemented as a list of int, containing all leaves IDs.
    """ 

    # List of all fixes
    list_of_fixes = []
    removed_edges_dict = {}

    # Dict of tree nodes saved locally
    tree_nodes = {}

    while len(PQ) > 0 :
        current_node_id = PQ.pop(0)

        # Add node to the tree dictionary
        if not current_node_id in tree_nodes : 
            tree_nodes[current_node_id] = get_node(current_node_id)

        # If the current node has not been traversed yet
        if tree_nodes[current_node_id]['todo'] != 0 :
            tree_nodes[current_node_id]['todo'] = 0

        # Check whether we reached a CVE node
        parent_node = get_parent_node(current_node_id)
        if parent_node and parent_node['type'] == 'CVE' : 
            path = tree_nodes[current_node_id]['needed'] + [parent_node['nodeID']]
            fix_temp, removed_edges_temp, new_v = reached_CVE(parent_node['name'], path)
            if fix_temp : 

                for fix in fix_temp :    
                    tree_nodes = updateTree(list(fix.keys())[0], path, tree_nodes)

                list_of_fixes += fix_temp
                removed_edges_dict.update(removed_edges_temp)
                
                if new_v : PQ.append(new_v)
                continue

        # Retrieve the list of OR parent nodes IDs
        OR_parent_list = get_OR_parents(current_node_id)  
        for OR_parent_ID in OR_parent_list :
            # Eventually add the OR_node to the dict
            if not OR_parent_ID in tree_nodes :
                tree_nodes[OR_parent_ID] = get_node(OR_parent_ID)            

            # if the path from the current node is more risky than the previous path saved into the OR_parent
            if tree_nodes[current_node_id]['weight'] > tree_nodes[OR_parent_ID]['weight'] :
                tree_nodes[OR_parent_ID]['weight'] = tree_nodes[current_node_id]['weight']
                tree_nodes[OR_parent_ID]['needed'] = tree_nodes[current_node_id]['needed'] + [current_node_id] + [OR_parent_ID]
                tree_nodes[OR_parent_ID]['pred'] = current_node_id

                # If not in the PQ already, append the OR_node id
                if not OR_parent_ID in PQ : 
                    PQ.append(OR_parent_ID)

        # Retrieve the list of AND parent nodes
        AND_parent_list = get_AND_parents(current_node_id)
        for AND_parent_ID in AND_parent_list :
            
            # Eventually add the AND_node to the dict
            if not AND_parent_ID in tree_nodes :
                tree_nodes[AND_parent_ID] = get_node(AND_parent_ID)

            # Decrement AND_NODE TODO 
            tree_nodes[AND_parent_ID]['todo'] -= 1
            tree_nodes[AND_parent_ID]['needed'] += tree_nodes[current_node_id]['needed'] + [current_node_id]

            # If all AND_parent children have been traversed
            if tree_nodes[AND_parent_ID]['todo'] == 0 : 
                tree_nodes[AND_parent_ID]['needed'] += [AND_parent_ID]
                tree_nodes[AND_parent_ID]['pred'] = current_node_id
                tree_nodes[AND_parent_ID]['weight'] = get_weight_sum(AND_parent_ID)

                # Case in which the AND_node is the last node before the CVE node
                parent_node = get_parent_node(AND_parent_ID)
                if parent_node and parent_node['type'] == 'CVE' : 
                    path = tree_nodes[AND_parent_ID]['needed'] + [parent_node['nodeID']]
                    fix_temp, removed_edges_temp, new_v = reached_CVE(parent_node['name'], path)
                    if fix_temp : 

                        for fix in fix_temp :    
                            tree_nodes = updateTree(list(fix.keys())[0], path, tree_nodes)
                        
                        list_of_fixes += fix_temp
                        removed_edges_dict.update(removed_edges_temp)
                        
                        if new_v : PQ.append(new_v)
                        continue

                # Retrieve the list of OR parent nodes
                OR_parent_list = get_OR_parents(AND_parent_ID)
                for OR_parent_ID in OR_parent_list :

                    # Eventually add the OR_node to the dict
                    if not OR_parent_ID in tree_nodes :
                        tree_nodes[OR_parent_ID] = get_node(OR_parent_ID)

                    # if the path from the current AND node is more risky than the previous path saved into the OR_parent
                    if tree_nodes[AND_parent_ID]['weight'] > tree_nodes[OR_parent_ID]['weight'] :
                        tree_nodes[OR_parent_ID]['weight'] = tree_nodes[AND_parent_ID]['weight']
                        tree_nodes[OR_parent_ID]['needed'] = tree_nodes[AND_parent_ID]['needed'] + [OR_parent_ID]
                        tree_nodes[OR_parent_ID]['pred'] = AND_parent_ID
                        # If not in the PQ already, append the OR_node id
                        if not OR_parent_ID in PQ : 
                            PQ.append(OR_parent_ID)

    return list_of_fixes, removed_edges_dict