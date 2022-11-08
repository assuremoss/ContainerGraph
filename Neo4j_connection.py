from neo4j import GraphDatabase
import os

### Read Neo4J Environmental variables ###
try:
    NEO4J_ADDRESS = os.environ.get('NEO4J_ADDRESS')
    NEO4J_PORT = os.environ.get('NEO4J_PORT')
    NEO4J_USER = os.environ.get('NEO4J_USER')
    NEO4J_PWS = os.environ.get('NEO4J_PWS')

except KeyError :
    print("Environment variable does not exist! You need to define NEO4J_ADDRESS, NEO4J_PORT, NEO4J_USER, and NEO4J_PWS")
    exit(1)

uri = "bolt://" + NEO4J_ADDRESS + ":" + NEO4J_PORT

def connect_to_neo4j() :
    return GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PWS))