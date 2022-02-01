import networkx as nx


def create_img_graph(img, infra) :
    """ 
    Description

    Parameters
    ---------
    name: type
        Description

    Returns
    -------
    type:
        Description
    """

    # Create a new Graph
    G=nx.MultiDiGraph()

    # Add all nodes for one container
    G.add_nodes_from([
        ('c', { 'labels': 'c:Container', 'name': 'Container', \
            'id':'', \
            'start_t':'', \
            'stop_t':'', \
            'status':''}),
        ('cc', { 'labels': 'cc:ContainerConfig', 'name': 'ContainerConfig'}),
        ('i', { 'labels': 'i:Image', 'name': 'Image', \
            'id': img.img_id, \
            'repo': img.repo, \
            'tag': img.tag, \
            't_created': img.t_created, \
            'size': img.img_size}),
        ('df', { 'labels': 'df:Dockerfile', 'name': 'Dockerfile', \
            'base_image': 'ubuntu', \
            'user': 'root', \
            'env': 'n/a', \
            'volume': 'n/a', \
            'net_adapter': 'bridge', \
            'net_ports': 'n/a', \
            'entrypoint': 'n/a', \
            'cmd': 'sh'}), 
        ('p', { 'labels': 'p:Permissions', 'name': 'Permissions', \
            'profile': 'docker-default', \
            'CAPs': 'AUDIT_WRITE, CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL, MKNOD, NET_BIND_SERVICE, NET_RAW, SETFCAP, SETGID, SETPCAP, SETUID, SYS_CHROOT', \
            'syscalls': 'accept, access, bind, capget, chmod, chown, close, connect, creat, execve, exit, fork, ioctl, kill, mkdir, open, read, rename, send, socket, time, uname, write'}),
        ('h', { 'labels': 'h:Host', 'name': 'Host', \
            'hostname': infra.host.hostname, \
            'os': infra.host.os, \
            'kernel': infra.host.kernel_v, \
            'cpus': infra.host.cpus, \
            'mem': infra.host.mem}),
        ('ce', { 'labels': 'de:DockerEngine', 'name': 'DockerEngine', \
            'docker_v': infra.docker_v, \
            'containerd_v': infra.containerd_v, \
            'runc_v': infra.runc_v, \
            'storage': infra.storage, \
            'registry': infra.registry}),
    ])

    # Add relationships
    G.add_edges_from([
        ('ce','h','dir',{'label':'RUNS_ON_TOP'}),
        ('ce','i','dir',{'label':'MANAGES'}),
        ('i','df','dir',{'label':'BUILT_FROM'}),
        ('ce','c','dir',{'label':'RUNS'}),
        ('c','i','dir',{'label':'INSTANCIATE'}),
        ('c','cc','dir',{'label':'HAS'}),
        ('c','p','dir',{'label':'CAN'}),
        ])

    return G


def save_graph(G, img_id) :
    """ 
    Save the NetworkX graph to GraphML format.

    Parameters
    ---------
    G: Networkx Graph
        Description

    Output
    -------
    Writes on disk the GraphML XML file corresponding to the graph.
    """

    graph_name = "charts/" + str(img_id) + "_chart.graphml"
    nx.write_graphml(G, graph_name, named_key_ids=True)


def generate_GraphML_chart(img, infra) :
    """
    TODO
    """

    G = create_img_graph(img, infra)
    save_graph(G, img.img_id)

