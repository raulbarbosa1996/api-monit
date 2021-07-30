
import requests
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt
import networkx as nx
from flask_restful import Resource
from ModelTopology import topologyInformation
class Topology(Resource):

    def get(self):

        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))

        if(response.ok):
            jData = json.loads(response.content)
            funce = topologyInformation(jData)
            G,color_map,list_hosts=funce.topologyInformation()
            print(G.nodes)
            print(color_map)
            '''
            labels = nx.get_edge_attributes(G,'weight')
            nx.draw(G, with_labels = True,node_color = color_map,font_size=7)
            '''
            pos = nx.spring_layout(G)
            nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),
                                   node_color = color_map, node_size = 500)
            nx.draw_networkx_labels(G, pos)
            nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrows=False)
            l,r = plt.xlim()
            plt.xlim(l-0.1,r+0.1)
            plt.savefig('filename.png', bbox_inches="tight")
            plt.clf()
        else:
            response.raise_for_status()





