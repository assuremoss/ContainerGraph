
## Permissions

The **--privileged** flag overrides all other security options (e.g. AppArmor or Seccomp profiles).



## MAC (Mandatory Access Control)

Intro...


## Seccomp - Secure Compute Mode - SECure COMPuting with filters

Seccomp allows for filtering the syscalls invoked by a process and can thereby be used to restrict which syscalls a given process is allowed to execute. Many software projects, such as Android, Flatpak, Chrome, and Firefox, use seccomp to tighten security further.

The Linux kernel has a few hundred system calls, but most of them are not needed by any given process. If a process can be compromised and tricked into making other system calls, though, it may lead to a security vulnerability that could result in the compromise of the whole system. By restricting what system calls can be made, we can reduce the kernel's attack surface.

The seccomp filter mode allows developers to write BPF programs that determine whether a given system call will be allowed or not. That decision can be based on the system call number and on the argument values, which come from the registers (up to six) in which they are passed.

The filter is expressed as a Berkeley Packet Filter (BPF) program, as with socket filters, except that the data operated on is related to the system call being made: system call number (the number depends on the architecture being used, that's why it is important to specify it) and the system call arguments.

We do only consider the **X86_64 architecture**.

[1] https://itnext.io/seccomp-in-kubernetes-part-i-7-things-you-should-know-before-you-even-start-97502ad6b6d6
[2] https://itnext.io/seccomp-in-kubernetes-part-2-crafting-custom-seccomp-profiles-for-your-applications-c28c658f676e
[3] https://itnext.io/seccomp-in-kubernetes-part-3-the-new-syntax-plus-some-advanced-topics-95dd3835263a
[4] https://lwn.net/Articles/656307/ 
[5] https://www.kernel.org/doc/Documentation/prctl/seccomp_filter.txt


**Docker and Seccomp**

Docker, by default, uses a default Seccomp profile that disables 44 out of more than 300 system calls (the full list is here: https://docs.docker.com/engine/security/seccomp/#significant-syscalls-blocked-by-the-default-profile).

There is also a set of 15 system calls that a Docker container needs to properly function and run (the full list is here: https://github.com/moby/moby/issues/22252).

We've seen based on this that a typical **container uses between 40 and 70 syscalls** [1].

[1] https://blog.aquasec.com/aqua-3.2-preventing-container-breakouts-with-dynamic-system-call-profiling


### No New Privileges

The no_new_privs bit (since Linux 3.5) is a new, generic mechanism to make it safe for a process to modify its execution environment in a manner that persists across execve. Any task can set no_new_privs. Once the bit is set, it is inherited across fork, clone, and execve and cannot be unset.  With no_new_privs set, execve
promises not to grant the privilege to do anything that could not have been done without the execve call.  For example, the setuid and setgid bits will no longer change the uid or gid; file capabilities will not add to the permitted set, and LSMs will not relax constraints after execve.

By itself, no_new_privs can be used to reduce the attack surface available to an unprivileged user. If everything running with a given uid has no_new_privs set, then that uid will be unable to escalate its privileges by directly attacking setuid, setgid, and fcap-using binaries; it will need to compromise something without the no_new_privs bit set first.

[1] https://www.kernel.org/doc/Documentation/prctl/no_new_privs.txt


## AppArmor






## Containers and Syscalls

The default Seccomp profile provides a good a balance between tightening the security while remaining portable to allow most workloads to run without receiving permission errors.

However, the default filter is pretty loose, and it still allows more than 300 of the 435 syscalls on Linux 5.3 x86_64. The high number of available syscalls is essential to support as many containers as possible. However, according to Aqua Sec, most containers require only 40 to 70 syscalls. This means that the syscall attack surface of an average container could further be reduced by around 80 percent.

[1] https://www.redhat.com/sysadmin/container-security-seccomp
[2] https://blog.aquasec.com/aqua-3.2-preventing-container-breakouts-with-dynamic-system-call-profiling

To restrict more syscalls than the default filter, we face the problem of finding out **which syscalls a container actually needs**.

There are several solutions available to find out which system calls a container is using:

 - strace & ptrace (considerable performance impects) **TO_CHECK**

 - audit log (e.g. used by Seccomp): however, when using multiple container in parallel, it is not possible to track which process called which system call. There is an ongoing debade within the Linux kernel community about this (https://lwn.net/Articles/750313/). **TO_CHECK**

 - Sysdig Falco - system call tracker

 - eBPF solutions: Tracee by Aqua, oci-seccomp-bpf-hook, syscall2seccomp

[1] https://github.com/containers/oci-seccomp-bpf-hook
[2] https://github.com/antitree/syscall2seccomp
[3] https://sysdig.com/blog/sysdig-vs-dtrace-vs-strace-a-technical-discussion/
[4] https://sysdig.com/blog/selinux-seccomp-falco-technical-discussion/


## eBPF

https://lwn.net/Articles/603983/


## Kernel Versions

Within the knowledge graph, we model only the kernel version in the format of "<kernel version>.<major revision>" (e.g. "3.12"); we do ignore minor revisions and distro-specific suffixes. Thus 3.12.25-gentoo and 3.12-1-amd64 will both be modeled as version 3.12, with kernel: 3 and major 12.



## AND/OR trees - Neo4J

Reference: 

[1] https://neo4j.com/labs/apoc/4.1/overview/apoc.path/apoc.path.subgraphNodes/

[2] https://stackoverflow.com/questions/71815007/given-a-neo4j-tree-with-a-weight-on-its-leaves-how-do-i-return-for-each-node-th/71820674#71820674


**Test Data**

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


**Python dict**

{
    'a': ['b']
    'b': ['c', 'd']
    'c': ['GREEN', 'RED', 'RED']
    'd': ['RED', e]
    'e': ['GREEN', 'GREEN']
}



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

