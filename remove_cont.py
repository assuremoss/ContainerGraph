from neo4j import GraphDatabase
import os
import docker
import json


def connect_to_Docker() : 
    return docker.from_env()


def connect_to_neo4j(uri, user, password) :
    return GraphDatabase.driver(uri, auth=(user, password))


def reset_ahp() : 
    """  brief title.
    
    Arguments:
    arg1 - desc
    arg2 - desc

    Description:
    blablabla
    """

    try :
        with open('./files/ahp_weights.json', 'r+') as f :
            ahp_weights = json.load(f)

            ahp_weights['version_upgrade'] = 0
            ahp_weights['not_privileged'] = 0
            ahp_weights['not_root'] = 0
            ahp_weights['not_capability'] = 0
            ahp_weights['not_syscall'] = 0
            ahp_weights['read-only_fs'] = 0
            ahp_weights['no_new_priv'] = 0

            f.seek(0)
            json.dump(ahp_weights, f, indent=4)
            f.truncate()

    except FileNotFoundError as error :
        print(error)
        exit(1)


def neo4j_remove_all(NEO4J_ADDRESS):
    """
    TODO
    """
    
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(neo4jremove_data)
    driver.close()


def neo4jremove_data(tx) :
    """
    TODO
    """
    
    tx.run("MATCH (n) DETACH DELETE n")


def XML_remove_all() :
    """
    TODO
    """
    
    dir = os.listdir("charts")
    
    try :
        for d in dir :
            if d != "template_chart.xml" : 
                os.remove("charts/" + d )

    except FileNotFoundError:
        pass


def cont_remove_all() :
    """
    TODO
    """
    
    try:
        # remove all running containers
        # docker stop $(docker container ls -q)
        cmd1 = 'docker stop $(docker container ls -q)'
        cmd2 = 'docker container prune -f'

        os.system(cmd1)
        os.system(cmd2)

    # Raise an exception if docker fails
    except FileNotFoundError:
        pass


def data_remove_all(NEO4J_ADDRESS) : 
    """
    TODO
    """
    
    # Clean up containers
    cont_remove_all()

    # Clean up Neo4J
    neo4j_remove_all(NEO4J_ADDRESS)

    # Reset AHP weights
    reset_ahp()

    print("Everything was cleaned up!")


def remove_cont_Neo4j(NEO4J_ADDRESS, cont_id) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":7687", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(neo4jremove_cont, cont_id)
    driver.close()


def neo4jremove_cont(tx, cont_id) :
    """
    TODO
    """
    
    ### SHOULD WE ALSO REMOVE ALL THE ASSOCIATED NODES (e.g. user, volumes, net, etc.)

    tx.run("MATCH (c:Container)-[r]-() "
           "WHERE c.cont_id = $cont_id "
           "DELETE r, c; ",
           cont_id = cont_id
    )
    
    # Alternative:
    # tx.run("MATCH (c:Container:Docker {cont_id: }) DETACH DELETE c", )


def remove_container(NEO4J_ADDRESS, cont_id) :
    """
    TODO
    """

    client = connect_to_Docker()

    try:
        # retrieve container object
        cont = client.containers.get(cont_id)
        cont_id = cont.short_id

        # kill the container
        cmd1 = 'docker stop ' + cont_id
        cmd2 = 'docker container prune -f'

        os.system(cmd1)
        os.system(cmd2)

        # remove the container from Neo4J
        remove_cont_Neo4j(NEO4J_ADDRESS, cont_id)

        print("Successfully removed the container with ID " + cont_id)

    # Raise an exception if docker fails
    except docker.errors.NotFound as error :
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)
    except FileNotFoundError as error:
        print(error)
        exit(1)

