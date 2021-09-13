


import networkx as nx
from flask_restful import Resource
import requests
from mycroft_bus_client import MessageBusClient, Message
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt
import time
import mysql.connector
from itertools import combinations
import random

from Functions.GetServicesHosts import GetServicesHosts
from Functions.Insert import Insert
from Functions.GetPrioritys import Priority
from Functions.GetDataForPath import GetDataForPath

from ModelTopologyWWeight import topologyInformationWWeight
from ModelTopology import topologyInformation
from flask import  jsonify, request, make_response
import  time
from types import SimpleNamespace

from models import Intents

def getMysqlConnection():
    return mysql.connector.connect(user='flask_u', host='0.0.0.0', port='4000', password='password', database='services',auth_plugin='mysql_native_password')

class CreateService(Resource):

    def post(self):
        data = request.json
        intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        print(intent)

        #Obter nome do serviço e hosts envolvidos
        name=""
        perfomance=""
        priority=""
        internet_acess=False
        lista_hosts=[]
        cond=intent.Conditions
        for i in range(0,len(cond)):
            constr=cond[i].Constraints
            for j in range(0,len(constr)):
                try:
                    domains=constr[j].Domains
                    for l in range(0,len(domains)):
                        name=domains[l].Name
                        perfomance=domains[l].Perfomance
                        internet_acess=domains[l].Bool
                        for t in range(0,len(domains[l].Acess)):
                            lista_hosts.append(domains[l].Acess[t])
                except:
                    print("")

        print(name)
        print(lista_hosts)
        print(perfomance)
        print(internet_acess)

        source=lista_hosts[0].split(".")[-1]
        destination=lista_hosts[1].split(".")[-1]
        data = request.json
        intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        print(intent)

        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))

        if(response.ok):
            jData = json.loads(response.content)

            #Chamar função com pesos para obter o caminho mais curto
            funce = topologyInformationWWeight(jData)
            G,color_map=funce.topologyInformation()
            pos = nx.spring_layout(G)  # positions for all nodes
            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)

            path = nx.shortest_path(G,source=int(source),target=int(destination),weight='weight')
            print(path)
            plt.clf()
            path_edges = zip(path,path[1:])
            path_edges = set(path_edges)

            #Chamar função sem peso para criar imagem interpretável
            funce = topologyInformation(jData)
            G_w_weight,color_map_w_weight,lista=funce.topologyInformation()
            pos_w_weight = nx.spring_layout(G_w_weight)
            nx.draw(G_w_weight, with_labels = True,pos=pos_w_weight,node_color = color_map_w_weight,font_size=7)
            nx.draw_networkx_edges(G_w_weight,pos_w_weight,edgelist=path_edges,edge_color='r',width=5)
            nx.draw_networkx_nodes(G_w_weight,pos_w_weight,nodelist=path,node_color='r')
            l,r = plt.xlim()
            plt.xlim(l-1,r+1)
            plt.savefig('tss.png', bbox_inches="tight")
            plt.clf()

            #Obter informação switchs
            url = "http://127.0.0.1:5000/infoSW"
            res = requests.get(url)
            if(res.ok):
                switch_info = json.loads(res.content)
                print(switch_info)

            #Obter os hosts que estao envolvidos no serviço e os que não estão
            nodes=list(G.nodes)
            lista_hosts=[]
            for i in range(0,len(nodes)):
                if (color_map[i]=='blue'):
                    lista_hosts.append(nodes[i])
            print(lista_hosts)
            #hosts que estao envolvidos no serviço
            service_list_hosts = [element for element in lista_hosts if element in path]
            print(service_list_hosts)
            #hosts que não estão envolvidos no serviço
            hosts_list_wout_service=list(set(lista_hosts) - set(service_list_hosts))
            delete_flows=hosts_list_wout_service
            #Apagar host associado à internet
            hosts_list_wout_service.remove(107)
            print(hosts_list_wout_service)



            #Obter current_id para apagar flows
            url = "http://127.0.0.1:5000/currentId"
            res = requests.get(url)
            if(res.ok):
                current_id = json.loads(res.content)
            body={
                "flow-node-inventory:flow": [
                    {
                        "id": "100",
                        "flags": "",
                        "priority": 3,
                        "opendaylight-flow-statistics:flow-statistics": {
                            "duration": {
                                "second": 2013,
                                "nanosecond": 768000000
                            },
                            "packet-count": 0,
                            "byte-count": 0
                        },
                        "table_id": 0,
                        "hard-timeout": 0,
                        "instructions": {
                            "instruction": [
                                {
                                    "order": 0,
                                    "apply-actions": {
                                        "action": [
                                            {
                                                "order": 0,
                                                "drop-action": {

                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        },
                        "idle-timeout": 0,
                        "match": {
                            "in-port":101,
                            "ipv4-destination": "192.168.2.1/32",
                            "ipv4-source": "192.168.2.2/32",
                            "ethernet-match": {
                                "ethernet-type": {
                                    "type": 2048
                                }
                            }

                        },
                        "cookie": 0
                    }
                ]
            }
            #Apagar para hosts de diferentes serviços e internet
            data_services = GetServicesHosts(intent)
            lista_serviços = data_services.get_sameTarget()

            if(lista_serviços and internet_acess):
                try:
                    lista_serviços.remove("192.168.2.107")
                except:
                    print("No")
            if(lista_serviços):
                print("LISTA DE SERVIÇOS")
                print(lista_serviços)
                print(service_list_hosts)
                for i in range(0,len(service_list_hosts)):
                    for j in range(0,len(lista_serviços)):
                        id_number=random.randint(1000,10000)
                        body['flow-node-inventory:flow'][0]['id'] = str(id_number)
                        body['flow-node-inventory:flow'][0]['match']['in-port']=service_list_hosts[i]
                        body['flow-node-inventory:flow'][0]['match']['ipv4-source']="192.168.2."+str(int(str(service_list_hosts[i]).split(".")[-1])-100)+"/32"
                        body['flow-node-inventory:flow'][0]['match']['ipv4-destination']="192.168.2."+str(int(lista_serviços[j].split(".")[-1])-100)+"/32"
                        for key in switch_info:
                            try:
                                url='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:'+str(key)+'/table/0/flow/'+str(id_number)
                                res_ = requests.put(url, json=body, auth=HTTPBasicAuth('admin', 'admin'))
                                if res_.ok:
                                    print("Done")
                                    print(url)
                                else:
                                    print(url)
                                    print(body)
                                    print(res_.status_code)
                            except :
                                print("")
            count=1
            #Add FLow
            if(len(path)==4):
                ip_src=path[0]-100
                ip_dst=path[-1]-100
                switch_name_src=switch_info[str(path[1])]
                switch_name_src=switch_name_src.split("b")[1]
                switch_name_dst=switch_info[str(path[2])]
                switch_name_dst=switch_name_dst.split("b")[1]
                #Insert new Flow
                url = "http://127.0.0.1:5000/addFlowIP"
                data={"Switch":"openflow:"+str(path[1]),"in-port":str(path[0]), "out-port":str(switch_name_src)+str(switch_name_dst), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                print(data)
                res_ = requests.post(url, json=data)
                if res_.ok:
                    print("Done")
                else:
                    count=0
                data={"Switch":"openflow:"+str(path[2]),"in-port":str(switch_name_dst)+str(switch_name_src), "out-port":str(path[3]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                print(data)
                res_ = requests.post(url, json=data)
                if res_.ok:
                    print("Done")
                else:
                    count=0

            if(internet_acess):
                for i in range(0,len(service_list_hosts)):
                    path = nx.shortest_path(G,source=int(service_list_hosts[i]),target=107,weight='weight')
                    print("Aqui")
                    print(path)
                    ip_src=path[0]-100
                    ip_dst=path[-1]-100
                    switch_name_src=switch_info[str(path[1])]
                    switch_name_src=switch_name_src.split("b")[1]
                    switch_name_dst=switch_info[str(path[2])]
                    switch_name_dst=switch_name_dst.split("b")[1]
                    url = "http://127.0.0.1:5000/addFlowIP"
                    data={"Switch":"openflow:"+str(path[1]),"in-port":str(path[0]), "out-port":str(switch_name_src)+str(switch_name_dst), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                    print(data)
                    res_ = requests.post(url, json=data)
                    if res_.ok:
                        print("Done")
                    else:
                        count=0
                    data={"Switch":"openflow:"+str(path[2]),"in-port":str(switch_name_dst)+str(switch_name_src), "out-port":str(path[3]), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                    print(data)
                    res_ = requests.post(url, json=data)
                    if res_.ok:
                        print("Done")
                    else:
                        count=0
                    service_list_hosts.append(107)

            if perfomance:
                try:
                    comb = combinations(service_list_hosts, 2)
                    # Print the obtained combinations
                    for i in list(comb):
                        print (i)
                        data={"source_ns":"192.168.2."+str(i[0]-100),"destination_ns":"192.168.2."+str(i[1]-100), "max_rate":str(perfomance[0])}
                        print(data)
                        url = "http://127.0.0.1:5000/double_sim"
                        res = requests.post(url, json=data)
                        if res.ok:
                            print("Ok")
                            print(res.json())
                        else:
                            print(res)
                except:
                    msg="Hosts with priorities"
            for key in switch_info:
                for i in range(0,len(service_list_hosts)):
                    #Delete Flow id
                    url = "http://127.0.0.1:5000/deleteFlow_withID"
                    data={"Switch":str(switch_info[key]), "Flow_id":str(service_list_hosts[i])}
                    print(data)
                    res_ = requests.delete(url, json=data)
                    if res_.ok:
                        print("Done")
            insert_intent=Insert(intent)
            name_service=name
            name,gw=insert_intent.insert_intent()
            msg="Service "+name_service+" created successfully"
            print("Inserted")
            client = MessageBusClient(port=6666)
            client.run_in_thread()
            client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))
        else:
            msg="When trying to compile your request, an error occurred. Please try again "

            client = MessageBusClient(port=6666)
            client.run_in_thread()
            client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))


