from Neo4j_connection import connect_to_neo4j
import os
import docker


def connect_to_Docker() : 
    return docker.from_env()


def neo4j_remove_all():
    """
    This code connects to a Neo4j database using the connect_to_neo4j() function. It then creates a session with the driver and uses the write_transaction() method to execute the neo4jremove_data() function. Finally, it closes the driver connection.
    """

    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(neo4jremove_data)
    driver.close()

def neo4jremove_data(tx) :
    # tx.run("MATCH (n) DETACH DELETE n")
    print("THIS WILL DELETE EVERYTHING!")
    
    tx.run("MATCH (c:Container:Docker) DETACH DELETE c")


def neo4j_remove_cont():
    """
    This code connects to a Neo4j database using the connect_to_neo4j() function. It then creates a session with the driver and uses the write_transaction() method to execute the neo4jremove_data() function. Finally, it closes the driver connection.
    """

    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(neo4jremove_cont)
    driver.close()

def neo4jremove_cont(tx) :
    tx.run("MATCH (c:Container:Docker) DETACH DELETE c")


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


def data_remove_all() : 
    """
    TODO
    """

    # Clean up Neo4J
    neo4j_remove_all()
    
    # Clean up containers
    cont_remove_all()

    print("Everything was cleaned up!")


def data_remove_cont() : 
    """
    TODO
    """

    # Clean up Neo4J
    neo4j_remove_cont()
    
    # Clean up containers
    cont_remove_all()

    print("All containers were cleaned up!")



def remove_cont_Neo4j(cont_id) :
    driver = connect_to_neo4j()
    with driver.session() as session:
        session.write_transaction(neo4jremove_cont, cont_id)
    driver.close()

def neo4jremove_cont(tx, cont_id) :
    tx.run("MATCH (c:Container:Docker {cont_id: $cont_id}) DETACH DELETE c ", cont_id=cont_id)

def remove_container(cont_id) :
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
        remove_cont_Neo4j(cont_id)

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

