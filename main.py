from container_builder import build_Container
from infrastructure_parser import get_Infrastructure
from permission_taxonomy import create_Permissions
from XML_sec_chart import generate_XML_chart
from Neo4J_sec_chart import generate_Neo4J_sec_chart


# 1. Program initialization
# - logo
print("My awesome script!")


# 2. Retrieve Image & build Container 
cont = build_Container()
"""
While reconstructing the Dockerfile, we can alert on dangerous
configurations (e.g. based on the CIS Benchmark).
"""

    # 2.1 Retrieve the underlying infrastructure
infra = get_Infrastructure()

    # 2.2 Create a container permissions class
"""
We need to decide a granularity for this.

Linux Capabilities 
 - how to trace capabilities: https://stackoverflow.com/questions/35469038/how-to-find-out-what-linux-capabilities-a-process-requires-to-work/47991611#47991611)
 - bcc capable tool: https://www.brendangregg.com/blog/2016-10-01/linux-bcc-security-capabilities.html
 - Docker default capabilities: https://github.com/moby/moby/blob/master/oci/caps/defaults.go#L6-L19

Linux System Calls (which system calls are allowed and which not)

Difference between --cap-add=ALL and --privileged
https://stackoverflow.com/questions/66635237/difference-between-privileged-and-cap-add-all-in-docker
"""


# 3. Generate (first version of) the Security Charts

XML_sec_chart = generate_XML_chart(cont, infra)
neo4j_sec_chart = generate_Neo4J_sec_chart(cont, infra)


# 4. Docker run
"""
Network type: "type": ["bridge", "host", "overlay", "macvlan"]


We capture the docker run parameters using the Python Docker API!


Same as for the Dockerfile, also at this step we can alert
for dangerous parameters (e.g. privileged).


 - Eventually change/update the Permissions class of the Container object
 - Update security charts based on docker run parameters


From now on, we need to continuosly check if the container is alive.
    Option: https://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python

Get the container PID:
    $ docker run ... > /dev/null& --> gives us the container PID? TO CHECK

    $ docker inspect -f '{{.State.Pid}}' <container id>
     - using cgroups systemd-cgls
     - child process of containerd-shim (pgrep containerd-shim, pgrep -P)
    https://stackoverflow.com/questions/34878808/finding-docker-container-processes-from-host-point-of-view
"""


# 5. Update security charts
"""
- XML security chart
- Neo4J security chart
""" 


### At this point, we have the first container snapshot.
"""
HOW TO build a (graphic) container life timeline ?
"""



### Entering eBPF ###


# 6. MONITOR container drift
"""
 - eBPF monitors [only] container events
"""


# 7. PREVENT container drift
"""
 - MAC and SELinux
"""