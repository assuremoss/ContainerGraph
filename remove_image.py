from neo4j import GraphDatabase
import os


def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def neo4j_remove_container(img_id):

    driver = connect_to_neo4j("bolt://localhost:11005", "neo4j", "password")
    with driver.session() as session:
        session.write_transaction(neo4jremove_container, img_id)
    driver.close()


def neo4jremove_container(tx, img_id) :    
    tx.run("MATCH (c:Container:Docker {img_id: $img_id}) DETACH DELETE c", img_id=img_id)


def XML_remove_container(img_id) :
    
    try :
        os.remove("charts/" + img_id + "_chart.xml" )

    except FileNotFoundError:
        pass


def delete_container(img_id) : 

    # Clean up Neo4J
    neo4j_remove_container(img_id)

    # Clean up XML files
    XML_remove_container(img_id)