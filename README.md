
# ContainerGraph Tool

A Python-based tool for automatic detection and mitigation of vulnerabilities and misconfigurations for Docker containers. 


## Requirement - Docker

ContainerGraph uses the Neo4J graph database as a back-end storage. You can run both the ContainerGraph tool and Neo4J database as Docker containers.

This tool has been tested on MacOS and Ubuntu laptops.


## How-to Run





## Usage Examples

To display all options, you can use: `... --help`

1. Execute a new privileged container: `... --run docker run --name nginxpriv -it --rm -d --privileged nginx`

2. Analyze the container for misconfigurations and vulnerabilities: `... --analyze`


## Interaction with the Neo4J Database

You can access the Neo4J browser interface to interact with the data stored in the database at the following address:

<http://localhost:7474/browser/>

The credentials to login in are the ones used to start the Neo4J container, by default user: `neo4j`, and password: `password`.

 - To query the database, check some [query examples](https://neo4j.com/developer/cypher/querying/).

 - To change the number of nodes displayed in the browser, check the [Neo4j documentation](https://neo4j.com/docs/browser-manual/current/operations/browser-settings/#adjust-in-browser).


## Issues and Bugs

For any issue and bug you encounter while using the tool, please open an issue on this repository.

