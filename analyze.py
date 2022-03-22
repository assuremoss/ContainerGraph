import docker
import warnings
import json
from colorama import Fore, Style
from neo4j import GraphDatabase


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


def connect_to_neo4j(uri, user, password) :
    """
    TODO
    """

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def is_c_running(cont_id) :
    """
    TODO
    """

    client = connect_to_Docker()

    try:
        # retrieve container object
        # if the container is not running anymore --> error
        cont = client.containers.get(cont_id)

        cont_id = cont.short_id

        # check that the container also exists into Neo4J
        # if not cont_already_existing(cont_id) :
        #     print("A container with id " + str(cont_id) + " does not exist! Exiting...")
        #     exit(1)

        return cont_id

    # Raise an exception if the image doesn't exist
    except docker.errors.NotFound as error :
        #
        ### TODO ###
        # remove it from Neo4J
        #
        print(error)
        exit(1)
    except docker.errors.APIError as error :
        print(error)
        exit(1)

    
def query_Neo4j(query, cont_id) :
    """
    TODO
    """

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:
        result = session.read_transaction(query_cont_vuln, query, cont_id)
    driver.close()
    
    return result


def query_cont_vuln(tx, query, cont_id):
    """
    TODO
    """

    result = tx.run(query, cont_id = cont_id)

    # for now, ignore Neo4J warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")

        result = result.single()[0]
        return result


def analyze_cont(cont_id) :
    """
    TODO
    """

    cont_id = is_c_running(cont_id)
    container_attacks, kernel_attacks, engine_attacks = parse_query_file()

    # iterate over the queries
    for vuln in container_attacks :
        result = query_Neo4j(container_attacks[vuln], cont_id)
        if result : print("The container is vulnerable to " + Fore.RED + vuln + Style.RESET_ALL)

    for vuln in kernel_attacks :
        result = query_Neo4j(kernel_attacks[vuln], cont_id)
        if result : print("The container is vulnerable to " + Fore.RED + vuln + Style.RESET_ALL)

    for vuln in engine_attacks :
        result = query_Neo4j(engine_attacks[vuln], cont_id)
        if result : print("The container is vulnerable to " + Fore.RED + vuln + Style.RESET_ALL)


def parse_query_file() :
    """
    TODO
    """

    try :
        with open('./files/vulns_query.json', 'r') as query_file :
            query = json.load(query_file)

            container_attacks = query['container_attacks'][0]
            kernel_attacks = query['kernel_attacks'][0]
            engine_attacks = query['engine_attacks'][0]

            return container_attacks, kernel_attacks, engine_attacks

    except FileNotFoundError as error :
        print(error)
        exit(1)


def remove_container(cont_id) :
    """
    TODO
    """

    # Given a container with is not running anymore (stopped or crashed), remove
    # it from the Neo4J database.

    print("TODO")


def parse_vulns_file() :
    """
    TODO
    """

    # retrieve list of vulnerabilities/misconfigurations
    # container_attacks, kernel_attacks, engine_attacks = parse_vulns_file()
    # retrieve vulnerabilities/misconfigurations Neo4J queries

    # parse the file `vulns.json` and return a list of vulnerabilities/misconfigurations
    # for each vuln type (i.e. container_attacks, kernel_attacks, engine_attacks)

    container_attacks = []
    kernel_attacks = []
    engine_attacks = []

    # TODO

    # we need to decide how to compute the queries from this file
    # how to update vulns, how to update queries, etc.
    
    # manually is also an option: we manually add a vuln to vulns.json 
    # and we define a function to update the queries, for example:
    # python main.py --update-vulns-queries

    return container_attacks, kernel_attacks, engine_attacks

