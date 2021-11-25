from neo4j import GraphDatabase
import os


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def neo4j_remove_all():

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(neo4jremove_data)
    driver.close()


def neo4jremove_data(tx) :
    tx.run("MATCH (n) DETACH DELETE n")


def XML_remove_all() :
    dir = os.listdir("charts")
    
    try :
        for d in dir :
            if d != "template_chart.xml" : 
                os.remove("charts/" + d )

    except FileNotFoundError:
        pass


def data_remove_all() : 

    # Clean up Neo4J
    neo4j_remove_all()

    # Clean up XML files
    XML_remove_all()