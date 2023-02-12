from networkx import Graph, DiGraph
from networkx.exception import NetworkXError

NODE_INDEX = 'index'
EDGE_INDEX = 'index'

class D3Graph(Graph):
    
    listeners = []
    n_index = 0
    e_index = 0
    node_lookup = []
    
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.listeners = []
        self.n_index = 0
        self.e_index = 0
        self.node_lookup = []
        for u in self.nodes():
            self.nodes[u][NODE_INDEX] = self.n_index
            self.node_lookup.append(u)
            self.n_index += 1
        for u,v in self.edges:
            self.edges[u,v][EDGE_INDEX] = self.e_index
            self.e_index += 1
    
    def add_listener(self,L):
        if L not in self.listeners:
            self.listeners.append(L)
        
    def remove_listener(self,L):
        if L in self.listeners:
            self.listeners.remove(L)
    
    def node_by_index(self, nidx):
        return self.node_lookup[nidx]
    
    def node_index(self, n):
        return self.nodes[n][NODE_INDEX]

    def edge_index(self, u, v):
        return self.edges[u,v][EDGE_INDEX]
    
    def edge_indices(self, u, v):
        return self.edge_index(u,v), self.node_index(u), self.node_index(v)
    
    def add_node(self, node_for_adding, **attr):
        # call super, adding in the index value
        attr[NODE_INDEX] = self.n_index
        super().add_node(node_for_adding, **attr)
        self.node_lookup.append(node_for_adding)
               
        for L in self.listeners:
            L.node_added(self.n_index,node_for_adding,attr)
        self.n_index += 1
    
    def add_nodes_from(self, nodes_for_adding, **attr):
        for node_for_adding in nodes_for_adding:
            self.add_node(node_for_adding, **attr)
    
    def remove_node(self, n):
        idx = self.node_index(n)
        for u in list(self.neighbors(n)):
            self.remove_edge(n,u)
        self.node_lookup[idx] = None
        super().remove_node(n)
        
        for L in self.listeners:
            L.node_removed(idx,n)
    
    def remove_nodes_from(self, nodes):
        for n in nodes:
            self.remove_node(n)
    
    def add_edge(self, u_of_edge, v_of_edge, **attr):
        # call super, adding in the index value
        if not self.has_node(u_of_edge):
            self.add_node(u_of_edge)
        if not self.has_node(v_of_edge):
            self.add_node(v_of_edge)
            
        attr[EDGE_INDEX] = self.e_index
        super().add_edge(u_of_edge, v_of_edge, **attr)
                
        uidx = self.node_index(u_of_edge)
        vidx = self.node_index(v_of_edge)
        for L in self.listeners:
            L.edge_added(self.e_index,uidx,vidx,attr)
        self.e_index += 1
        
    def add_edges_from(self, ebunch_to_add, **attr):
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
                attr.update(dd)
            elif ne == 2:
                u, v = e
            else:
                raise NetworkXError(f"Edge tuple {e} must be a 2-tuple or 3-tuple.")
            self.add_edge(u,v,**attr)
        
    def remove_edge(self, u, v):
        eidx,uidx,vidx = self.edge_indices(u,v)
        super().remove_edge(u, v)
        
        for L in self.listeners:
            L.edge_removed(eidx,uidx,vidx)
        
    def remove_edges_from(self, ebunch):
        for e in ebunch:
            self.remove_edge(*e)
        
class D3DiGraph(DiGraph):
    
    listeners = []
    n_index = 0
    e_index = 0
    node_lookup = []
    
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.listeners = []
        self.n_index = 0
        self.e_index = 0
        self.node_lookup = []
        for u in self.nodes():
            self.nodes[u][NODE_INDEX] = self.n_index
            self.node_lookup.append(u)
            self.n_index += 1
        for u,v in self.edges:
            self.edges[u,v][EDGE_INDEX] = self.e_index
            self.e_index += 1
    
    def add_listener(self,L):
        if L not in self.listeners:
            self.listeners.append(L)
        
    def remove_listener(self,L):
        if L in self.listeners:
            self.listeners.remove(L)
    
    def node_by_index(self, nidx):
        return self.node_lookup[nidx]
    
    def node_index(self, n):
        return self.nodes[n][NODE_INDEX]

    def edge_index(self, u, v):
        return self.edges[u,v][EDGE_INDEX]
    
    def edge_indices(self, u, v):
        return self.edge_index(u,v), self.node_index(u), self.node_index(v)
    
    def add_node(self, node_for_adding, **attr):
        # call super, adding in the index value
        attr[NODE_INDEX] = self.n_index
        super().add_node(node_for_adding, **attr)
        self.node_lookup.append(node_for_adding)
               
        for L in self.listeners:
            L.node_added(self.n_index,node_for_adding,attr)
        self.n_index += 1
    
    def add_nodes_from(self, nodes_for_adding, **attr):
        for node_for_adding in nodes_for_adding:
            self.add_node(node_for_adding, **attr)
    
    def remove_node(self, n):
        idx = self.node_index(n)
        for u in list(self.neighbors(n)):
            self.remove_edge(n,u)
        self.node_lookup[idx] = None
        super().remove_node(n)
        
        for L in self.listeners:
            L.node_removed(idx,n)
    
    def remove_nodes_from(self, nodes):
        for n in nodes:
            self.remove_node(n)
    
    def add_edge(self, u_of_edge, v_of_edge, **attr):
        # call super, adding in the index value
        if not self.has_node(u_of_edge):
            self.add_node(u_of_edge)
        if not self.has_node(v_of_edge):
            self.add_node(v_of_edge)
            
        attr[EDGE_INDEX] = self.e_index
        super().add_edge(u_of_edge, v_of_edge, **attr)
                
        uidx = self.node_index(u_of_edge)
        vidx = self.node_index(v_of_edge)
        for L in self.listeners:
            L.edge_added(self.e_index,uidx,vidx,attr)
        self.e_index += 1
        
    def add_edges_from(self, ebunch_to_add, **attr):
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
                attr.update(dd)
            elif ne == 2:
                u, v = e
            else:
                raise NetworkXError(f"Edge tuple {e} must be a 2-tuple or 3-tuple.")
            self.add_edge(u,v,**attr)
        
    def remove_edge(self, u, v):
        eidx,uidx,vidx = self.edge_indices(u,v)
        super().remove_edge(u, v)
        
        for L in self.listeners:
            L.edge_removed(eidx,uidx,vidx)
        
    def remove_edges_from(self, ebunch):
        for e in ebunch:
            self.remove_edge(*e)