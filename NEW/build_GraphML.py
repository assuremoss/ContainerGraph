import networkx as nx


def create_graph() :
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
        ('c',{'labels':':Container:Docker', \
            'id':'', \
            'name':'', \
            'start_t':'', \
            'stop_t':'', \
            'status':''}),
        ('cc',{'labels':':ContainerConfig', \
            'user':'', \
            'env':'', \
            'volume':'', \
            'net_adapter':'', \
            'net_ports':'', \
            'entrypoint':'', \
            'cmd':''}),
        ('i',{'labels':':Image', \
            'id':'', \
            'repo':'', \
            'tag':'', \
            't_created':'', \
            'size':'', \
            'base_img':''}),
        ('p',{'labels':':Permissions', \
            'profile':'', \
            'files':'', \
            'network':'', \
            'processes':'', \
            'adminop':''}),
        ('h',{'labels':':Infrastructure:Host', \
            'hostname':'', \
            'docker_v':'', \
            'containerd_v':'', \
            'runc_v':'', \
            'os':'', \
            '':'', \
            '':'', \
            'mem':'', \
            'registry':''}),
    ])

    # Add relationships
    G.add_edges_from([
        ('c','cc','dir',{'label':'HAS'}),
        ('c','i','dir',{'label':'INSTANCIATE'}),
        ('c','p','dir',{'label':'CAN'}),
        ('c','h','dir',{'label':'RUNS_ON_TOP'})
        ])

    return G


def save_graph(G) :
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
    nx.write_graphml(G, "charts/img_id_chart.graphml")


# NetworkX Documentation
#
# https://networkx.org/documentation/networkx-1.10/tutorial/tutorial.html


G = create_graph()
save_graph(G)

