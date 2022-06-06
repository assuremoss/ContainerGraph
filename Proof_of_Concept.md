
---
# Proof of Concept

This file shows the list of commands to use for a proof of concept of this tool.

First of all, became root `sudo su` and create a pipenv shell `pipenv shell`. Then, install Python requirements `pipenv install`.

For Vagrant Ubuntu VM: `export NEO4J_ADDRESS="192.168.2.5"`.

Cleaning up the environment: `python main.py --remove all`

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

## Example with Escape_1

https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/

1. Default container (14 CAPs and 320 syscalls):
`python main.py --run docker run -it --rm -d nginx`

2. Privileged container (41 CAPs and 364 syscalls):
`python main.py --run docker run -it --rm -d --privileged nginx`

3. Unconfined security profile:
`python main.py --run docker run -it --rm -d --security-opt apparmor=unconfined --cap-add=SYS_ADMIN nginx`

4. Custom security profiles:
`python main.py --run docker run -it --rm -d --security-opt apparmor=custom nginx`

5. Manually add Escape_1 to Neo4J.

6. `docker ps` & Analyze containers.
`python main.py --analyze <container_id> Escape_1`


---
## Fixing Container Configurations

The list of possible fixes depends on the set of leaves belonging to valid paths within the vulnerability AND/OR tree. Invalidating one or more assumptions of an attack not part of a valid path, perhaps makes the configuration more secure (e.g., by restricting the set of available system calls), although without invalidating the attack itself.

Steps to suggest effective fixes: 

1. Split the set of assumptions (leaves in the tree) into an effective set (blocking the attack) and an evocative set (making the configuration more secure without blocking the attack).
    - any existing algorithm for AND/OR trees? Perhaps we need a custom procedure for this.

2. Rank the fixes effective set using AHP.
    - we need to define a list of criteria

3. Apply the choosen fix. There is no need to run again the vulnerability query because based on the set from which the fix comes from (effective or evocative), we already know if the attack is still possible or not.



### Multi-vulnerabilities

https://sysdig.com/blog/vulnerability-score-cvss-meaning/




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
## Docker and AppArmor

how to load a new profile

url


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

## Single path - Unique Fix

**OR-tree Test**

MERGE (l:CVE {name: 'CVE_1', cvss: 9})
MERGE (m:OR_NODE {key:'OR_NODE'})
MERGE (o:DockerVersion {key:'o', property: 'RED', weight: 5})
MERGE (p:containerdVersion {key:'p', property: 'RED', weight: 7})
MERGE (q:runcVersion {key:'q', property: 'RED', weight: 9})
MERGE (r:KernelVersion {key:'r', property: 'RED', weight: 6})

MERGE (m)-[:OR]->(l)
MERGE (o)-[:OR]->(m)
MERGE (p)-[:OR]->(m)
MERGE (q)-[:OR]->(m)
MERGE (r)-[:OR]->(m)

`python vuln_tree_taversal.py`


## Single path - Multiple Fixes

**AND-tree Test**

MERGE (l:CVE {name: 'CVE_1', cvss: 9})
MERGE (m:AND_NODE {key:'AND_NODE'})
MERGE (o:Capability {name:'SYS_ADMIN', property: 'GREEN', weight: 10})
MERGE (p:SystemCall {name:'mount', property: 'GREEN', weight: 7})
MERGE (q:NoNewPriv {name:'NoNewPriv', property: 'GREEN', weight: 5})
MERGE (r:SystemCall {name:'unshare', property: 'RED', weight: 7})

MERGE (m)-[:AND]->(l)
MERGE (o)-[:AND]->(m)
MERGE (p)-[:AND]->(m)
MERGE (q)-[:AND]->(m)
MERGE (r)-[:AND]->(m)

`python vuln_tree_taversal.py`


## Multiple paths - Multiple Fixes

**Escape 1**

MERGE (a:CVE {name: 'CVE_1', cvss: 8})
MERGE (b:OR_NODE {key:'OR_NODE'})
MERGE (c:AND_NODE {key:'AND_NODE'})

MERGE (i:LEAF {key:'d', name: 'PrivPermissions', property: 'RED', weight: 100})
MERGE (f:LEAF {key:'f', property: 'RED', weight: 5})
MERGE (g:LEAF {key:'g', property: 'GREEN', weight: 6})
MERGE (h:LEAF {key:'h', property: 'GREEN', weight: 7})

MERGE (b)-[:OR]->(a)
MERGE (i)-[:OR]->(b)
MERGE (c)-[:OR]->(b)
MERGE (f)-[:AND]->(c)
MERGE (g)-[:AND]->(c)
MERGE (h)-[:AND]->(c)

`python vuln_tree_taversal.py`





### TEST data

MERGE (a:CVE {name: 'CVE_2', cvss: 7})
MERGE (b:AND_NODE {name:'AND_NODE'})
MERGE (c:OR_NODE {name:'OR_NODE'})
MERGE (d:OR_NODE {name:'OR_NODE'})
MERGE (e:AND_NODE {name:'AND_NODE'})
MERGE (f:LEAF {key:'f', property: 'RED', weight: 6})
MERGE (g:LEAF {key:'g', property: 'GREEN', weight: 6})
MERGE (h:LEAF {key:'h', property: 'RED', weight: 6})
MERGE (i:LEAF {key:'i', property: 'RED', weight: 100})
MERGE (j:LEAF {key:'j', property: 'GREEN', weight: 5})
MERGE (k:LEAF {key:'k', property: 'GREEN', weight: 7})

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



### Compute Path Risk

MERGE (att:ATTACK {name: 'ATTACK'})
MERGE (dep:DEPLOYMENT {name: 'DEPLOYMENT'})

MERGE ()-[:r]->(att)
MERGE (dep)-[:r]->()




---
# Escape_1 Neo4J Code

MERGE (p:Permissions:Privileged {name: 'Privileged'})
MERGE (m:MITRE:TACTIC {name: 'Privilege Escalation'})
MERGE (mm:MITRE:TECHNIQUE {name: 'Escape to Host'})
MERGE (c:CVE {name: 'Escape_1'})
MERGE (a:AND_NODE {key: 'AND_NODE'})
MERGE (b:OR_NODE {key: 'OR_NODE'})
MERGE (mm)-[:LEADS_TO]->(m)
MERGE (c)-[:EXPLOITS]->(mm)
MERGE (b)-[:OR]->(c)
MERGE (a)-[:OR]->(b)
UNION
MATCH (b:OR_NODE {key: 'OR_NODE'})
MATCH (p:Permissions:Privileged)
MERGE (p)-[:OR]->(b)
UNION
MATCH (np:NoNewPriv {name: 'NoNewPriv'})
MATCH (a:AND_NODE {key: 'AND_NODE'})
MERGE (np)-[:AND]->(a)
UNION
MATCH (ro:NotReadOnly {name: 'NotReadOnly', object: 'Container'})
MATCH (a:AND_NODE {key: 'AND_NODE'})
MERGE (ro)-[:AND]->(a)
UNION
MATCH (c:Capability {name: 'CAP_SYS_ADMIN'})
MATCH (a:AND_NODE {key: 'AND_NODE'})
MERGE (c)-[:AND]->(a)
UNION
MATCH (s:SystemCall {name: 'mount'})
MATCH (a:AND_NODE {key: 'AND_NODE'})
MERGE (s)-[:AND]->(a)
UNION
MATCH (cc:ContainerConfig {name: 'root'})
MATCH (a:AND_NODE {key: 'AND_NODE'})
MERGE (cc)-[:AND]->(a)