from container_builder import build_Container
from infrastructure_parser import get_Infrastructure
from permission_taxonomy import create_Permissions
from XML_sec_chart import generate_XML_chart
from XML_sec_chart import update_XML_chart


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
    # INDEPENDENT from containers


# 3. Generate (first version of) the Security Charts

XML_sec_chart = generate_XML_chart(cont, infra)

#neo4j_sec_chart = generate_Neo4J_sec_chart(cont)


# 4. Docker run
"""
How do we capture the docker run parameters ???????


Same as for the Dockerfile, also at this step we can alert
for dangerous parameters (e.g. privileged).


 - Eventually change/update the Permissions class of the Container object
 - Update security charts based on docker run parameters
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


# 6. MONITOR container drift
"""
 - eBPF monitors [only] container events
"""


# 7. PREVENT container drift
"""
 - MAC and SELinux
"""