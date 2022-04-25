
---
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


## 3 - Add Docker Container

```bash

python main.py --run docker run --name test -it --rm -d nginx 

docker ps 
```

Show Neo4J graph.


## 4 - Show Charts

Show updated Neo4J knowledge graph and running containers `docker ps`.

Describe the `vulns.json` file (i.e. how we represent container vulnerabilities and misconfigurations and how we geenrate the corresponding queries).


---
# Container Permissions

With the current configuration, we model:

 - 364 system calls

 - 41 Linux capabilities

The Docker (Seccomp and Apparmor) default profiles block 45 system calls and grant only 14 capabilities.

## Examples

1. Privileged container (41 CAPs and 364 syscalls):
`python main.py --run docker run -it --rm -d --privileged nginx`

2. Default container (14 CAPs and 320 syscalls):
`python main.py --run docker run -it --rm -d nginx`

3. Custom capability (15 CAPs and 327 syscalls):
`python main.py --run docker run -it --rm -d --cap-add sys_admin nginx`

4. Custom profiles container (5 CAPs and 313 syscalls):
`python main.py --run docker run -it --rm -d --security-opt seccomp=./files/Seccomp/custom-nginx.json --security-opt apparmor=docker-nginx nginx`


---
## Container Capabilities

### To enforce an Apparmor profile into a container

1. Save the profile into `/etc/apparmor.d/containers/`.

2. Load the profile: `sudo apparmor_parser -r -W /etc/apparmor.d/containers/<profile_name>`.

3. Run the container with the custom profile: `--security-opt "apparmor=custom-profile"`.

[1] https://docs.docker.com/engine/security/apparmor/

### List capabilities

To list the capabilities belonging to a container, we can use the following command: `apk add -U libcap; capsh --print`.

Alternatively, we can use `getpcaps` in the following manner:

```bash
docker top <container_id>
getpcaps <container_pid>
``` 

Rules governing how capabilities are inherited when starting a process:

 - P'(ambient)
 - P'(permitted)
 - P'(effective)
 - P'(inheritable)

These are usually represented as: `+eip`.

[1] https://blog.container-solutions.com/linux-capabilities-in-practice


---
## Vulnerabilities

A list of vulnerabilities affecting the Docker engine (and its subcomponents, like containerd and runc) can be retrived from the Docker releases webpage.

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


---
# AND/OR trees - Neo4J Algorithm

An algorithm to traverse and analyze AND/OR trees implemented in Python and Neo4J.

## Test tree

MERGE (a:ROOT_NODE{key:'a'})
MERGE (b:AND_NODE{key:'b'})
MERGE (c:OR_NODE{key:'c'})
MERGE (d:OR_NODE{key:'d'})
MERGE (e:AND_NODE{key:'e'})
MERGE (f:LEAF{key:'f', property: 'RED'})
MERGE (g:LEAF{key:'g', property: 'GREEN'})
MERGE (h:LEAF{key:'h', property: 'RED'})
MERGE (i:LEAF{key:'i', property: 'RED'})
MERGE (j:LEAF{key:'j', property: 'GREEN'})
MERGE (k:LEAF{key:'k', property: 'GREEN'})

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

