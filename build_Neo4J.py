from neo4j import GraphDatabase
import shutil


def connect_to_neo4j(uri, user, password) :
    """
    Add comments
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def generate_Neo4J_chart(img_id) :
    """
    Add comments
    """

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    
    with driver.session() as session:
        session.write_transaction(import_graph, img_id)

    driver.close()


def import_graph(tx, img_id) :
    """
    Add comments
    """

    # Copy the GraphML file into the Neo4J import directory
    # CAREFULL: Neo4J graphml import does not parse the '_' underscore char in file's name!
    src = "./charts/" + img_id + "_chart.graphml"
    dst = "/Users/francescominna/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/dbms-58a0642f-74c7-4d4a-a80b-53e06c50abc4/import/" + img_id + ".graphml"
    shutil.copyfile(src, dst)

    # tx.run("CALL apoc.import.graphml('file://" + img_id + ".graphml', {readLabels: true, storeNodeIds:true});")
    tx.run("CALL apoc.import.graphml('file://" + img_id + ".graphml', {readLabels: true});")

