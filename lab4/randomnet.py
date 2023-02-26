import random

from networkx import Graph, DiGraph, NetworkXError

__all__ = ['small_world_graph','local_attachment_graph','erdos_renyi_graph','barabasi_albert_graph','duplication_divergence_graph']

def small_world_graph(n,q,p,graph=None):
    '''
    q must be even
    '''
    if graph is not None and not isinstance(graph,Graph):
        raise NetworkXError('The graph provided must be undirected')
    if graph is not None and len(graph) > 0:
        raise NetworkXError('the graph must be empty, if provided')
       
    if type(q) != int:
        raise NetworkXError('q must be an integer')
    if q % 2 != 0:
        raise NetworkXError('q must be even')
    if p > 1 or p < 0:
        msg = f"NetworkXError p={p} is not in [0,1]."
        raise NetworkXError(msg)
    
    G = graph
    if G is None:
        G = Graph()
        
    for i in range(n):
        G.add_node(i)
        
    # add the regular edges
    for u in range(n):
        for v in range(u+1,int(u+1+q/2)):
            v = v % n
            G.add_edge(u,v)

    # add the random edges
    for u in range(n):
        for v in range(u+1,n):
            if not G.has_edge(u,v):
                if random.random() <= p:
                    G.add_edge(u,v)
    return G

def local_attachment_graph(n, m, r, **kwargs):
    """
    Generate a random graph using the local attachment model.
    
    **Args**:
    
        * ``n`` (int): the number of nodes to add to the graph
        * ``m`` (int): the number of edges a new node will add to the graph
        * ``r`` (int): the number of edges (of the ``m``) that a node will add to uniformly selected random nodes.
          All others will be added to neighbors of the ``r`` selected nodes.
    
    **KwArgs**:
        * ``seed [=-1]`` (int): a seed for the random number generator
        * ``graph [=None]`` (:py:class:`networkx.DiGraph`): the graph that will be populated.  If the graph is ``None``, 
          then a new graph will be created.
    
    **Returns**:
        :py:class:`networkx.DiGraph`. The graph generated.
    
    .. note::
        Source: M. O. Jackson and B. O. Rogers "Meeting strangers and friends of friends: How random are social networks?" The American Economic Review, 2007.
    """
    seed = kwargs.pop('seed',None)
    graph = kwargs.pop('graph',None)
    
    if graph is not None and not isinstance(graph,DiGraph):
        raise NetworkXError('The graph provided must be directed')
    if graph is not None and len(graph) > 0:
        raise NetworkXError('the graph must be empty, if provided')
    
    if len(kwargs) > 0:
        raise NetworkXError('Unknown arguments: %s' % ', '.join(kwargs.keys()))
    
    if type(r) != int:
        raise NetworkXError('r must be an integer')
    elif r < 1:
        raise NetworkXError('r must be 1 or larger')
        
    if seed is None:
        seed = -1
    
    if seed >= 0:
        random.seed(seed)
        
    #####
    # build the initial graph
    
    G = graph
    if G is None:
        G = DiGraph()
    
    # populate with nodes
    for i in range(m+1):
        G.add_node(i)
        
    # according to Jackson's paper, all initial nodes have m neighbors.
    for i in range(m+1):
        for j in range(m+1):
            if j != i:
                G.add_edge(j,i)
            
    ######
    # Build the rest of the graph
    node_list = list(range(m+1))
    for i in range(m+1,n):
        G.add_node(i)
        
        # pick random neighbors (the parents)
        parents = random.sample(node_list,r)
        
        # pick neighbors from the parents' neighborhoods
        potentials = set()
        for n in parents:
            potentials.update(set(G.successors(n)))
            
        potentials.difference_update(parents)
        nsize = min([m-r,len(potentials)])
        neighbors = random.sample(potentials,nsize)
        
        # connect
        for v in (parents + neighbors):
            G.add_edge(i,v)
            
        node_list.append(i)
            
    # done
    return G

def barabasi_albert_graph(n, m, **kwargs):
    """
    Generate a random graph using the Barabasi-Albert preferential attachment model.
    
    **Args**:
    
        * ``n`` (int): the number of nodes to add to the graph
        * ``m`` (int): the number of edges a new node will add to the graph
    
    **KwArgs**:
        * ``directed [=False]`` (boolean): whether to build the graph directed.  If ``True``, then the ``m`` edges created
          by a node upon its creation are instantiated as out-edges.  All others are in-edges to that node.
        * ``seed [=-1]`` (int): a seed for the random number generator
        * ``graph [=None]`` (:py:class:`networkx.Graph` or :py:class:`networkx.DiGraph`): this is the actual graph instance to populate. It must be
          empty and its directionality must agree with the value of ``directed``.
    
    **Returns**:
        :py:class:`networkx.Graph` or :py:class:`networkx.DiGraph`. The graph generated.  If ``directed = True``, then a :py:class:`networkx.DiGraph` will be returned.
    
    .. note::
        Source: A. L. Barabasi and R. Albert "Emergence of scaling in random networks", Science 286, pp 509-512, 1999.
    """
    seed = kwargs.pop('seed',None)
    directed = kwargs.pop('directed',False)
    graph = kwargs.pop('graph',None)
    
    if graph is not None:
        if len(graph) > 0:
            raise NetworkXError('the graph must be empty, if provided')
        if type(graph)==DiGraph != directed:
            raise NetworkXError('graph and directed arguments must agree')
    else:
        if directed:
            graph = DiGraph()
        else:
            graph = Graph()
    
    if len(kwargs) > 0:
        raise NetworkXError('Unknown arguments: %s' % ', '.join(kwargs.keys()))
        
    if seed is None:
        seed = -1
    
    if not directed:
        return __inner_barabasi_albert_udir(n, m, seed, graph)
    else:
        return __inner_barabasi_albert_dir(n, m, seed, graph)
       
def __inner_barabasi_albert_udir(n, m, seed, G):
    # add nodes
    G.add_nodes_from(range(m))
    
    #####
    # add edges
    if seed >= 0:
        random.seed(seed)
    
    # add the first (m+1)th node
    G.add_node(m)
    for i in range(m):
        G.add_edge(m,i)
    
    # add the remaining nodes
    num_endpoints = 2 * m
    for new_node_idx in range(m+1,n):
        G.add_node(new_node_idx)
        
        # this node drops m edges
        delta_endpoints = 0
        for e in range(m):
            rnd = random.random() * (num_endpoints-delta_endpoints)
            
            # now loop through nodes and find the one whose endpoint has the running sum
            # note that we ignore nodes that we already have a connection to
            running_sum = 0
            for i in range(new_node_idx):
                if G.has_edge(new_node_idx,i):
                    continue
                    
                running_sum += G.degree(i)
                if running_sum > rnd:
                    G.add_edge(new_node_idx,i)
                    
                    # this node can no longer be selected.  So we remove this node's degree
                    # from the total degree of the network - making sure that a node will get
                    # selected next time.  We decrease by 1 because the node's degree has just
                    # been updated by 1 because it gained an endpoint from the node being
                    # added.  This edge isn't included in the number of endpoints until the 
                    # node has finished being added (since the node can't connect to itself).
                    # As a result the delta endpoints must not include this edge either.
                    delta_endpoints += G.degree(i) - 1
                    break
                    
        num_endpoints += m * 2
        
    return G

def __inner_barabasi_albert_dir(n, m, seed, G):
    # add nodes
    G.add_nodes_from(range(m))

    #####
    # add edges
    if seed >= 0:
        random.seed(seed)

    # add the first (m+1)th node
    G.add_node(m)
    for i in range(m):
        G.add_edge(m,i)

    # add the remaining nodes
    num_endpoints = 2 * m
    for new_node_idx in range(m+1,n):
        G.add_node(new_node_idx)
        
        # this node drops m edges
        delta_endpoints = 0
        for e in range(m):
            rnd = random.random() * (num_endpoints-delta_endpoints)

            # now loop through nodes and find the one whose endpoint has the running sum
            # note that we ignore nodes that we already have a connection to
            running_sum = 0
            for i in range(new_node_idx):
                if G.has_edge(new_node_idx,i):
                    continue

                node_degree = G.in_degree(i) + G.out_degree(i)
                running_sum += node_degree
                if running_sum > rnd:
                    G.add_edge(new_node_idx,i)
                    
                    # this node can no longer be selected.  So we remove this node's degree
                    # from the total degree of the network - making sure that a node will get
                    # selected next time.
                    delta_endpoints += node_degree
                    break

        num_endpoints += m * 2
        
    return G

def erdos_renyi_graph(n, p, **kwargs):
    """
    Generate an Erdos-Renyi graph.
    
    **Args**:
         * ``num_nodes`` (int): the number of nodes to populate the graph with.
         * ``p`` (0 <= float <= 1): the probability p given to each edge's existence.
    
    **KwArgs**:
        * ``directed [=False]`` (boolean): indicates whether the network generated is directed.
        * ``self_loops [=False]`` (boolean): indicates whether self-loops are permitted in the generated graph.
        * ``seed [=-1]`` (int): the seed provided to the random generator used to drive the graph construction.
        * ``graph [=None]`` (:py:class:`zen.Graph` or :py:class:`zen.DiGraph`): this is the actual graph instance to populate. It must be
          empty and its directionality must agree with the value of ``directed``.
    """
    directed = kwargs.pop('directed',False)
    self_loops = kwargs.pop('self_loops',False)
    seed = kwargs.pop('seed',None)
    graph = kwargs.pop('graph',None)
    
    if graph is not None:
        if len(graph) > 0:
            raise NetworkXError('the graph must be empty, if provided')
        if isinstance(graph,DiGraph) != directed:
            raise NetworkXError('graph and directed arguments must agree')
    else:
        if directed:
            graph = DiGraph()
        else:
            graph = Graph()
    if p > 1 or p < 0:
        msg = f"NetworkXError p={p} is not in [0,1]."
        raise NetworkXError(msg)
            
    if len(kwargs) > 0:
        raise NetworkXError('Unknown arguments: %s' % ', '.join(kwargs.keys()))
        
    if seed is None:
        seed = -1
    
    if directed:
        return __erdos_renyi_directed(n,p,self_loops,seed,graph)
    else:
        return __erdos_renyi_undirected(n,p,self_loops,seed,graph)

def __erdos_renyi_undirected(num_nodes, p, self_loops, seed, G):
    if seed >= 0:
        random.seed(seed)
    
    # add nodes
    for i in range(num_nodes):
        G.add_node(i)
        
    # add edges
    for i in range(num_nodes):
        if self_loops:
            first_j = i
        else:
            first_j = i+1
            
        for j in range(first_j,num_nodes):
            rnd = random.random()
            if rnd < p:
                G.add_edge(i,j)
    
    return G
    
def __erdos_renyi_directed(num_nodes, p, self_loops, seed, G):
    if seed >= 0:
        random.seed(seed)
    
    # add nodes
    for i in range(num_nodes):
        G.add_node(i)
    
    # add edges
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i == j and not self_loops:
                continue
                
            rnd = random.random()
            if rnd < p:
                G.add_edge(i,j)

    return G

def duplication_divergence_graph(n, p, seed=None, graph=None):
    """Returns an undirected graph using the duplication-divergence model.

    A graph of `n` nodes is created by duplicating the initial nodes
    and retaining edges incident to the original nodes with a retention
    probability `p`.

    Parameters
    ----------
    n : int
        The desired number of nodes in the graph.
    p : float
        The probability for retaining the edge of the replicated node.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    G : Graph

    Raises
    ------
    NetworkXError
        If `p` is not a valid probability.
        If `n` is less than 2.

    Notes
    -----
    This algorithm appears in [1].

    This implementation disallows the possibility of generating
    disconnected graphs.

    References
    ----------
    .. [1] I. Ispolatov, P. L. Krapivsky, A. Yuryev,
       "Duplication-divergence model of protein interaction network",
       Phys. Rev. E, 71, 061911, 2005.

    """
    if p > 1 or p < 0:
        msg = f"NetworkXError p={p} is not in [0,1]."
        raise NetworkXError(msg)
    if n < 2:
        msg = "n must be greater than or equal to 2"
        raise NetworkXError(msg)

    G = graph
    if G is None:
        G = Graph()

    if seed is None:
        seed = -1
    if seed >= 0:
        random.seed(seed)
        
    # Initialize the graph with two connected nodes.
    G.add_edge(0, 1)
    i = 2
    while i < n:
        # Choose a random node from current graph to duplicate.
        random_node = random.choice(list(G))
        # flag indicates whether at least one edge is connected on the replica.
        flag = False
        nbrs = []
        for nbr in G.neighbors(random_node):
            if random.random() < p:
                # Link retention step.
                nbrs.append(nbr)
                flag = True
                
        # Successful duplication.
        if flag: 
            G.add_node(i)
            for nbr in nbrs:
                G.add_edge(i,nbr)
            i += 1
           
    return G