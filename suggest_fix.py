from neo4j import GraphDatabase
from vuln_tree_taversal import traverse_tree
from colorama import Fore, Style


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))

def query_deployment(NEO4J_ADDRESS) :
    """  brief title.
    
    Arguments:

    Description:
    blablabla
    """

    traverse_tree(NEO4J_ADDRESS)




# def query_deployment(NEO4J_ADDRESS) :
#     """  brief title.
    
#     Arguments:

#     Description:
#     blablabla
#     """

#     try :
#         # Standardize container ID
#         # client = connect_to_Docker()
#         # cont_id = client.containers.get(cont_id).short_id
        
#         # Get the CVE node ID
#         root_id = get_cve_nodes(NEO4J_ADDRESS, cve)

#         # Traverse and evaluate the AND/OR vulnerability tree
#         start = time.time()
#         result = evaluate_tree(NEO4J_ADDRESS, root_id, cont_id)
#         end = time.time()

#         # The container is vulnerable
#         if result : 
#             print("The container is vulnerable to " + Fore.RED + cve + Style.RESET_ALL + "!")
#             result = (root_id, result)
#         else : 
#             print(Fore.GREEN + "The container configuration is safe!" + Style.RESET_ALL)
        


# def print_fix(fix) : 

#     if fix['fix'] == 'version_upgrade' :
#         print(Fore.GREEN + "Upgrade " + Style.RESET_ALL + fix['value'] + " to a newer version.")

#     elif fix['fix'] == 'not_privileged' : 
#         print("Do not run the container with the privileged option: " + Fore.RED + "--privileged" + Style.RESET_ALL)

#     elif fix['fix'] == 'not_root' :
#         print("Run the container with the user option: " + Fore.GREEN + "--user UID:GID" + Style.RESET_ALL)

#     elif fix['fix'] == 'not_capability' :
#         print("Run the container with the option: " + Fore.GREEN + "--cap-drop " + fix['value'] + Style.RESET_ALL)

#     elif fix['fix'] == 'not_syscall' :
#         print("Add the following line to the container AppArmor profile: " + Fore.GREEN + "deny " + fix['value'] + Style.RESET_ALL)

#     elif fix['fix'] == 'read_only_fs' :
#         print("Run the container with the option: " + Fore.GREEN + "--read-only" + Style.RESET_ALL)

#     elif fix['fix'] == 'no_new_priv' :
#         print("Run the container with the option: " + Fore.GREEN + "--security-opt=no-new-privileges:true" + Style.RESET_ALL)


# def suggest_fix(NEO4J_ADDRESS, all_results) : 
#     """  Computes and returns the weight of an AND/OR tree valid path
    
#     Arguments:
#     path - list of node IDs representing a valid path in an AND/OR tree

#     Description:
#     blablabla
#     """

#     # Only one valid path
#     if len(all_results) == 1 : 

#         leaves = all_results[0]['path_0'][-1]

#         # Single leaf
#         if type(leaves) == int : 

#             # Retrieve ``type'' of the leaf
#             leaf_type, leaf_value = get_leaf_type(NEO4J_ADDRESS, leaves)

#             # Based on the type, suggest the only possible fix
#             if leaf_type == 'DockerVersion' or \
#                 leaf_type == 'containerdVersion' or \
#                   leaf_type == 'runcVersion' or \
#                       leaf_type == 'KernelVersion' :

#                         # TODO
#                         # Specify the minimum version to which you should upgrade
#                         value = leaf_type[:-7]
#                         fix = {'fix': 'version_upgrade', 'value': value}
#                         print_fix(fix)

#             elif leaf_value == 'PrivPermissions' :
#                 fix = {'fix': 'not_privileged'}
#                 print_fix(fix)

#             else :
#                 # TODO
#                 print('TODO')

#         # Multiple leaves - AND node
#         elif type(leaves) == list :

#             ahp_weights = parse_ahp_weights()
#             ahp_fixes = []

#             # Remove not relevant fixes
#             for l in leaves : 
#                 leaf_type, leaf_value = get_leaf_type(NEO4J_ADDRESS, l)
#                 aux = {'type': leaf_type, 'value': leaf_value}
                
#                 if leaf_type == 'Privileged' : 
#                     aux['weight'] = ahp_weights['not_privileged']
#                     aux['fix'] = 'not_privileged'
#                 elif leaf_type == 'Capability' : 
#                     aux['weight'] = ahp_weights['not_capability']
#                     aux['fix'] = 'not_capability'
#                 elif leaf_type == 'SystemCall' : 
#                     aux['weight'] = ahp_weights['not_syscall']
#                     aux['fix'] = 'not_syscall'
#                 elif leaf_type == 'NotReadOnly' : 
#                     aux['weight'] = ahp_weights['read_only_fs']
#                     aux['fix'] = 'read_only_fs'
#                 elif leaf_type == 'NoNewPriv' : 
#                     aux['weight'] = ahp_weights['no_new_priv']
#                     aux['fix'] = 'no_new_priv'
#                 elif leaf_type == 'ContainerConfig' : 
#                     # TODO
#                     pass
                    
#                 ahp_fixes.append(aux)

#             # Sort fixes by weights (returns a list)
#             ahp_fixes = sorted(ahp_fixes, key=lambda d: d['weight'], reverse=True) 

#             aws = 'n'
#             # Iterate possible fixes
#             for f in ahp_fixes : 

#                 if f['type'] == 'SystemCall' : 
#                     aws = input("Deny systemcall " + f['value'] + " (y/n) ? ")

#                 elif f['type'] == 'Capability' : 
#                     aws = input("Deny capability " + f['value'] + " (y/n) ? ")
                
#                 else :
#                     aws = input("Accept " + f['fix'] + " (y/n) ? ")
                
#                 if aws == '' or aws == 'y' : 
#                     print_fix(f)
#                     break 

#             if aws == 'n' : 
#                 print(Fore.RED + 'No fix has been choosen! ' + Style.RESET_ALL + 'Exiting...')        

#     # AHP : Multiple valid paths with multiple possible fixes
#     else :
#         fix = apply_ahp(all_results)
#         # print(fix)


# def fix_deployment(NEO4J_ADDRESS, cve) :
#     """  Computes and returns the weight of an AND/OR tree valid path
    
#     Arguments:
#     path - list of node IDs representing a valid path in an AND/OR tree

#     Description:
#     blablabla
#     """

#     result = query_vulnerability(NEO4J_ADDRESS, '', cve)

#     if not result : 
#         return

#     # TODO Fix this function
#     # make it recursive
#     all_path = extract_path(result)

#     all_results = []
#     for i, path in enumerate(all_path) : 
#         w = weight_path(NEO4J_ADDRESS, path)
#         aux = {'cve': cve, 'path_' + str(i): path, 'risk': w}
#         all_results.append(aux)

#     print(all_results)
#     suggest_fix(NEO4J_ADDRESS, all_results)


# ### CUSTOM FUNCTION ###
# # NEO4J_ADDRESS = '192.168.2.5'
# # cve = 'CVE_1'
# # fix_deployment(NEO4J_ADDRESS, cve)
