
# ContainerGraph

A tool to generate a Knowledge Graph of Docker containers. 


## How to run the tool

Blablabla




## Useful Tools

https://github.com/containers


## Neo4J Database Connection

To run the tool within a `Vagrant` virtual machine you have to allow remote connections to the Neo4J database. To do so, change the following Database settings:

`dbms.connector.bolt.listen_address=0.0.0.0:11005`

The ContainerGraph tool will read the Neo4J database address to use from the local environmental variable `NEO4J_ADDRESS`.

You can specify your own address using the following commands: `export NEO4J_ADDRESS="neo4j_server_ip"`. By default, `localhost` will be used. 

