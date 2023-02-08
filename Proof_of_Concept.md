
# TESTING

Test the tool on the following sequence of containers:

    1, 2, 5, 10, 20, 50, 100, 200, 500


First plot shows the time to add containers to the tool/database:

    `$ time ./testing.sh N`


Second plot shows the time to fix all (privileged) containers; we automatically reply yes each time the tool prompts whether to fix a given container for a specific vulnerability (`yes | python main.py --analyze`)

    `$ yes | time python main.py --analyze`





































# DEMO TOOL

For terminal demos, use Demo Magic
https://github.com/paxtonhare/demo-magic




# EVALUATION

> Test with many (~50/100) qualitatively different CVEs
    - we assume the CVE pre/post conditions are given

> An alternative is also to find what is the best combination of Linux kernel and Docker engine versions, and what is the impact of different container configurations on that.

> Trovare diverse configurazioni docker o report in cui dicono che x% of containers run as root, with CVE CVSS score 9, etc.
 - write to the report authors if we can get the docker run configurations (Linkedin)
 - check Files Capabilities (also in DockerHub) https://www.cyberark.com/resources/threat-research-blog/how-docker-made-me-more-capable-and-the-host-less-secure

> Scaling up. Demonstrate that the tool can scale up to 1...n containers



# TODO

> Fix the algorithm (green and blue paths)

> CVEs automatic integration
    Check following papers (mainly, we need to find references on previous work representing CVEs as AND/OR trees and automatic "integration" of CVE in databases)
    - https://link.springer.com/content/pdf/10.1007/978-3-319-18467-8.pdf
    - https://ieeexplore.ieee.org/document/5161653
    - https://link.springer.com/content/pdf/10.1007/978-3-319-24249-1.pdf
    - https://link.springer.com/content/pdf/10.1007/978-3-319-03964-0.pdf
    - https://link.springer.com/content/pdf/10.1007/b104908.pdf
    - https://link.springer.com/content/pdf/10.1007/978-3-030-57024-8.pdf
    - https://mal-lang.org/

> Process & File Capabilities for evaluation
    - https://man7.org/linux/man-pages/man7/capabilities.7.html
    - https://github.com/RHsyseng/container-security-demos
    - Check File CAPs in container images in DockerHub:
        `` export an image to a rootfs folder https://blog.heroku.com/terrier-open-source-identifying-analyzing-containers
        `getcap -r /path/to/image/root/fs/ 2>/dev/null` 

    https://sysdig.com/blog/vulnerability-score-cvss-meaning/
    https://man7.org/linux/man-pages/man7/capabilities.7.html
    https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33528.pdf
    https://sites.google.com/site/fullycapable/inheriting-privilege?authuser=0
    https://www.linuxjournal.com/magazine/making-root-unprivileged
    https://blog.heroku.com/terrier-open-source-identifying-analyzing-containers
    

> Runtime events integration ?

> Optimaze Neo4j nodes/edges structure
> Python best practices


> Allow users to customize CVE assumption (tree leaf) weights. 
   - we assume the same custom weight is the same for all containers
   - alternatively, we could assign a weight to the edge going from Deployment to the leaf

> Allow users to rank CVEs based on the CVSS score
    - Eventually, we can ask the user to provide custom values for the Impact Subscore Modifiers (e.g., in a config file).
      https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator


---
# Proof of Concept

This file shows the list of commands to use for a proof of concept of this tool. Read the README.md file.

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

python main.py --run docker run --name nginx -it --rm -d nginx 

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
`python main.py --run docker run --name nginxpriv -it --rm -d --privileged nginx`

3. Unconfined security profile:
`python main.py --run docker run --name nginxcustom -it --rm -d --security-opt apparmor=unconfined --cap-add=SYS_ADMIN nginx`

4. Custom security profiles:
`python main.py --run docker run -it --rm -d --security-opt apparmor=custom nginx`

5. Manually add Escape_1 to Neo4J.

6. `docker ps` & Analyze containers.
`python main.py --analyze <container_id> Escape_1`


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

