
# Proof of Concept

This file shows the list of commands to use for a proof of concept of this tool.


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

python main.py --add 40c
```

Show Neo4J graph.


## 2 - Add Docker Container

```bash

python main.py --run docker run -it --rm -d nginx

python main.py --run docker run --name test -it --rm -d nginx 

docker ps 
```

Show Neo4J graph.


## 4 - Show Charts

Show updated Neo4J knowledge graph and running containers `docker ps`.

Describe the `vulns.json` and `vulns_query.json` files (i.e. how we represent container vulnerabilities and misconfigurations and how we geenrate the corresponding queries).


## 5 - Analyze Containers

```bash

python main.py --analyze <container_id>

python main.py --remove-all
```

## 6 - Add "Dangerous" Containers

In this example we run the same container image with 3 different configurations. Equivalently, we could stop the running container, and re-execute it with a new (perhaps vulnerable) configuration.

```bash

python main.py --run docker run --name test1 -it --rm -d nginx

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




## Usefull Neo4J Queries

Remove all: `MATCH p = (a)-[r]->(b) RETURN *`.

Return all: `MATCH (n) DETACH DELETE n`.


## Queries example

**Does the container have a specific permission?**

`MATCH (c:Container:Docker {cont_id: '...'})-[:CAN]->(p:Permissions) WHERE 'chmod' IN p.syscalls RETURN COUNT(c) > 0`

Equivalent queries work also with properties that are not of type list (e.g. user).


**Return all relationships of a container**

`MATCH (c:Container:Docker {cont_id: '...'})-[r]->(b) RETURN r, c, b`


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

