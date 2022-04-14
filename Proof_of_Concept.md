
## Seccomp - Secure Compute Mode

Seccomp is a Linux techonology to limit the set of system calls a process (container) can use.





## AND/OR trees - Neo4J

Reference: 

[1] https://neo4j.com/labs/apoc/4.1/overview/apoc.path/apoc.path.subgraphNodes/

[2] https://stackoverflow.com/questions/71815007/given-a-neo4j-tree-with-a-weight-on-its-leaves-how-do-i-return-for-each-node-th/71820674#71820674



Return all AND/OR nodes of a CVE node (no leaves):

"
MATCH (r:ROOT_NODE)
CALL apoc.path.subgraphAll(r, {
	relationshipFilter: "<",
	labelFilter: "+AND_NODE|+OR_NODE"
})
YIELD nodes, relationships
WITH REVERSE(nodes) AS result
RETURN result
"

To __exclude__ specific nodes, use the following:
`blackListNodes: List<Node>`












## AND/OR Graph Traversal Algorithm

// For a given vulnerability
// return (the list of) AND or OR nodes
...

// For each AND/OR node, find children nodes 
UNWIND nodes AS n
    CALL {
        WITH n
        MATCH (c)-[*1]->(n)
        WITH COLLECT(c) as children
        UNWIND children AS child
        WITH COLLECT( EXISTS( (:Container {name: 'Nginx'})-[*]->(child) ) ) AS connections
        RETURN connections
    }
    // Evaluate AND/OR conditions
    CALL {
        WITH n, connections
        RETURN
        CASE n.name
        WHEN 'AND_NODE'  THEN ALL(con in connections WHERE con=True)
        WHEN 'OR_NODE' THEN ANY(con in connections WHERE con=True)
        END AS result
    }

// Combine all AND/OR condition results
WITH COLLECT(result) AS results
RETURN ALL(r in results WHERE r=True)



## Vulnerabilities

We can retrieve a list of vulnerabilities affecting the Docker engine (and its subcomponents, like containerd and runc) by checking the Docker releases webpage.

### (Docker) Container Engine
https://docs.docker.com/engine/release-notes/

v20.10
    - CVE-2022-24769
    - CVE-2021-41092
    - CVE-2021-41190 (containerd)
    - CVE-2021-41103 (containerd)
    - CVE-2021-41089
    - CVE-2021-41091
    - CVE-2021-21285
    - CVE-2021-21284
    - CVE-2021-30465 (runc)
    - CVE-2021-21334 (containerd)
    - CVE-2019-14271

https://docs.docker.com/engine/release-notes/19.03/
v19.03

### Container CVE List

 - https://www.container-security.site/general_information/container_cve_list.html

### Docker security non-events

 - https://docs.docker.com/engine/security/non-events/

 - https://blog.pentesteracademy.com/abusing-sys-module-capability-to-perform-docker-container-breakout-cf5c29956edd




------------------------------------------------------------------------

# Proof of Concept

This file shows the list of commands to use for a proof of concept of this tool.

For Vagrant Ubuntu VM: `export NEO4J_ADDRESS="192.168.2.5"`.

Cleaning up the environment: `python main.py --remove-all`

Within the Neo4J browser, run: `:config initialNodeDisplay: 1000`


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
MERGE (a:ROOT_NODE{key:'a'})
MERGE (b:AND_NODE{key:'b'})
MERGE (c:OR_NODE{key:'c'})
MERGE (d:OR_NODE{key:'d'})
MERGE (e:AND_NODE{key:'e'})
MERGE (f:RED{key:'f'})
MERGE (g:GREEN{key:'g'})
MERGE (h:RED{key:'h'})
MERGE (i:RED{key:'i'})
MERGE (j:GREEN{key:'j'})
MERGE (k:GREEN{key:'k'})

MERGE (k)-[:AND]->(e)
MERGE (j)-[:AND]->(e)
MERGE (e)-[:OR]->(d)
MERGE (i)-[:OR]->(d)
MERGE (f)-[:OR]->(c)
MERGE (g)-[:OR]->(c)
MERGE (h)-[:OR]->(c)
MERGE (c)-[:AND]->(b)
MERGE (d)-[:AND]->(b)
MERGE (b)-[:OR]->(a)
"


Examples of Neo4J queries to check whether a container is vulnerable to a specific vulnerability:

"
...
"


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

