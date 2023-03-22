from neo4j_connection import connect_to_neo4j
import docker
from vuln_tree_taversal import traverse_tree
from colorama import Fore, Style
from remove_cont import remove_container
from parse_perm_file import get_all_CAPs, get_all_syscalls
from build_cont_neo4j import create_cont_exploit_rel


def connect_to_Docker() : 
    return docker.from_env()

def restore_graph_edges(removed_edges_dict) : 
    driver = connect_to_neo4j()
    with driver.session() as session:
        cont_IDs = session.write_transaction(restore_edges, removed_edges_dict)
    driver.close()

    if cont_IDs :
        with driver.session() as session:
            for cont_id in cont_IDs :
                session.write_transaction(create_cont_exploit_rel, cont_id)
        driver.close()
        

def restore_edges(tx, removed_edges_dict) : 
    cont_IDs = []

    for key, value in removed_edges_dict.items() :

        if value['type'] == 'engine' :                
            # Delete new version edge
            tx.run("""
                MATCH (eng)-[r]->(v) WHERE ID(eng)=$eng_id AND ID(v)=$new_v
                DELETE r
            """, eng_id=value['engine_id'], new_v=value['new_v_id'])

            # Restore new version edge
            tx.run("""
                MATCH (eng) WHERE ID(eng)=$eng_id
                MATCH (v) WHERE ID(v)=$old_v
                MERGE (eng)-[:HAS_PROPERTY]->(v)
                UNION
                MATCH (eng) WHERE ID(eng)=$eng_id
                MATCH (v) WHERE ID(v)=$old_v
                MERGE (eng)-[:EXPLOITS]->(v)
            """, eng_id=value['engine_id'], old_v=value['old_v_id'])

        elif value['type'] == 'privileged' :
            tx.run("""
                MATCH (p:Permissions {name: 'Permissions', container: $cont_id}) 
                SET p.profile = 'docker-privileged'
                UNION
                MATCH (p:Permissions {name: 'Permissions', container: $cont_id})
                MATCH (aa:AppArmor {name: 'AppArmor', container: $cont_id, object: 'Container'})
                DETACH DELETE (aa)
                UNION
                MATCH (p:Permissions {name: 'Permissions', container: $cont_id})
                MATCH (sc:SecComp {name: 'SecComp', container: $cont_id})
                DETACH DELETE (sc)
            """, cont_id=value['cont_id'])

            all_sysc = get_all_syscalls()
            all_caps = get_all_CAPs()

            for sysc in all_sysc :
                tx.run("""
                MATCH (perm:Permissions {name: 'Permissions', container: $cont_id})
                MATCH (s:SystemCall {name: $name})
                MERGE (perm)-[:HAS_PROPERTY]->(s)
                """, cont_id=value['cont_id'], name=sysc)

            for cap in all_caps :
                tx.run("""
                MATCH (perm:Permissions {name: 'Permissions', container: $cont_id})
                MATCH (c:Capability {name: $name})
                MERGE (perm)-[:HAS_PROPERTY]->(c)
                """, cont_id=value['cont_id'], name=cap)

            tx.run("""
            MATCH (perm:Permissions {name: 'Permissions', container: $cont_id})
            MATCH (priv:Permissions:Privileged {name: 'Privileged'})
            MERGE (perm)-[:HAS_PROPERTY]->(priv)
            """, cont_id=value['cont_id'])

            cont_IDs.append(value['cont_id'])

        elif value['type'] == 'container' :
            for perm_id in value['perm'] :
                tx.run("""
                MATCH (perm:Permissions {name: 'Permissions', container: $cont_id})
                MATCH (p) WHERE ID(p)=$perm_id
                MERGE (perm)-[:HAS_PROPERTY]->(p)
                """, cont_id=value['cont_id'], perm_id=perm_id)

            for cap_id in value['caps'] :
                tx.run("""
                MATCH (aa:AppArmor {name: 'AppArmor', container: $cont_id, object: 'Container'})
                MATCH (c:Capability) WHERE ID(c)=$cap_id
                MERGE (aa)-[:HAS_PROPERTY]->(c)
                """, cont_id=value['cont_id'], cap_id=cap_id)

            for sysc_id in value['syscalls'] :
                tx.run("""
                MATCH (sc:SecComp {name: 'SecComp', container: $cont_id}) 
                MATCH (s:SystemCall) WHERE ID(s)=$sysc_id
                MERGE (sc)-[:HAS_PROPERTY]->(s)
                """, cont_id=value['cont_id'], sysc_id=sysc_id)

            cont_IDs.append(value['cont_id'])

    return cont_IDs


def analyze_all_deployment() :
    """Description ...
    
    Parameters
    ----------
    param1 : desc ...

    Return
    ----------
    object
    """

    # Initialize Priority Queue (ordered by weights -- highest to lowest)
    PQ = initialize_pq()

    if not bool(PQ) :
        print(Fore.GREEN + "The current configuration is safe! Exiting..." + Style.RESET_ALL)
        return

    # List of all fixes
    # graph = AOTrees()
    list_of_fixes, removed_edges_dict = traverse_tree(PQ)   

    # Print list of all fixes to eventually implement
    if list_of_fixes : 
        # Restore the delete edges
        restore_graph_edges(removed_edges_dict)

        print("---------")
        print('')
        print("The following is the list of all fixes choosen to be implemented.")
        print("All containers must be stopped and started again with the new configuration.\n")

        for fix in list_of_fixes :

            n = list(fix.keys())[0]
            print(' •', fix[n]['output'])

        print() # add a new empty line to the output


def initialize_pq() : 
    """Description ...
    """
   
    # Get all container IDs children of DockerDeployment
    cont_IDs = get_cont_IDs()

    # # Check that each container is running otherwise, remove container
    # for cont_id in cont_IDs : 
    #     check_container(cont_id)

    return get_leaves()


def get_cont_IDs() :
    """Returns the list of container IDs connected to the Deployment node. 
    If no containers are running, it returns an empty list.
    
    Return
    ----------
    List of container IDs.
    """
   
    driver = connect_to_neo4j()
    with driver.session() as session:
        temp = session.read_transaction(query_deployment)
    driver.close()
    return temp


def query_deployment(tx) :
    return tx.run("""
    MATCH (dd:DockerDeployment {name: 'DockerDeployment'})-[:HAS]->(c:Container:Docker)
    WITH COLLECT(c.cont_id) as cont_IDs
    RETURN cont_IDs
    """).value()[0]


def get_leaves() :
    """Returns all leaves (CVE assumptions) connected to at least one container, 
    ordered by weights, from highest to lowest, that are part of at least
    one CVE tree (i.e., that have at least an AND or OR edge).
    
    Return
    ----------
    List of leaf IDs.
    """
    driver = connect_to_neo4j()
    with driver.session() as session:
        leaves = session.read_transaction(query_leaves)
    driver.close()
    return leaves

    
def query_leaves(tx):
    return tx.run("""
        MATCH ()-[:EXPLOITS]->(l)
        WHERE EXISTS( (l)-[:AND]->(:AND_NODE) ) OR EXISTS( (l)-[:OR]->(:OR_NODE) )
        WITH DISTINCT l ORDER BY l.weight DESC 
        WITH COLLECT(ID(l)) AS leaves_IDs RETURN leaves_IDs
    """).value()[0]


def check_container(cont_id) :
    
    # Retrieve container ID
    client = connect_to_Docker()

    try:
        # Retrieve container object
        client.containers.get(cont_id)
    
    # Raise an exception if the container doesn't exist/is not running
    except docker.errors.NotFound as error :
        remove_container(cont_id)

    except docker.errors.APIError as error :
        remove_container(cont_id)

