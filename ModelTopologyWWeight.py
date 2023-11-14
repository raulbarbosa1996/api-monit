import json
import requests
import networkx as nx

class topologyInformationWWeight():

    def __init__(self,data):
        self.data=data
    def convert_to_hex(rgba_color) :
        red = int(rgba_color[0]*255)
        green = int(rgba_color[1]*255)
        blue = int(rgba_color[2]*255)
        return '#%02x%02x%02x' % (red, green, blue)


    def topologyInformation(self):
        G = nx.Graph()
        color_map = []
        url = "http://127.0.0.1:5000/getAllPortInfo"
        response = requests.get(url)
        if(response.ok):
            jData = json.loads(response.content)
        for i in self.data["network-topology"]["topology"]:
            if "node" in i:
                for j in i["node"]:
                    node_id=j["node-id"].encode('ascii','ignore').decode("utf-8")
                    aux_node_id=node_id.split(':')
                    #print(aux_node_id[0])
                    if(aux_node_id[0]=='host'):
                        continue
                    color_map.append('yellow')
                    id_switch=node_id
                    id_s=''.join(filter(str.isdigit, id_switch))
                    G.add_node(int(id_s))
                    for l in j["termination-point"]:
                        tp_id=l["tp-id"].encode('ascii','ignore').decode("utf-8")
                        aux_tp_id=tp_id.split(':')
                        if(aux_tp_id[2]!="LOCAL" and int(aux_tp_id[2])/100>1):
                            if(aux_tp_id[0]=="host"):
                                id_host=aux_tp_id[-1]
                            else:
                                id_host=aux_tp_id[2]
                            id_h= ''.join(filter(str.isdigit, id_host))
                            G.add_node(int(id_h))
                            throughput=jData[node_id][0][node_id+":"+str(id_h)]["Throughput"]
                            #print(throughput)
                            G.add_edge(int(id_s),int(id_h),weight=throughput)
                            color_map.append('blue')
            if "link" in i:
                for t in i["link"]:
                    try:
                        aux_link_id=t["link-id"].split(':')
                        if(aux_link_id[0]=='host'):
                            #print(aux_link_id[0])
                            continue
                        source=t["source"]
                        try:
                            source_node=source["source-node"]
                            aux_source_node=source_node.split(':')
                            if(aux_source_node[0]=="host"):
                                continue
                                source_node=aux_source_node[-1]
                                switch=jData["openflow:"+source_node][0]
                            else:
                                source_node=aux_source_node[1]
                                switch=jData["openflow:"+source_node][0]
                        except:
                            print("Sem node")
                    except:
                        print("Sem source")
                    try:
                        destination=t["destination"]
                        link_id=t["link-id"]
                        try:
                            dest_node=destination["dest-node"]
                            aux_dest_node=dest_node.split(':')
                            if(aux_dest_node[0]=="host"):
                                dest_node=aux_dest_node[-1]
                            else:
                                dest_node=aux_dest_node[1]
                            id_so=''.join(filter(str.isdigit, source_node))
                            id_d=''.join(filter(str.isdigit, dest_node))
                            aux_link_id=link_id.split(':')
                            throughput=switch["openflow:"+source_node+":"+str(aux_link_id[-1])]["Throughput"]
                            #print(throughput)
                            G.add_edge(int(id_so),int(id_d),weight=throughput)
                        except:
                            print("Sem node")
                    except:
                        print("Sem Destination")
        return G,color_map



