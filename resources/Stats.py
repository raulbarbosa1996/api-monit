import networkx as nx
from flask_restful import Resource
import requests
from mycroft_bus_client import MessageBusClient, Message
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt
from Functions.Insert import Insert
from types import SimpleNamespace

from Functions.GetDataForPath import GetDataForPath

from ModelTopologyWWeight import topologyInformationWWeight
from ModelTopology import topologyInformation
from flask import  jsonify, request, make_response
import  time

class Stats(Resource):

    def get(self):
        global switch_info
        #starttime = time.time()
        #while True:
        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
        res = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
        if(res.ok):
            jData = json.loads(res.content)
            #Chamar função com pesos para obter o caminho mais curto
            funce = topologyInformationWWeight(jData)
            G,color_map=funce.topologyInformation()
            #G[196039699939907][187769002179392]['weight']=2000
            pos = nx.spring_layout(G)  # positions for all nodes
            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
            path = nx.shortest_path(G,source=103,target=107,weight='weight')
            labels = {e: G.edges[e]['weight'] for e in G.edges}
            print(labels)
            print(path)
            plt.clf()
            path_edges = zip(path,path[1:])
            path_edges = set(path_edges)
            #Chamar função sem peso para criar imagem interpretável
            funce = topologyInformation(jData)
            G_w_weight,color_map_w_weight,list_hosts=funce.topologyInformation()
            pos_w_weight = nx.spring_layout(G_w_weight)
            nx.draw(G_w_weight, with_labels = True,pos=pos_w_weight,node_color = color_map_w_weight,font_size=7)
            nx.draw_networkx_edges(G_w_weight,pos_w_weight,edgelist=path_edges,edge_color='r',width=5)
            nx.draw_networkx_nodes(G_w_weight,pos_w_weight,nodelist=path,node_color='r')
            l,r = plt.xlim()
            plt.xlim(l-1,r+1)
            plt.savefig('tss.png', bbox_inches="tight")
            plt.clf()

            blah_b=nx.all_pairs_dijkstra_path(G)
            shortest_paths = dict(blah_b)
            #print(shortest_paths)

            nodes=list(G.nodes)

            lista_hosts=[]
            for i in range(0,len(nodes)):
                if (color_map[i]=='blue'):
                    lista_hosts.append(nodes[i])
            print(G.nodes)
            print(color_map)


            #Obter informação switchs
            url = "http://127.0.0.1:5000/infoSW"
            res = requests.get(url)
            if(res.ok):
                switch_info = json.loads(res.content)
                print(switch_info)

            #Obter current_id para apagar flows
            url = "http://127.0.0.1:5000/currentId"
            res = requests.get(url)
            if(res.ok):
                print("aQui")
                current_id = json.loads(res.content)
                for key in switch_info:
                    for i in range(1000,int(current_id)):
                        #Delete Flow id
                        url = "http://127.0.0.1:5000/deleteFlow_withID"
                        data={"Switch":str(switch_info[key]), "Flow_id":str(i)}
                        print(data)
                        res_ = requests.delete(url, json=data)
                        if res_.ok:
                            print("Done")

            for i in range(0,len(lista_hosts)):
                for j in range(0,len(lista_hosts)):
                    if(len(shortest_paths.get(lista_hosts[i])[lista_hosts[j]])>1):
                        caminho=shortest_paths.get(lista_hosts[i])[lista_hosts[j]]
                        ip_src=caminho[0]-100
                        ip_dst=caminho[-1]-100
                        #print(caminho)
                        #print("\n")
                        if(len(caminho)==3):
                            #Insert new Flow
                            url = "http://127.0.0.1:5000/addFlowIP"
                            data={"Switch":"openflow:"+str(caminho[1]),"in-port":str(caminho[0]), "out-port":str(caminho[-1]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                        elif(len(caminho)==4):
                            print((shortest_paths.get(lista_hosts[0]))[107])
                            switch_name_src=switch_info[str(caminho[1])]
                            switch_name_src=switch_name_src.split("b")[1]
                            switch_name_dst=switch_info[str(caminho[2])]
                            switch_name_dst=switch_name_dst.split("b")[1]
                            #Insert new Flow
                            url = "http://127.0.0.1:5000/addFlowIP"
                            data={"Switch":"openflow:"+str(caminho[1]),"in-port":str(caminho[0]), "out-port":str(switch_name_src)+str(switch_name_dst), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                            data={"Switch":"openflow:"+str(caminho[2]),"in-port":str(switch_name_dst)+str(switch_name_src), "out-port":str(caminho[3]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                        else:
                            print((shortest_paths.get(lista_hosts[0]))[107])
                            switch_name_src=switch_info[str(caminho[1])]
                            switch_name_src=switch_name_src.split("b")[1]
                            switch_name_dst=switch_info[str(caminho[3])]
                            switch_name_dst=switch_name_dst.split("b")[1]
                            switch_name_mdl=switch_info[str(caminho[2])]
                            switch_name_mdl=switch_name_mdl.split("b")[1]
                            #Insert new Flow
                            url = "http://127.0.0.1:5000/addFlowIP"
                            data={"Switch":"openflow:"+str(caminho[1]),"in-port":str(caminho[0]), "out-port":str(switch_name_src)+str(switch_name_mdl), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                            data={"Switch":"openflow:"+str(caminho[2]),"in-port":str(switch_name_mdl)+str(switch_name_src), "out-port":str(switch_name_mdl)+str(switch_name_dst), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                            data={"Switch":"openflow:"+str(caminho[3]),"in-port":str(switch_name_dst)+str(switch_name_mdl), "out-port":str(caminho[4]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")






                        #curl --header "Content-Type: application/json" --request POST --data '{"Switch":"openflow:196100289772364","in-port":"101", "out-port":"12", "ipv4-src":"192.168.2.158", "ipv4-dst":"192.168.2.2", "tcp_src":"5100", "tcp_dst":"5200"}' http://127.0.0.1:5000/addFlowTCP



            #Calcular Dijkstra para todos os nodes

            #Guarda o custo do Node x para y
            #blah=nx.all_pairs_dijkstra_path_length(G)

            #Guarda o melhor caminho do Node X para o Node Y- neste caso para todos
            #blah_b=nx.all_pairs_dijkstra_path(G)

            #shortest_paths = dict(blah_b)
            #print(shortest_paths)

            #path = nx.all_pairs_shortest_path(G)
            #print(dict(path))


                #time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    def post(self):
        data = request.json
        intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        #Obter Source e Target
        '''
        data_getData=GetDataForPath(data)
        source,target=data_getData.getData()
        print(source)
        print(target)'''

        starttime = time.time()
        conta=0
        while True:

            '''
            url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
            res = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
            if(res.ok):
                jData = json.loads(res.content)
                #Chamar função com pesos para obter o caminho mais curto
                funce = topologyInformationWWeight(jData)
                G,color_map=funce.topologyInformation()
                pos = nx.spring_layout(G)  # positions for all nodes
                nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
    
                path = nx.shortest_path(G,source=int(source),target=int(target),weight='weight')
                print(path)
                plt.clf()
                path_edges = zip(path,path[1:])
                path_edges = set(path_edges)
    
                #Chamar função sem peso para criar imagem interpretável
                funce = topologyInformation(jData)
                G_w_weight,color_map_w_weight=funce.topologyInformation()
                pos_w_weight = nx.spring_layout(G_w_weight)
                nx.draw(G_w_weight, with_labels = True,pos=pos_w_weight,node_color = color_map_w_weight,font_size=7)
                nx.draw_networkx_edges(G_w_weight,pos_w_weight,edgelist=path_edges,edge_color='r',width=5)
                nx.draw_networkx_nodes(G_w_weight,pos_w_weight,nodelist=path,node_color='r')
                l,r = plt.xlim()
                plt.xlim(l-1,r+1)
                plt.savefig('tss.png', bbox_inches="tight")
                plt.clf()
                '''
            #Depois de conectar, otimizar
            url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
            res = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
            if(res.ok):
                jData = json.loads(res.content)
                #Chamar função com pesos para obter o caminho mais curto
                funce = topologyInformationWWeight(jData)
                G,color_map=funce.topologyInformation()
                pos = nx.spring_layout(G)  #positions for all nodes
                nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
                blah_b=nx.all_pairs_dijkstra_path(G)
                shortest_paths = dict(blah_b)
                print(shortest_paths)

            nodes=list(G.nodes)

            lista_hosts=[]
            for i in range(0,len(nodes)):
                if (color_map[i]=='blue'):
                    lista_hosts.append(nodes[i])
            print(G.nodes)
            print(color_map)

            #Obter informação switchs
            url = "http://127.0.0.1:5000/infoSW"
            res = requests.get(url)
            if(res.ok):
                switch_info = json.loads(res.content)
                print(switch_info)

            #Obter current_id para apagar flows
            url = "http://127.0.0.1:5000/currentId"
            res = requests.get(url)
            if(res.ok):
                print("aQui")
                current_id = json.loads(res.content)
                for key in switch_info:
                    for i in range(1000,int(current_id)):
                        #Delete Flow id
                        url = "http://127.0.0.1:5000/deleteFlow_withID"
                        data={"Switch":str(switch_info[key]), "Flow_id":str(i)}
                        print(data)
                        res_ = requests.delete(url, json=data)
                        if res_.ok:
                            print("Done")

            #Inserir novos flows
            for i in range(0,len(lista_hosts)):
                for j in range(0,len(lista_hosts)):
                    if(len(shortest_paths.get(lista_hosts[i])[lista_hosts[j]])>1):
                        caminho=shortest_paths.get(lista_hosts[i])[lista_hosts[j]]
                        ip_src=caminho[0]-100
                        ip_dst=caminho[-1]-100
                        #print(caminho)
                        #print("\n")
                        if(len(caminho)==3):
                            #Insert new Flow
                            url = "http://127.0.0.1:5000/addFlowIP"
                            data={"Switch":"openflow:"+str(caminho[1]),"in-port":str(caminho[0]), "out-port":str(caminho[-1]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                        elif(len(caminho)==4):
                            print((shortest_paths.get(lista_hosts[0]))[107])
                            switch_name_src=switch_info[str(caminho[1])]
                            switch_name_src=switch_name_src.split("b")[1]
                            switch_name_dst=switch_info[str(caminho[2])]
                            switch_name_dst=switch_name_dst.split("b")[1]
                            #Insert new Flow
                            url = "http://127.0.0.1:5000/addFlowIP"
                            data={"Switch":"openflow:"+str(caminho[1]),"in-port":str(caminho[0]), "out-port":str(switch_name_src)+str(switch_name_dst), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                            data={"Switch":"openflow:"+str(caminho[2]),"in-port":str(switch_name_dst)+str(switch_name_src), "out-port":str(caminho[3]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                        else:
                            print((shortest_paths.get(lista_hosts[0]))[107])
                            switch_name_src=switch_info[str(caminho[1])]
                            switch_name_src=switch_name_src.split("b")[1]
                            switch_name_dst=switch_info[str(caminho[3])]
                            switch_name_dst=switch_name_dst.split("b")[1]
                            switch_name_mdl=switch_info[str(caminho[2])]
                            switch_name_mdl=switch_name_mdl.split("b")[1]
                            #Insert new Flow
                            url = "http://127.0.0.1:5000/addFlowIP"
                            data={"Switch":"openflow:"+str(caminho[1]),"in-port":str(caminho[0]), "out-port":str(switch_name_src)+str(switch_name_mdl), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                            data={"Switch":"openflow:"+str(caminho[2]),"in-port":str(switch_name_mdl)+str(switch_name_src), "out-port":str(switch_name_mdl)+str(switch_name_dst), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
                            data={"Switch":"openflow:"+str(caminho[3]),"in-port":str(switch_name_dst)+str(switch_name_mdl), "out-port":str(caminho[4]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                            res_ = requests.post(url, json=data)
                            if res_.ok:
                                print("Done")
            if(conta==0):
                insert_intent=Insert(intent)
                name,gw=insert_intent.insert_intent()
                msg="Network optimized"
                print("Inserted")
                client = MessageBusClient(port=6666)
                client.run_in_thread()
                client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))
            conta=1
            time.sleep(60)