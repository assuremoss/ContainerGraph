from neo4j import GraphDatabase
import docker
from vuln_tree_taversal import traverse_tree, append_node_property
from colorama import Fore, Style
from vuln_tree_taversal import get_node


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))

def connect_to_Docker() : 
    return docker.from_env()


def get_deployments(NEO4J_ADDRESS, cont_id=0) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        temp = session.read_transaction(query_deployments, cont_id)
    driver.close()
    return temp

def query_deployments(tx, cont_id) :
    
    # Return all Deployment nodes
    if cont_id == 0 :
        return tx.run("MATCH (n:Deployment) RETURN {node_id: ID(n), cont_id: n.cont_id, ignore: n.ignore}").value()

    else : 
        return tx.run("""
        MATCH (n:Deployment {name: 'Deployment', cont_id: $cont_id})
        RETURN {node_id: ID(n), cont_id: n.cont_id, ignore: n.ignore}
        """, cont_id=cont_id).value()


def analyze_deployment(NEO4J_ADDRESS, d) : 
    # To check the container is running
    client = connect_to_Docker()

    try:
        # Retrieve container object
        cont = client.containers.get(d['cont_id'])

        # Check the container is running
        if cont.status == 'running' : 

            # Traverse the AND/OR tree to check for possible vulnerabilities
            CVEs = traverse_tree(NEO4J_ADDRESS, d['node_id'])
            
            # Iterate all exploitable vulnerabilities
            for cve in CVEs : 
                print("The container with ID " + d['cont_id'] + " is vulnerable to " + Fore.RED + cve['CVE'] + Style.RESET_ALL + "!")

                # Ask the user whether she/he wants to fix the CVE
                aws = input("Do you want to fix it? (y/n) ")

                if aws == 'y' : 
                    # If yes, suggest possible fixes
                    suggest_fix(NEO4J_ADDRESS, cve)
                else : 
                    # Otherwise, ignore this CVE 
                    append_node_property(NEO4J_ADDRESS, d['node_id'], 'ignore_CVEs', cve['CVE'])
                    print(Fore.RED + cve['CVE'] + " affecting " + d['cont_id'] + " will be ignored!" + Style.RESET_ALL) 

            if not CVEs : 
                print(Fore.GREEN + "The container with ID " + d['cont_id'] + " is safe!" + Style.RESET_ALL)

    # Raise an exception if the container doesn't exist/is not running
    except docker.errors.NotFound as error :
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)


def analyze_single_deployment(NEO4J_ADDRESS, cont_id) :
    
    # Retrieve container ID
    client = connect_to_Docker()

    try:
        # Retrieve container object
        cont = client.containers.get(cont_id)

        # Get the deployment Neo4J node
        deployment = get_deployments(NEO4J_ADDRESS, cont.short_id)[0]

        # Analyze the container deployment
        analyze_deployment(NEO4J_ADDRESS, deployment)
    
    # Raise an exception if the container doesn't exist/is not running
    except docker.errors.NotFound as error :
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)


def analyze_all_deployment(NEO4J_ADDRESS) :

    # Get a list of Deployment node IDs
    deployments = get_deployments(NEO4J_ADDRESS)

    # Iterate over each container
    for d in deployments : 

        # Analyze the container deployment
        analyze_deployment(NEO4J_ADDRESS, d)
 
    # If no containers are running, print safe deployment
    if not deployments :
        print(Fore.GREEN + "There are no running containers to analyze! Exiting..." + Style.RESET_ALL)


def suggest_fix(NEO4J_ADDRESS, cve) : 
    # Keep track if a fix was choosen
    choosen = False

    # Retrieve the leaves part of the valid path in the AND/OR tree
    for node_id in cve['path'] : 

        # Retrieve the leaf Neo4J node
        # If the current node is not a leaf, just ignore    
        leaf = get_node(NEO4J_ADDRESS, node_id)

        if leaf['type'] == 'DockerVersion' or \
            leaf['type'] == 'containerdVersion' or \
            leaf['type'] == 'runcVersion' or \
                leaf['type'] == 'KernelVersion' :
                    aws = input('Do you want to update ' + leaf['type'] + '? (y/n) ')
                    if aws == 'y' : 
                        choosen = True
                        # TODO
                        # Specify the minimum version to which you should upgrade
                        print_fix({'fix': 'version_upgrade', 'value': leaf['type']})

        elif leaf['type'] == 'Permissions' and leaf['name'] == 'Privileged' :
            aws = input('Do you want to run the container as privileged? (y/n) ')
            if aws == 'n' : 
                choosen = True
                print_fix({'fix': 'not_privileged'})
        
        elif leaf['type'] == 'SystemCall' : 
            aws = input('Do you need the ' + leaf['name'] + ' system call? (y/n) ')
            if aws == 'n' : 
                choosen = True
                print_fix({'fix' : 'not_syscall', 'value': leaf['name']})

        elif leaf['type'] == 'Capability' : 
            aws = input('Do you need the ' + leaf['name'] + ' capability? (y/n) ')
            if aws == 'n' : 
                choosen = True
                print_fix({'fix' : 'not_capability', 'value': leaf['name']})

        elif leaf['type'] == 'ContainerConfig' : 
            if leaf['name'] == 'root' :
                aws = input('Do you want to run the container as root? (y/n) ')
                if aws == 'n' : 
                    choosen = True
                    print_fix({'fix' : 'not_root'})
                # elif
                # TODO
                # volumes, env, etc.

        elif leaf['type'] == 'NewPriv' : 
            aws = input('Do you want the container to gain additional privileges? (y/n) ')
            if aws == 'n' : 
                choosen = True
                print_fix({'fix' : 'no_new_priv'})

        elif leaf['type'] == 'NotReadOnly' : 
            aws = input('Do you need write access to the filesystem? (y/n) ')
            if aws == 'n' : 
                choosen = True
                print_fix({'fix' : 'read_only_fs'})

    # If no fix has been choosen..
    if not choosen :
        print(Fore.RED + 'No fix has been choosen! ' + Style.RESET_ALL + 'Exiting...')   


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

