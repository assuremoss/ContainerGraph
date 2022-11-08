
CVEs = {

    'vuln1': """
    MERGE (m:MITRE:TACTIC {name: 'Privilege Escalation'})
    MERGE (mm:MITRE:TECHNIQUE {name: 'Escape to Host'})
    CREATE (c:CVE {name: 'ContainerEscape'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 5, needed: [], pred: gds.util.NaN()})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    MERGE (c)-[:USES]->(mm)
    MERGE (mm)-[:LEADS_TO]->(m)
    MERGE (b)-[:ROOT]->(c)
    MERGE (a)-[:OR]->(b)
    UNION
    MATCH (b:OR_NODE {name: 'OR_NODE'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(b)
    UNION
    MATCH (np:NewPriv {name: 'NewPriv'})
    MATCH (a:AND_NODE {name: 'AND_NODE'})
    MERGE (np)-[:AND]->(a)
    UNION
    MATCH (ro:NotReadOnly {name: 'NotReadOnly', object: 'Container'})
    MATCH (a:AND_NODE {name: 'AND_NODE'})
    MERGE (ro)-[:AND]->(a)
    UNION
    MATCH (c:Capability {name: 'CAP_SYS_ADMIN'})
    MATCH (a:AND_NODE {name: 'AND_NODE'})
    MERGE (c)-[:AND]->(a)
    UNION
    MATCH (s:SystemCall {name: 'mount'})
    MATCH (a:AND_NODE {name: 'AND_NODE'})
    MERGE (s)-[:AND]->(a)
    UNION
    MATCH (cc:ContainerConfig {name: 'root', type: 'user'})
    MATCH (a:AND_NODE {name: 'AND_NODE'})
    MERGE (cc)-[:AND]->(a)
    """,

    'vuln2': """
    MERGE (m:MITRE:TACTIC {name: 'Privilege Escalation'})
    MERGE (mm:MITRE:TECHNIQUE {name: 'Exploitation'})
    CREATE (c:CVE {name: 'CVE-2022-0847'})
    CREATE (cvss:CVSS {name: 'CVSS_score', cve: 'CVE-2022-0847', score_v3: 7.8})
    CREATE (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    MERGE (mm)-[:LEADS_TO]->(m)
    MERGE (c)-[:USES]->(mm)
    MERGE (b)-[:ROOT]->(c)
    MERGE (c)-[:HAS_SEVERITY]->(cvss)
    UNION 
    MATCH (kv:KernelVersion {name: '5.4'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.9'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.10'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.15'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.16'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln2'})
    MERGE (kv)-[:OR]->(b)
    """,

    'vuln3': """
    MERGE (m:MITRE:TACTIC {name: 'Privilege Escalation'})
    MERGE (mm:MITRE:TECHNIQUE {name: 'Exploitation'})
    CREATE (c:CVE {name: 'CVE-2022-0185'})
    CREATE (cvss:CVSS {name: 'CVSS_score', cve: 'CVE-2022-0185', score_v3: 8.4})
    CREATE (a:AND_NODE {name: 'AND_NODE', vuln: 'vuln3', key: 'and1', weight: 0, todo: 2, needed: [], pred: gds.util.NaN()})
    CREATE (a1:AND_NODE {name: 'AND_NODE', vuln: 'vuln3', key: 'and2', weight: 0, todo: 2, needed: [], pred: gds.util.NaN()})
    CREATE (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or1', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    CREATE (b2:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    MERGE (mm)-[:LEADS_TO]->(m)
    MERGE (c)-[:USES]->(mm)
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (b2)-[:AND]->(a)
    MERGE (c)-[:HAS_SEVERITY]->(cvss)
    UNION 
    MATCH (b2:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or1'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(b2)
    UNION
    MATCH (b2:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or1'})
    MATCH (a1:AND_NODE {name: 'AND_NODE', vuln: 'vuln3', key: 'and2'})
    MERGE (a1)-[:OR]->(b2)
    UNION
    MATCH (a1:AND_NODE {name: 'AND_NODE', vuln: 'vuln3', key: 'and2'})
    MATCH (cc:ContainerConfig {name: 'root', type: 'user'})
    MERGE (cc)-[:AND]->(a1)
    UNION
    MATCH (a1:AND_NODE {name: 'AND_NODE', vuln: 'vuln3', key: 'and2'})
    MATCH (cap:Capability {name: 'CAP_SYS_ADMIN'})
    MERGE (cap)-[:AND]->(a1)
    UNION
    MATCH (kv:KernelVersion {name: '5.1'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.2'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.3'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.4'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.5'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.6'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.7'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.8'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.9'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.10'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.11'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.12'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.13'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.14'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.15'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    UNION
    MATCH (kv:KernelVersion {name: '5.16'})
    MATCH (b:OR_NODE {name: 'OR_NODE', vuln: 'vuln3', key: 'or2'})
    MERGE (kv)-[:OR]->(b)
    """





}