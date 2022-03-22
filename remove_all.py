from neo4j import GraphDatabase
import os
import docker


def connect_to_Docker() : 
    """ 
    Connects to the Docker daemon running on the current host

    Returns
    -------
    Docker client:
        Returns a client configured from environment variables.
    """

    # Connect to the Docker daemon
    client = docker.from_env()
    return client


def connect_to_neo4j(uri, user, password):
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def neo4j_remove_all(NEO4J_ADDRESS):
    """
    TODO
    """
    
    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
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

    # Clean up XML files
    # XML_remove_all()


def remove_cont_Neo4j(NEO4J_ADDRESS, cont_id) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://" + NEO4J_ADDRESS + ":11005", "neo4j", "password")
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

