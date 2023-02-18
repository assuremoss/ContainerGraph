from parse_perm_file import parse_perm_taxonomy
from packaging import version


def compare_versions_range(v1, v, v2) : 
    """
    Return True is v1 <= v <= v2, else False.
    """
    return version.Version(v1) <= version.Version(v) <= version.Version(v2)


def initialize_escape_cves() : 
    ##################
    ### Container Escapes ###

    list_of_queries = []

    # ContainerEscape1 --- using cgroup notify_on_release()
    query = """
    CREATE (c:CVE {name: 'ContainerEscape1'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 5, needed: [], pred: gds.util.NaN()})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    WITH a, b, c
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
    """
    query = query.strip().replace('\n', '')
    list_of_queries.append(query)

    # ContainerEscape2 --- by loading a kernel module
    query = """
    CREATE (c:CVE {name: 'ContainerEscape2'})
    CREATE (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape2', weight: 0, todo: 2, needed: [], pred: gds.util.NaN()})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'ContainerEscape2'})
    WITH a, b, c
    MERGE (b)-[:ROOT]->(c)
    MERGE (a)-[:OR]->(b)
    UNION
    MATCH (b:OR_NODE {name: 'OR_NODE', key: 'ContainerEscape2'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(b)
    UNION
    MATCH (c:Capability {name: 'CAP_SYS_MODULE'})
    MATCH (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape2'})
    MERGE (c)-[:AND]->(a)
    UNION
    MATCH (cc:ContainerConfig {name: 'root', type: 'user'})
    MATCH (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape2'})
    MERGE (cc)-[:AND]->(a)
    """
    query = query.strip().replace('\n', '')
    list_of_queries.append(query)

    # ContainerEscape3 --- using ptrace
    query = """
    CREATE (c:CVE {name: 'ContainerEscape3'})
    CREATE (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape3', weight: 0, todo: 2, needed: [], pred: gds.util.NaN()})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'ContainerEscape3'})
    WITH a, b, c
    MERGE (b)-[:ROOT]->(c)
    MERGE (a)-[:OR]->(b)
    UNION
    MATCH (b:OR_NODE {name: 'OR_NODE', key: 'ContainerEscape3'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(b)
    UNION
    MATCH (c:Capability {name: 'CAP_SYS_PTRACE'})
    MATCH (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape3'})
    MERGE (c)-[:AND]->(a)
    UNION
    MATCH (c:Capability {name: 'CAP_SYS_ADMIN'})
    MATCH (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape3'})
    MERGE (c)-[:AND]->(a)
    UNION
    MATCH (cc:ContainerConfig {name: 'root', type: 'user'})
    MATCH (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape3'})
    MERGE (cc)-[:AND]->(a)
    UNION
    CREATE (cc:ContainerConfig {name: 'PidNamespace', type: 'host', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    WITH cc
    MATCH (a:AND_NODE {name: 'AND_NODE', key: 'ContainerEscape3'})
    MERGE (cc)-[:AND]->(a);
    """
    query = query.strip().replace('\n', '')
    list_of_queries.append(query)

    return list_of_queries


def initialize_engine_cves() : 
    ##################
    ### runc CVEs ###

    list_of_queries = []
    result = parse_perm_taxonomy()
    
    # CVE-2022-29162
    query = """
    CREATE (c:CVE {name: 'CVE-2022-29162'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2022-29162'})
    MERGE (b)-[:ROOT]->(c)
    UNION 
    """
    for r_v in reversed(result['runc_v']) :        
        if version.Version(r_v) <= version.Version('1.1.1') :
            query += "MATCH (rv:runcVersion {name: '" + r_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-29162'}) MERGE (rv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2022-24769
    query = """
    CREATE (c:CVE {name: 'CVE-2022-24769'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2022-24769'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for r_v in reversed(result['runc_v']) :
        if version.Version(r_v) <= version.Version('1.1.1') :
            query += "MATCH (rv:runcVersion {name: '" + r_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-24769'}) MERGE (rv)-[:OR]->(b) UNION "
        else : break    
    for d_v in reversed(result['docker_v']) : 
        if version.Version(d_v) <= version.Version('20.10.13') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-24769'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2021-43784
    query = """
    CREATE (c:CVE {name: 'CVE-2021-43784'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2021-43784'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for r_v in reversed(result['runc_v']) :
        if version.Version(r_v) <= version.Version('1.0.2') :
            query += "MATCH (rv:runcVersion {name: '" + r_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2021-43784'}) MERGE (rv)-[:OR]->(b) UNION "  
        else : break 
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2021-30465

    # CVE-2019-19921

    # CVE-2019-16884
    query = """
    CREATE (c:CVE {name: 'CVE-2019-16884'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2019-16884'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for r_v in reversed(result['runc_v']) :
        if version.Version(r_v) <= version.Version('1.0.0') :
            query += "MATCH (rv:runcVersion {name: '" + r_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2019-16884'}) MERGE (rv)-[:OR]->(b) UNION "
        else : break
    for d_v in reversed(result['docker_v']) : 
        if version.Version(d_v) <= version.Version('19.03.2') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2019-16884'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2019-5736
    query = """
    CREATE (c:CVE {name: 'CVE-2019-5736'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2019-5736'})
    CREATE (aa:AND_NODE {name: 'AND_NODE2', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2019-5736'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2019-5736'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2019-5736'})
    WITH c, a, aa, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    MERGE (aa)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2019-5736'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'}) 
    MERGE (p)-[:OR]->(bb) 
    UNION
    MATCH (aa:AND_NODE {name: 'AND_NODE2', key: 'CVE-2019-5736'})
    MATCH (cc:ContainerConfig {name: 'root', type: 'user'})
    MERGE (cc)-[:AND]->(aa) 
    UNION
    MATCH (aa:AND_NODE {name: 'AND_NODE2', key: 'CVE-2019-5736'})
    MATCH (ro:NotReadOnly {name: 'NotReadOnly', object: 'Container'})
    MERGE (ro)-[:AND]->(aa)    
    UNION
    """
    for r_v in reversed(result['runc_v']) :
        if version.Version(r_v) <= version.Version('1.0.0') :
            query += "MATCH (rv:runcVersion {name: '" + r_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2019-5736'}) MERGE (rv)-[:OR]->(b) UNION "
        else : break
    for d_v in reversed(result['docker_v']) : 
        if version.Version(d_v) <= version.Version('18.09.1') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2019-5736'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-3697
    query = """
    CREATE (c:CVE {name: 'CVE-2016-3697'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-3697'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for r_v in reversed(result['runc_v']) :
        if version.Version(r_v) <= version.Version('0.0.9') :
            query += "MATCH (rv:runcVersion {name: '" + r_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-3697'}) MERGE (rv)-[:OR]->(b) UNION "
        else : break
    for d_v in reversed(result['docker_v']) : 
        if version.Version(d_v) <= version.Version('1.11.1') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-3697'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')      
    list_of_queries.append(query)

    ##################
    ### containerd CVEs ###
    
    # CVE-2022-31030
    query = """
    CREATE (c:CVE {name: 'CVE-2022-31030'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2022-31030'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for c_v in reversed(result['containerd_v']) :
        if version.Version(c_v) <= version.Version('1.5.12') or compare_versions_range('1.6.0', c_v, '1.6.5') :
            query += "MATCH (cv:containerdVersion {name: '" + c_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-31030'}) MERGE (cv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2022-23648

    # CVE-2021-43816 
    query = """
    CREATE (c:CVE {name: 'CVE-2021-43816'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2021-43816'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for c_v in reversed(result['containerd_v']) :
        if compare_versions_range('1.5.0', c_v, '1.5.8') :
            query += "MATCH (cv:containerdVersion {name: '" + c_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2021-43816'}) MERGE (cv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2021-41103
    query = """
    CREATE (c:CVE {name: 'CVE-2021-41103'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2021-41103'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2021-41103'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2021-41103'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2021-41103'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'}) 
    MERGE (p)-[:OR]->(bb) 
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2021-41103'})
    MATCH (s:SystemCall {name: 'setuid'})
    MERGE (s)-[:OR]->(bb)
    UNION
    """
    for c_v in reversed(result['containerd_v']) :
        if version.Version(c_v) <= version.Version('1.4.10') or compare_versions_range('1.5.0', c_v, '1.5.6') :
            query += "MATCH (cv:containerdVersion {name: '" + c_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2021-41103'}) MERGE (cv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2021-32760

    # CVE-2021-21334
    query = """
    CREATE (c:CVE {name: 'CVE-2021-21334'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2021-21334'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for c_v in reversed(result['containerd_v']) :
        if version.Version(c_v) <= version.Version('1.3.9') or compare_versions_range('1.4.0', c_v, '1.4.3') :
            query += "MATCH (cv:containerdVersion {name: '" + c_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2021-21334'}) MERGE (cv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2020-15257
    query = """
    CREATE (c:CVE {name: 'CVE-2020-15257'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-15257'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-15257'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-15257'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2020-15257'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'}) 
    MERGE (p)-[:OR]->(bb) 
    UNION
    CREATE (cc:ContainerConfig {name: 'NetNamespace', type: 'host', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    WITH cc
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2020-15257'})
    MERGE (cc)-[:OR]->(bb)
    UNION
    """
    for c_v in reversed(result['containerd_v']) :
        if version.Version(c_v) <= version.Version('1.3.8') or compare_versions_range('1.4.0', c_v, '1.4.2') :
            query += "MATCH (cv:containerdVersion {name: '" + c_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2020-15257'}) MERGE (cv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2020-15157
    
    ##################
    ### Docker CVEs ###

    # CVE-2021-21285

    # CVE-2021-21284

    # CVE-2020-27534
    query = """
    CREATE (c:CVE {name: 'CVE-2020-27534'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-27534'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if version.Version(d_v) <= version.Version('19.03.8') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2020-27534'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)
    
    # CVE-2020-14300
    query = """
    CREATE (c:CVE {name: 'CVE-2020-14300'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-14300'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if d_v == '1.13.1' :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2020-14300'}) MERGE (dv)-[:OR]->(b) UNION "
            break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2020-14298
    query = """
    CREATE (c:CVE {name: 'CVE-2020-14298'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-14298'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if d_v == '1.13.1' :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2020-14298'}) MERGE (dv)-[:OR]->(b) UNION "
            break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2020-13401
    query = """
    CREATE (c:CVE {name: 'CVE-2020-13401'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-13401'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-13401'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-13401'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2020-13401'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'}) 
    MERGE (p)-[:OR]->(bb) 
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2020-13401'})
    MATCH (cap:Capability {name: 'CAP_NET_RAW'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if version.Version(d_v) <= version.Version('19.03.10') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2020-13401'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2019-14271

    # CVE-2019-13509
    query = """
    CREATE (c:CVE {name: 'CVE-2019-13509'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2019-13509'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if version.Version(d_v) <= version.Version('18.09.7') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2019-13509'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2019-13139
    
    # CVE-2018-15664
    query = """
    CREATE (c:CVE {name: 'CVE-2018-15664'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2018-15664'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if d_v == '17.06.1' or d_v == '17.07.0' or d_v == '17.10.0' or d_v == '17.11.0' or compare_versions_range('17.06.0', d_v, '17.06.2') or compare_versions_range('17.09.0', d_v, '17.09.1') or compare_versions_range('17.12.0', d_v, '17.12.1') or compare_versions_range('18.01.0', d_v, '18.06.0') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2018-15664'}) MERGE (dv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2018-15514

    # CVE-2018-10892
    query = """
    CREATE (c:CVE {name: 'CVE-2018-10892'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2018-10892'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if compare_versions_range('1.11.0', d_v, '18.03.1') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2018-10892'}) MERGE (dv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2017-14992

    # CVE-2016-9962
    query = """
    CREATE (c:CVE {name: 'CVE-2016-9962'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-9962'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-9962'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-9962'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-9962'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'}) 
    MERGE (p)-[:OR]->(bb) 
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-9962'})
    MATCH (cc:ContainerConfig {name: 'root', type: 'user'}) 
    MERGE (cc)-[:OR]->(bb)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if compare_versions_range('1.11.0', d_v, '1.12.6') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-9962'}) MERGE (dv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-8867

    # CVE-2016-6595
    query = """
    CREATE (c:CVE {name: 'CVE-2016-6595'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-6595'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if d_v == '1.12.0' :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-6595'}) MERGE (dv)-[:OR]->(b) UNION "
            break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2015-3631

    # CVE-2015-3630
    query = """
    CREATE (c:CVE {name: 'CVE-2015-3630'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-3630'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if version.Version(d_v) <= version.Version('1.6.2') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-3630'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2015-3627
    query = """
    CREATE (c:CVE {name: 'CVE-2015-3627'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-3627'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for d_v in reversed(result['docker_v']) :
        if version.Version(d_v) <= version.Version('1.6.2') :
            query += "MATCH (dv:DockerVersion {name: '" + d_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-3627'}) MERGE (dv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)
    
    return list_of_queries


def initialize_kernel_cves() : 
    ##################
    ### Kernel CVEs ###

    list_of_queries = []
    result = parse_perm_taxonomy()
    
    # CVE-2017-7308
    query = """
    CREATE (c:CVE {name: 'CVE-2017-7308'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-7308'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-7308'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-7308'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2017-7308'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2017-7308'})
    MATCH (cap:Capability {name: 'CAP_NET_RAW'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.10.6') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2017-7308'}) MERGE (kv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2017-5123
    query = """
    CREATE (c:CVE {name: 'CVE-2017-5123'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-5123'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if k_v == "4.13.6" or k_v == "4.13.5" or k_v == "4.13.4" or k_v == "4.13.3" or k_v == "4.13.2" or k_v == "4.13.1" or k_v == "4.13.0" :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2017-5123'}) MERGE (kv)-[:OR]->(b) UNION "      
    query = query[:-7].strip().replace('\n', '')  
    list_of_queries.append(query)
    
    # CVE-2016-4997
    query = """
    CREATE (c:CVE {name: 'CVE-2016-4997'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4997'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4997'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4997'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-4997'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-4997'})
    MATCH (cap:Capability {name: 'CAP_NET_ADMIN'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('3.19.0', k_v, '4.1.27') or compare_versions_range('4.2.0', k_v, '4.4.13') or compare_versions_range('4.5.0', k_v, '4.6.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-4997'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)
    
    # CVE-2017-6074
    query = """
    CREATE (c:CVE {name: 'CVE-2017-6074'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-6074'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-6074'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-6074'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2017-6074'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2017-6074'})
    MATCH (cap:Capability {name: 'CAP_NET_ADMIN'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.9.11') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2017-6074'}) MERGE (kv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2017-1000112
    query = """
    CREATE (c:CVE {name: 'CVE-2017-1000112'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-1000112'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-1000112'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-1000112'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2017-1000112'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2017-1000112'})
    MATCH (cap:Capability {name: 'CAP_NET_ADMIN'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.13.9') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2017-1000112'}) MERGE (kv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2017-1000253

    # CVE-2017-1000366

    # CVE-2016-0728
    query = """
    CREATE (c:CVE {name: 'CVE-2016-0728'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-0728'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-0728'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-0728'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-0728'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-0728'})
    MATCH (s:SystemCall {name: 'keyctl'})
    MERGE (s)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('3.8.0', k_v, '3.10.95') or compare_versions_range('3.11.0', k_v, '3.12.53') or compare_versions_range('3.13.0', k_v, '3.14.59') or compare_versions_range('3.15.0', k_v, '3.16.35') or compare_versions_range('3.17.0', k_v, '3.18.26') or compare_versions_range('3.19.0', k_v, '4.1.16') or compare_versions_range('4.2.0', k_v, '4.3.4') or compare_versions_range('4.4.0', k_v, '4.4.1') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-0728'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-1583
    query = """
    CREATE (c:CVE {name: 'CVE-2016-1583'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-1583'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-1583'})
    CREATE (e:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-1583'})
    CREATE (d:AND_NODE {name: 'AND_NODE2', weight: 0, todo: 42, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-1583'})
    WITH c, a, b, e, d
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (e)-[:AND]->(a)
    MERGE (d)-[:AND]->(b)
    UNION
    MATCH (p:Permissions:Privileged {name: 'Privileged'})  
    MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-1583'})
    MERGE (p)-[:OR]->(b)
    UNION
    MATCH (aa:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-1583'})
    MATCH (s:SystemCall {name: 'mount'})
    MERGE (s)-[:AND]->(aa)
    UNION
    """
    # Append all CAPs
    for cap in result['capabilities'] :
        cap = cap['name']
        query += "MATCH (cap:Capability {name: '" + cap + "'}) MATCH (d:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-1583'}) MERGE (cap)-[:AND]->(d) UNION "
    # Append kernel versions
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('2.6.19', k_v, '3.18.53') or compare_versions_range('3.19.0', k_v, '4.4.13') or compare_versions_range('4.5.0', k_v, '4.6.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-1583'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2015-8660
    query = """
    CREATE (c:CVE {name: 'CVE-2015-8660'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-8660'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-8660'})
    CREATE (e:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-8660'})
    CREATE (d:AND_NODE {name: 'AND_NODE2', weight: 0, todo: 42, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-8660'})
    WITH c, a, b, e, d
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (e)-[:AND]->(a)
    MERGE (d)-[:AND]->(b)
    UNION
    MATCH (p:Permissions:Privileged {name: 'Privileged'})  
    MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-8660'})
    MERGE (p)-[:OR]->(b)
    UNION
    MATCH (d:AND_NODE {name: 'AND_NODE2', key: 'CVE-2015-8660'})
    MATCH (s:SystemCall {name: 'mount'})
    MERGE (s)-[:AND]->(d) 
    UNION 
    """
    # Append all CAPs
    for cap in result['capabilities'] :
        cap = cap['name']
        query += "MATCH (cap:Capability {name: '" + cap + "'}) MATCH (d:AND_NODE {name: 'AND_NODE2', key: 'CVE-2015-8660'}) MERGE (cap)-[:AND]->(d) UNION "
    # Append kernel versions
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.3.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE2', key: 'CVE-2015-8660'}) MERGE (kv)-[:OR]->(b) UNION "
        else : break
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-5195
    query = """
    CREATE (c:CVE {name: 'CVE-2016-5195'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-5195'})
    CREATE (aa:AND_NODE {name: 'AND_NODE2', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-5195'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-5195'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-5195'})
    WITH c, a, aa, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    MERGE (aa)-[:OR]->(bb)
    UNION
    MATCH (p:Permissions:Privileged {name: 'Privileged'})  
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-5195'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (aa:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-5195'})
    MATCH (s:SystemCall {name: 'ptrace'})
    MERGE (s)-[:AND]->(aa)
    UNION
    CREATE (cc:ContainerConfig {name: 'MntNamespace', type: 'host', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    WITH cc
    MATCH (aa:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-5195'})
    MERGE (cc)-[:AND]->(aa)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('2.6.22', k_v, '3.2.82') or compare_versions_range('3.3.0', k_v, '3.4.112') or compare_versions_range('3.5.0', k_v, '3.10.103') or compare_versions_range('3.11.0', k_v, '3.12.65') or compare_versions_range('3.13.0', k_v, '3.16.37') or compare_versions_range('3.17.0', k_v, '3.18.43') or compare_versions_range('3.19.0', k_v, '4.1.34') or compare_versions_range('4.2.0', k_v, '4.4.25') or compare_versions_range('4.5.0', k_v, '4.7.8') or compare_versions_range('4.8.0', k_v, '4.8.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-5195'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-4557
    query = """
    CREATE (c:CVE {name: 'CVE-2016-4557'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4557'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4557'})
    CREATE (e:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4557'})
    CREATE (d:AND_NODE {name: 'AND_NODE2', weight: 0, todo: 43, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4557'})
    WITH c, a, b, e, d
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (e)-[:AND]->(a)
    MERGE (d)-[:AND]->(b)
    UNION
    MATCH (p:Permissions:Privileged {name: 'Privileged'})  
    MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-4557'})
    MERGE (p)-[:OR]->(b)
    UNION
    MERGE (cc:ContainerConfig {name: 'MntNamespace', type: 'host', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    WITH cc
    MATCH (a:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-4557'})
    MERGE (cc)-[:AND]->(a)
    UNION
    MATCH (aa:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-4557'})
    MATCH (s:SystemCall {name: 'bpf'})
    MERGE (s)-[:AND]->(aa)
    UNION
    """
    # Append all CAPs
    for cap in result['capabilities'] :
        cap = cap['name']
        query += "MATCH (cap:Capability {name: '" + cap + "'}) MATCH (d:AND_NODE {name: 'AND_NODE2', key: 'CVE-2016-4557'}) MERGE (cap)-[:AND]->(d) UNION "
    # Append kernel versions
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('4.4.0', k_v, '4.4.13') or compare_versions_range('4.5.0', k_v, '4.5.4') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-4557'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2014-0038
    ### ---> No supported kernel version for this CVE ! ###
    # query = """
    # CREATE (c:CVE {name: 'CVE-2014-0038'})
    # CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2014-0038'})
    # MERGE (b)-[:ROOT]->(c)
    # UNION
    # """
    # for k_v in reversed(result['kernel_v']) :
    #     if compare_versions_range('3.0.0', k_v, '3.13.0') :
    #         query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2014-0038'}) MERGE (kv)-[:OR]->(b) UNION "    
    # query = query[:-7].strip().replace('\n', '')    
    # list_of_queries.append(query)

    # CVE-2017-14489
    query = """
    CREATE (c:CVE {name: 'CVE-2017-14489'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-14489'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.13.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2017-14489'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2017-16939
    query = """
    CREATE (c:CVE {name: 'CVE-2017-16939'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2017-16939'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        vv = int(k_v.replace('.', ''))
        if compare_versions_range('2.6.28', k_v, '3.2.96') or compare_versions_range('3.3.0', k_v, '3.16.51') or compare_versions_range('3.17.0', k_v, '3.18.85') or compare_versions_range('3.19.0', k_v, '4.1.47') or compare_versions_range('4.2.0', k_v, '4.4.103') or compare_versions_range('4.5.0', k_v, '4.9.59') or compare_versions_range('4.10.0', k_v, '4.13.10') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2017-16939'}) MERGE (kv)-[:OR]->(b) UNION "    
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2016-8655
    query = """
    CREATE (c:CVE {name: 'CVE-2016-8655'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-8655'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-8655'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-8655'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-8655'})
    MATCH (cap:Capability {name: 'CAP_NET_RAW'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-8655'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        vv = int(k_v.replace('.', ''))
        if compare_versions_range('3.2.0', k_v, '3.2.84') or compare_versions_range('3.3.0', k_v, '3.10.105') or compare_versions_range('3.11.0', k_v, '3.12.68') or compare_versions_range('3.13.0', k_v, '3.16.39') or compare_versions_range('3.17.0', k_v, '3.18.45') or compare_versions_range('3.19.0', k_v, '4.1.36') or compare_versions_range('4.2.0', k_v, '4.4.37') or compare_versions_range('4.5.0', k_v, '4.8.13') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-8655'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-9793
    query = """
    CREATE (c:CVE {name: 'CVE-2016-9793'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-9793'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-9793'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-9793'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-9793'})
    MATCH (cap:Capability {name: 'CAP_NET_ADMIN'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-9793'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('3.5.0', k_v, '3.12.68') or compare_versions_range('3.13.0', k_v, '3.16.39') or compare_versions_range('3.17.0', k_v, '3.18.51') or compare_versions_range('3.19.0', k_v, '4.1.49') or compare_versions_range('4.2.0', k_v, '4.4.37') or compare_versions_range('4.5.0', k_v, '4.8.13') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-9793'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')
    list_of_queries.append(query)

    # CVE-2016-2384
    query = """
    CREATE (c:CVE {name: 'CVE-2016-2384'})
    CREATE (a:AND_NODE {name: 'AND_NODE', weight: 0, todo: 2, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-2384'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-2384'})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-2384'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MERGE (cc:ContainerConfig {name: 'MntNamespace', type: 'host', tree: 'leaf', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    WITH cc
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-2384'})
    MERGE (cc)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2016-2384'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION   
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.4.8') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-2384'}) MERGE (kv)-[:OR]->(b) UNION "
        else : break    
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2022-0847
    query = """
    CREATE (c:CVE {name: 'CVE-2022-0847'})
    CREATE (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-0847', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    MERGE (b)-[:ROOT]->(c)
    UNION 
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('5.8.0', k_v, '5.10.101') or compare_versions_range('5.15.0', k_v, '5.15.24') or compare_versions_range('5.16.0', k_v, '5.16.10') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-0847'}) MERGE (kv)-[:OR]->(b) UNION "
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # # TOO LONG (> 3 h to be added to Neo4J)
    # CVE-2022-0492
    # query = """
    # CREATE (c:CVE {name: 'CVE-2022-0492'})
    # CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2022-0492'})
    # MERGE (b)-[:ROOT]->(c)
    # UNION
    # """
    # for k_v in reversed(result['kernel_v']) :
    #     if version.Version(k_v) <= version.Version('5.16.20') :
    #         query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-0492'}) MERGE (kv)-[:OR]->(b) UNION "    
    #     else : break
    # query = query[:-7].strip().replace('\n', '')    
    # list_of_queries.append(query)

    # CVE-2022-0185
    query = """
    CREATE (c:CVE {name: 'CVE-2022-0185'})
    CREATE (a:AND_NODE {name: 'AND_NODE', key: 'CVE-2022-0185', weight: 0, todo: 2, needed: [], pred: gds.util.NaN()})
    CREATE (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-0185', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN()})
    CREATE (bb:OR_NODE {name: 'OR_NODE2', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2022-0185'})
    WITH c, a, b, bb
    MERGE (a)-[:ROOT]->(c)
    MERGE (b)-[:AND]->(a)
    MERGE (bb)-[:AND]->(a)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2022-0185'})
    MATCH (p:Permissions:Privileged {name: 'Privileged'})
    MERGE (p)-[:OR]->(bb)
    UNION
    MATCH (bb:OR_NODE {name: 'OR_NODE2', key: 'CVE-2022-0185'})
    MATCH (cap:Capability {name: 'CAP_SYS_ADMIN'})
    MERGE (cap)-[:OR]->(bb)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('5.1.0', k_v, '5.4.173') or compare_versions_range('5.5.0', k_v, '5.10.93') or compare_versions_range('5.11.0', k_v, '5.15.16') or compare_versions_range('5.16.0', k_v, '5.16.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2022-0185'}) MERGE (kv)-[:OR]->(b) UNION " 
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # # TOO LONG (> 3 h to be added to Neo4J)
    # CVE-2020-14386
    # query = """
    # CREATE (c:CVE {name: 'CVE-2020-14386'})
    # CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2020-14386'})
    # MERGE (b)-[:ROOT]->(c)
    # UNION
    # """
    # for k_v in reversed(result['kernel_v']) :
    #     if version.Version(k_v) < version.Version('5.9.0') :
    #         query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2020-14386'}) MERGE (kv)-[:OR]->(b) UNION "    
    #     else : break
    # query = query[:-7].strip().replace('\n', '')    
    # list_of_queries.append(query)

    # # CVE-2015-3214
    # ## ---> No supported kernel version for this CVE ! ###
    # query = """
    # CREATE (c:CVE {name: 'CVE-2015-3214'})
    # CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-3214'})
    # MERGE (b)-[:ROOT]->(c)
    # UNION
    # """
    # for k_v in reversed(result['kernel_v']) :
    #     if version.Version(k_v) <= version.Version('2.6.31') :
    #         query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-3214'}) MERGE (kv)-[:OR]->(b) UNION "    
    #     else : break
    # query = query[:-7].strip().replace('\n', '')    
    # list_of_queries.append(query)

    # CVE-2015-4036
    query = """
    CREATE (c:CVE {name: 'CVE-2015-4036'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-4036'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('3.18.0') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-4036'}) MERGE (kv)-[:OR]->(b) UNION "   
        else : break 
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2016-2383
    query = """
    CREATE (c:CVE {name: 'CVE-2016-2383'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-2383'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) < version.Version('4.5.0') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-2383'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2016-3134
    query = """
    CREATE (c:CVE {name: 'CVE-2016-3134'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-3134'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.5.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-3134'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2016-4998
    query = """
    CREATE (c:CVE {name: 'CVE-2016-4998'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-4998'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.5.5') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-4998'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2015-3290
    query = """
    CREATE (c:CVE {name: 'CVE-2015-3290'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-3290'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.1.5') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-3290'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2015-5157
    query = """
    CREATE (c:CVE {name: 'CVE-2015-5157'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-5157'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.1.5') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-5157'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2015-2925
    query = """
    CREATE (c:CVE {name: 'CVE-2015-2925'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-2925'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.2.3') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-2925'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2015-8543
    query = """
    CREATE (c:CVE {name: 'CVE-2015-8543'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2015-8543'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if version.Version(k_v) <= version.Version('4.3.2') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2015-8543'}) MERGE (kv)-[:OR]->(b) UNION "    
        else : break
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    # CVE-2016-3135
    query = """
    CREATE (c:CVE {name: 'CVE-2016-3135'})
    CREATE (b:OR_NODE {name: 'OR_NODE', weight: -gds.util.infinity(), todo: 1, needed: [], pred: gds.util.NaN(), key: 'CVE-2016-3135'})
    MERGE (b)-[:ROOT]->(c)
    UNION
    """
    for k_v in reversed(result['kernel_v']) :
        if compare_versions_range('4.1.0', k_v, '4.4.21') or compare_versions_range('4.5.0', k_v, '4.6.0') :
            query += "MATCH (kv:KernelVersion {name: '" + k_v + "'}) MATCH (b:OR_NODE {name: 'OR_NODE', key: 'CVE-2016-3135'}) MERGE (kv)-[:OR]->(b) UNION "    
    query = query[:-7].strip().replace('\n', '')    
    list_of_queries.append(query)

    return list_of_queries

