from neo4j import GraphDatabase
import docker
from vuln_tree_taversal import traverse_tree
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
        return tx.run("MATCH (n:Deployment) RETURN {node_id: ID(n), cont_id: n.cont_id}").value()

    else : 
        return tx.run("""
        MATCH (n:Deployment {name: 'Deployment', cont_id: $cont_id})
        RETURN {node_id: ID(n), cont_id: n.cont_id}
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
            CVEs = traverse_tree(NEO4J_ADDRESS, d['cont_id'])

            # If the container is vulnerable to any CVE in the dataset
            if CVEs :

                # Concatenate the CVEs as strings
                CVEs_string = ", ".join( map(str, CVEs.keys()) )
                print("The container with ID " + d['cont_id'] + " is vulnerable to " + Fore.RED + CVEs_string + Style.RESET_ALL)

                # List of ignored CVEs for the current container
                cve_ignored = []
                # List of selected fixes
                fixes = []

                # Iterate all exploitable vulnerabilities
                for key, value in CVEs.items() : 

                    # Check if this CVE is being ignored for this container
                    if value['ignored'] :
                        cve_ignored += [key]

                    # Check if any selected fix (node_id) is in the path of the current CVE
                    # In such a case, ignore the CVE because it is already fixed by a previous mitigation
                    elif not any(item in fixes for item in value['path']) :

                        # Ask the user whether she/he wants to fix the CVE
                        aws = input("Do you want to fix " + Fore.RED + key + Style.RESET_ALL + "? (y/n) ")

                        if aws == 'y' : 
                            # If yes, suggest possible fixes and return the list of selected mitigations
                            rsp = suggest_fix(NEO4J_ADDRESS, value)
                            fixes += rsp

                            # Check if the selected fixes mitigate other CVEs
                            if rsp :
                                cve_mitigated = []
                                for k, v in CVEs.items() :
                                    if k!= key and any(item in rsp for item in v['path']) :
                                        cve_mitigated += [k]
                                
                                if cve_mitigated :
                                    cve_mitigated = ", ".join( map(str, cve_mitigated) )
                                    print('This fix or fixes would also mitigate ' + cve_mitigated)

                            # Otherwise, no fix was selected
                            else : cve_ignored += [key]

                        # Otherwise, ignore this CVE 
                        else : cve_ignored += [key]
                    
                    # Otherwise skip CVE because it's already mitigated by a previous fix
                    else : continue

                # If any CVE is currently ignored
                if cve_ignored :

                    # Build the (ignored) node
                    build_ignore(NEO4J_ADDRESS, d['cont_id'], cve_ignored)

                    cve_ignored = ", ".join( map(str, cve_ignored) )
                    print("The following CVEs are being ignored " + Fore.RED + cve_ignored + Style.RESET_ALL)

            # Otherwise, the configuration is safe, to the best of our knowledge
            else : 
                print(Fore.GREEN + "The container with ID " + d['cont_id'] + " is safe!" + Style.RESET_ALL)

    # Raise an exception if the container doesn't exist/is not running
    except docker.errors.NotFound as error :
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)


def build_ignore(NEO4J_ADDRESS, cont_id, CVEs) :
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(ignore_node, cont_id, CVEs)
    driver.close()

def ignore_node(tx, cont_id, CVEs) :

    for cve in CVEs : 

        query = """
        MERGE (ign:IsIgnored {name: 'IsIgnored', cve:$cve, cont_id:$cont_id})
        UNION
        MATCH (ign:IsIgnored {name: 'IsIgnored', cve:$cve, cont_id:$cont_id})
        MATCH (AS:AttackSurface {name: 'AttackSurface'})
        MERGE (ign)-[:BELONGS_TO]->(AS)
        UNION
        MATCH (ign:IsIgnored {name: 'IsIgnored', cve:$cve, cont_id:$cont_id})
        MATCH (cve:CVE {name:$cve})
        MERGE (cve)-[:IGNORE]->(ign)
        UNION
        MATCH (ign:IsIgnored {name: 'IsIgnored', cve:$cve, cont_id:$cont_id})
        MATCH (d:Deployment {cont_id:$cont_id})
        MERGE (d)-[:IGNORE]->(ign) 
        """

        tx.run(query, cont_id=cont_id, cve=cve)


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
    # Keep track of which fix (node_id in the path) were selected
    choosen = []

    # Retrieve the leaves part of the valid path in the AND/OR tree
    for node_id in cve['path'] : 

        # Retrieve the leaf Neo4J node
        # If the current node is not a leaf, just ignore    
        leaf = get_node(NEO4J_ADDRESS, node_id)

        if leaf['type'] == 'DockerVersion' or \
            leaf['type'] == 'containerdVersion' or \
            leaf['type'] == 'runcVersion' or \
                leaf['type'] == 'KernelVersion' :
                    aws = input('Do you want to upgrade ' + leaf['type'].strip('Version') + ' version? (y/n) ')
                    if aws == 'y' : 
                        choosen += [node_id]
                        print_fix({'fix': 'version_upgrade', 'value': leaf['type'].strip('Version'), 'version': leaf['name']})

        elif leaf['type'] == 'Permissions' and leaf['name'] == 'Privileged' :
            aws = input('Do you want to run the container as privileged? (y/n) ')
            if aws == 'n' : 
                choosen += [node_id]
                print_fix({'fix': 'not_privileged'})
        
        elif leaf['type'] == 'SystemCall' : 
            aws = input('Do you need the ' + leaf['name'] + ' system call? (y/n) ')
            if aws == 'n' : 
                choosen += [node_id]
                print_fix({'fix' : 'not_syscall', 'value': leaf['name']})

        elif leaf['type'] == 'Capability' : 
            aws = input('Do you need the ' + leaf['name'] + ' capability? (y/n) ')
            if aws == 'n' : 
                choosen += [node_id]
                print_fix({'fix' : 'not_capability', 'value': leaf['name']})

        elif leaf['type'] == 'ContainerConfig' : 
            if leaf['name'] == 'root' :
                aws = input('Do you want to run the container as root? (y/n) ')
                if aws == 'n' : 
                    choosen += [node_id]
                    print_fix({'fix' : 'not_root'})
                # elif
                # TODO
                # volumes, env, etc.

        elif leaf['type'] == 'NewPriv' : 
            aws = input('Do you want the container to gain additional privileges? (y/n) ')
            if aws == 'n' : 
                choosen += [node_id]
                print_fix({'fix' : 'no_new_priv'})

        elif leaf['type'] == 'NotReadOnly' : 
            aws = input('Do you need write access to the filesystem? (y/n) ')
            if aws == 'n' : 
                choosen += [node_id]
                print_fix({'fix' : 'read_only_fs'})

    # Return the list of choosen fixes or an empty list
    # print(Fore.RED + 'No fix has been choosen! ' + Style.RESET_ALL + 'Exiting...') 
    return choosen


def print_fix(fix) : 

    if fix['fix'] == 'version_upgrade' :
        print(Fore.GREEN + "Upgrade " + Style.RESET_ALL + fix['value'] + " to a version > " + fix['version'])

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

