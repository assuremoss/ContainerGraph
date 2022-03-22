
# Discussion

 - Representing each tool version with 5/10 node (5 versions less and 5 version more) --  we need a reference for this (e.g. people only update systems one or two version ahead at time).

 - How do we represent attacks with CAPEC? Is it the right template? I found several similar references of attacks representation to later generate attack paths.

 - AppArmor/Seccomp: edges are allowed CAPs/syscalls?

 - When to initialize vuln.json in Neo4J? Should we create missing nodes as well and "wait" containers will connect to them?

 - How do we model the interaction with the user? Terminal output?

 - All properties (nodes) in common between containers (root user, capabilities, etc.) are create only once and all containers connect to the same node. This should not be a problem because to update a container (privileges) we first need to stop and restart it (so also a new graph representation will be generated).

 - If we keep this container/attacks representation, I only need the vulns.json file to automatically create nodes in the graphs and automatically generate the query.

 - Analytical hierarchy process: [version_upgrade], [not_privileged], [not_root], [not_capability], [not_syscall], [read_only_fs], [no_new_priv], [official_image]




------------------------------------------------------------------------

# Proof of Concept

This file shows the list of commands to use for a proof of concept of this tool.

For Vagrant Ubuntu VM: `export NEO4J_ADDRESS="192.168.2.5"`.

Cleaning up the environment.

```bash
python main.py --remove-all
```


## 1 - List Docker Images

First, make sure Docker and Neo4J are running. To start Docker, use the following command from a terminal interface `open -a Docker`.

List current available Docker images: `docker images`.


## 2 - Add Docker Images

```bash

python main.py --help

docker images

python main.py --add <image_id>
```

Show Neo4J graph.


## 2 - Add Docker Container

```bash

python main.py --run docker run --name test -it --rm -d nginx 

docker ps 
```

Show Neo4J graph.


## 4 - Show Charts

Show updated Neo4J knowledge graph and running containers `docker ps`.

Describe the `vulns.json` file (i.e. how we represent container vulnerabilities and misconfigurations and how we geenrate the corresponding queries).


## 5 - Analyze Containers

```bash

python main.py --analyze <container_id>

python main.py --remove-all
```

## 6 - Add "Dangerous" Containers

In this example we run the same container image with 3 different configurations. Equivalently, we could stop the running container, and re-execute it with a new (perhaps vulnerable) configuration.

```bash

python main.py --run docker run --name vuln1 --cap-add sys_admin --security-opt apparmor=unconfined -it --rm -d nginx 

python main.py --run docker run --name vuln2 -it --rm --privileged -d nginx 

docker ps 
```

## 7 - Re-Analyze Containers

```bash

python main.py --analyze <container_id>
python main.py --analyze <container_id>
python main.py --analyze <container_id>

python main.py --remove-all
```


## 8 - CVE Queries


```bash
python main.py --run docker run --name vuln1 -it --rm -d --privileged nginx
python main.py --run docker run --name vuln2 -it --rm -d --privileged ubuntu
```

"
MERGE (cve:Escape1 {name: 'Escape_1'})
MERGE (mtac:Mitre:Tactic {name: 'Privilege Escalation'})
MERGE (mtec:Mitre:Technique {name: 'Escape to Host'})

MATCH (cve:Escape1 {name: 'Escape_1'})
MATCH (mtec:Mitre:Technique {name: 'Escape to Host'})
MERGE (cve)-[:LEADS_TO]->(mtec)

MATCH (mtac:Mitre:Tactic {name: 'Privilege Escalation'})
MATCH (mtec:Mitre:Technique {name: 'Escape to Host'})
MERGE (mtec)-[:PARTS_OF]->(mtac)

MATCH (cve:Escape1 {name: 'Escape_1'})
MATCH (cc:ContainerConfig {name: 'root'})
MERGE (cc)-[:ASSUMPTION_OF]->(cve)

MATCH (cve:Escape1 {name: 'Escape_1'})
MATCH (cap:Capability {name: 'CAP_SYS_ADMIN'})
MERGE (cap)-[:ASSUMPTION_OF]->(cve)

MATCH (cve:Escape1 {name: 'Escape_1'})
MATCH (sysc:SystemCall {name: 'mount'})
MERGE (sysc)-[:ASSUMPTION_OF]->(cve)
"


Examples of Neo4J queries to check whether a container is vulnerable to a specific vulnerability:

`MATCH p = (c:Container)-[*]-(cve:Escape1) RETURN COUNT(p) > 0`

This kind of query can actually be automatically generated :)


Query to return the **Spanning Tree** of a vulnerability:

`MATCH p = (a)-[:ASSUMPTION_OF]->(b)-[*]->(c) RETURN *`


Query to return the list of Assumptions for an attack:

`MATCH (a)-[:ASSUMPTION_OF]->(b) RETURN a.name`


## Pattern negation to multiple nodes

Correct approach: collect nodes to exclude, and use WHERE NONE() on the collection to drive exclusion.
Reference: https://neo4j.com/developer/kb/performing-pattern-negation/

Example: 
`MATCH path = ()-[*]->() WHERE NONE(n IN nodes(path) WHERE n.name == 'root') RETURN path`



## Usefull Neo4J Queries

Return every node and relationship: `MATCH p=(a) RETURN p`

Return all nodes with relationships: `MATCH p = (a)-[r]->(b) RETURN *`.

Remove all: `MATCH (n) DETACH DELETE n`.


## Queries example

**Does the container have a specific permission?**

`MATCH (c:Container:Docker {cont_id: 'fe9000b378'})-[*]->(sysc:SystemCall {name: 'mount'}) RETURN COUNT(c) > 0`

Equivalent queries work also with properties that are not of type list (e.g. user).


## Testing Container Permission Parser

```bash

python main.py --run docker run --name test0 -it --rm -d nginx

python main.py --run docker run --name test1 -it --rm --cap-drop all --cap-add sys_module -d nginx

python main.py --run docker run --name test2 -it --rm --cap-add sys_admin -d nginx

python main.py --run docker run --name test3 -it --rm --cap-drop chown -d nginx

python main.py --run docker run --name test4 -it --rm --privileged -d nginx

python main.py --run docker run --name test5 -it --rm --cap-add sys_admin --security-opt apparmor=unconfined -d nginx

python main.py --run docker run --name test6 -it --rm --cap-add sys_admin --security-opt seccomp=unconfined -d nginx

```

