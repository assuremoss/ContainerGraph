
# ContainerGraph

A tool to generate a Knowledge Graph of Docker containers. 


## How to run the tool

Blablabla






## Comparison Tool

**Microsoft Defender for Containers** 
 - https://techcommunity.microsoft.com/t5/microsoft-defender-for-cloud/introducing-microsoft-defender-for-containers/ba-p/2952317
 - https://docs.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction
 - https://docs.microsoft.com/en-us/azure/defender-for-cloud/alerts-reference#alerts-k8scluster
 - https://guillaumeben.xyz/defender-containers.html


## Useful Tools

https://github.com/containers


## Neo4J Database Connection

To run the tool within a `Vagrant` virtual machine you have to allow remote connections to the Neo4J database. To do so, change the following Database settings:

`dbms.connector.bolt.listen_address=0.0.0.0:11005`

The ContainerGraph tool will read the Neo4J database address to use from the local environmental variable `NEO4J_ADDRESS`.

You can specify your own address using the following commands: `export NEO4J_ADDRESS="neo4j_server_ip"`. By default, `localhost` will be used. 

