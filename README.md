
# ContainerGraph

A tool to generate a Knowledge Graph of Docker containers, unveil the presence of vulnerabilities, and suggest security policies. 

## Requirements

 - python

 - docker

 - Neo4J

## Run the tool as a Docker container

**TODO**

## How to run the tool

To run the tool, follow these steps:

1. `git clone https://github.com/fminna/ContainerGraph.git`

2. `cd ContainerGraph`

3.  `sudo addgroup --system docker`
    `sudo adduser $USER docker`
    `newgrp docker`

4. `sudo nano /etc/environment` and append the following line: `NEO4J_ADDRESS="neo4j_server_ip"`

5. Log out and log in again (to make the env variable persistent).

6. `pipenv install`

7. `pipenv shell`

8. `python main.py --help`


### Neo4J Database Connection

To run the tool within a `Vagrant` virtual machine you have to allow remote connections to the Neo4J database. To do so, change the following Database settings:

`dbms.connector.bolt.listen_address=0.0.0.0:7687`

The ContainerGraph tool will read the Neo4J database address to use from the local environmental variable `NEO4J_ADDRESS`.

You can specify your own address using the following commands: `export NEO4J_ADDRESS="neo4j_server_ip"`. By default, `localhost` will be used. 

