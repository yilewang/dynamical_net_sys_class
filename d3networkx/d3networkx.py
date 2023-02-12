from json import dumps
from time import sleep
from webbrowser import open_new
from os import getcwd, remove
from os.path import join as pathjoin
from sys import path as pythonpath
from random import randint
from datetime import timedelta

from networkx import Graph
from networkx import DiGraph
from d3graph import NODE_INDEX, EDGE_INDEX

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.httputil
import socket
import asyncio

__all__ = ["create_d3nx_visualizer","D3NetworkxRenderer"]

visualizer_clients = []
websocket_clients = []
messages_todo = []

class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.set_nodelay(True)
        if self not in websocket_clients:
            websocket_clients.append(self)
        #print('new connection @ '+str(self))

    def on_message(self, message):
        #print('message received @ %s:  %s' % (str(self),message))
        if message == 'visualizer':
            visualizer_clients.append(self)
            print('visualizer connected...',end='')
        elif message == 'python':
            print('networkx connected...',end='')
        else:
            self.send_to_visualizers(message)
            #self.write_message('1')

    def send_to_visualizers(self, message):
        for c in visualizer_clients:
            c.write_message(message)

    def on_close(self):
        if self in websocket_clients:
            websocket_clients.remove(self)
        if self in visualizer_clients:
            visualizer_clients.remove(self)
        #print('connection closed @ '+str(self))

    def check_origin(self, origin):
        return True


_STYLE_SHAPE = 'shape'
_STYLE_SIZE = 'size'
_STYLE_FILL = 'fill'
_STYLE_STROKE = 'stroke'
_STYLE_STROKE_WIDTH = 'strokewidth'

def node_style(shape=None, size=None, fill=None, stroke=None, stroke_width=None):
    style = {_STYLE_SHAPE:"circle",_STYLE_SIZE:8,_STYLE_FILL:'#77BEF5',_STYLE_STROKE:'#FFFFFF',_STYLE_STROKE_WIDTH:2}
    if shape:
        style[_STYLE_SHAPE] = shape
    if size:
        style[_STYLE_SIZE] = size
    if fill:
        style[_STYLE_FILL] = fill
    if stroke:
        style[_STYLE_STROKE] = stroke
    if stroke_width:
        style[_STYLE_STROKE_WIDTH] = stroke_width
    return style

def edge_style(stroke=None, stroke_width=None):
    style = {_STYLE_STROKE:'#494949',_STYLE_STROKE_WIDTH:2}
    if stroke:
        style[_STYLE_STROKE] = stroke
    if stroke_width:
        style[_STYLE_STROKE_WIDTH] = stroke_width
    return style


async def create_d3nx_visualizer(event_delay=0.03,interactive=True,
                canvas_size=(800,600),autolaunch=True,port=None,
                node_dstyle=None,edge_dstyle=None,node_hstyle=None,edge_hstyle=None):

    if port is None:
        port = 5000 + randint(1,4999)

    if autolaunch:
        nxdir = ''
        for d in pythonpath:  # look for the d3networkx folder in the python path
            if 'd3networkx' in d:
                nxdir = d
                break
        if nxdir == getcwd():  # if running the program from the same folder as the d3networkx folder
            nxdir = ''
        #print('launching visualizer!')
        p = pathjoin('file://'+getcwd(),nxdir,"visualizer.html?width=%i&height=%i&port=%i" % (canvas_size[0],canvas_size[1],port) )
        p = p.replace('\\','/')
        tmpname = 'tmp%i.html' % randint(1,9999)
        with open(tmpname,'w') as f:
            f. write('<meta http-equiv="refresh" content="0; URL=%s" />' % p)

        open_new(tmpname)

    d3 = D3NetworkxRenderer(event_delay=event_delay,interactive=interactive,port=port,
                node_dstyle=node_dstyle,edge_dstyle=edge_dstyle,node_hstyle=node_hstyle,edge_hstyle=edge_hstyle)


    await d3.start_client()
    d3.client.write_message('python')
    d3.start_client_polling()

    if autolaunch:
        remove(tmpname)

    return d3

class D3NetworkxRenderer(object):

    MAGICKEY = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self,event_delay=0.03,interactive=True,port=9876,
                node_dstyle=None,edge_dstyle=None,node_hstyle=None,edge_hstyle=None):

        self.event_delay = event_delay
        self.port = port
        self.server = None
        self.client = None
        self.interactive = interactive

        self.default_node_style = node_dstyle
        self.default_edge_style = edge_dstyle
        self.highlighted_node_style = node_hstyle
        self.highlighted_edge_style = edge_hstyle
        if not self.default_node_style:
            self.default_node_style = node_style()
        if not self.default_edge_style:
            self.default_edge_style = edge_style()
        if not self.highlighted_node_style:
            self.highlighted_node_style = node_style(size=10,fill='#FD5411')
        if not self.highlighted_edge_style:
            self.highlighted_edge_style = edge_style(stroke='#F79C00',stroke_width=4)
        self._highlighted_nodes = set([])
        self._highlighted_edges = set([])

        self.updates_todo = []

        self.start_server()

    def set_graph(self,graph):
        self.clear()
        if graph is None:
            return
        self._graph = graph
        self._directed = isinstance(graph,DiGraph)
        self._graph.add_listener(self)

        # Add nodes and edges if graph already has them
        if self._graph.number_of_nodes() > 0:
            for n in self._graph.nodes():
                self.node_added(self._graph.node_index(n),n,self._graph.nodes[n])
            for u,v in self._graph.edges():
                self.edge_added(*self._graph.edge_indices(u,v),self._graph[u][v])

    def set_title(self,newtitle):
        ti = {'titlename':newtitle}
        self._send_update('ti'+dumps(ti))
        self.update()

    def clear(self):
        self.clear_highlights()
        self._graph = None
        self._send_update('cc')
        self.update()

    def update(self):
        self._send_update('up')

    def set_event_delay(self,delay):
        self.event_delay = delay

    def set_interactive(self,interactive):
        self.interactive = interactive

    # Setting the position of nodes
    def position_node(self,n,x,y):
        mv_node = {'nid':self._graph.node_index(n), 'fixed':True, 'cx':x, 'cy':y}
        self._send_update('mn'+dumps(mv_node))

    # data is a list of tuples with form (node_object, x, y)
    def position_nodes(self,data):
        for n,x,y in data:
            self.position_node(n,x,y)

    # Adding style to nodes
    def stylize_node(self,n,style_dict):
        self._send_update('!n'+ self._node_update(self._graph.node_index(n),n,style_dict) )

    def stylize_nodes(self,nodes,style_dict):
        for n in nodes:
            self.stylize_node(n,style_dict)

    # Adding style to edges
    def stylize_edge(self,u,v,style_dict):
        self._send_update('!e'+ self._edge_update(*self._graph.edge_indices(u,v),style_dict) )

    def stylize_edges(self,ebunch,style_dict):
        for e in ebunch:
            self.stylize_edge(*e,style_dict)

    # Automatically called, do not call directly
    def node_added(self,nidx,n,data):
        self._send_update('+n'+ self._node_update(nidx,n) )

    # Automatically called, do not call directly
    def node_removed(self,nidx,n):
        rm_node = {'nid': nidx}
        self._send_update('-n'+dumps(rm_node))

    # Automatically called, do not call directly
    def edge_added(self,eidx,uidx,vidx,data):
        self._send_update('+e'+ self._edge_update(eidx,uidx,vidx) )

    # Automatically called, do not call directly
    def edge_removed(self,eidx,uidx,vidx):
        rm_edge = {'eid': eidx}
        self._send_update('-e'+dumps(rm_edge))

    # Highlighting Nodes
    def highlight_nodes(self,nodes):
        self.stylize_nodes(nodes,self.highlighted_node_style)
        self._highlighted_nodes.update(set(nodes))

    def highlight_nodes_by_index(self,nidxs):
        self.highlight_nodes([self._graph.node_by_index(nidx) for nidx in nidxs])

    def highlight_edges(self,edges):
        self.stylize_edges(edges,self.highlighted_edge_style)
        self._highlighted_edges.update(set(edges))

    def clear_highlights(self):
        self.stylize_nodes(self._highlighted_nodes,self.default_node_style)
        self.stylize_edges(self._highlighted_edges,self.default_edge_style)
        self._highlighted_nodes = set([])
        self._highlighted_edges = set([])

    # Helper functions for sending updates
    def _node_update(self,nidx,nobj,style_dict={}):
        update_node = {'nid': nidx}
        update_node['ntitle'] = ''
        if nobj is not None:
            update_node['ntitle'] = str( nobj )
        final_style = self.default_node_style.copy()
        final_style.update(style_dict)
        update_node.update(final_style)
        return dumps(update_node)

    def _edge_update(self,eidx,uidx,vidx,style_dict={}):
        update_edge = {'source':uidx, 'target':vidx}
        update_edge['eid'] = eidx
        update_edge['directed'] = int(self._directed)
        final_style = self.default_edge_style.copy()
        final_style.update(style_dict)
        update_edge.update(final_style)
        return dumps(update_edge)

    def _send_update(self,update=None):
        if update is not None:
            self.updates_todo.append(update)
            #print('Appended to the todo: '+update)
            if self.interactive:
                self.updates_todo.append('up')

    def _write_update(self):
        if self.client is None or asyncio.isfuture(self.client):
            print('NetworkX client is still loading.')
            return

        while len(self.updates_todo) > 0:
            update = self.updates_todo.pop(0)
            self.client.write_message(update)
            #print('Client Wrote: '+update)
            if update == 'up':
                break
        tornado.ioloop.IOLoop.current().add_timeout(timedelta(milliseconds=int(self.event_delay*1000)), self._write_update)

                #msg = yield self.client.read_message()
                #print('got back after up: '+msg)
                #sleep(self.event_delay)
                #asyncio.sleep(self.event_delay)

    def start_server(self):
        application = tornado.web.Application([(r'/ws', WSHandler),(r'/', WSHandler)])
        self.server = tornado.httpserver.HTTPServer(application)
        self.server.listen(self.port,'127.0.0.1')
        myIP = socket.gethostbyname(socket.gethostname())
        print('websocket server started...', end='') #' at %s***' % myIP)

    def stop_server(self):
        self.server.close()

    async def start_client(self):
        self.client = await tornado.websocket.websocket_connect('ws://localhost:%i/ws' % self.port)

    def start_client_polling(self):
        tornado.ioloop.IOLoop.current().add_timeout(timedelta(milliseconds=int(self.event_delay*1000)), self._write_update)
