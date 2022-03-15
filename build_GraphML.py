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
        ('i', { 'labels': 'i:Image', 'name': 'Image', \
            'img_id': img.img_id, \
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
        ('i','df','dir',{'label':'BUILT_FROM'})
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


def image_GraphML_chart(img, infra) :
    """
    TODO
    """

    G = create_img_graph(img, infra)
    save_graph(G, img.img_id)

