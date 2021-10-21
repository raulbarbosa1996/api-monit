


import networkx as nx
from flask_restful import Resource
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from mycroft_bus_client import MessageBusClient, Message
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt
import time
import mysql.connector
from itertools import combinations
from resources.Monitoring import *
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
flag=1

def getMysqlConnection():
    return mysql.connector.connect(user='flask', host='0.0.0.0', port='4000', password='password', database='services_active',auth_plugin='mysql_native_password')


class CreateService(Resource):


    def post(self):
        global flag
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
                        perfomance=domains[l].Performance
                        internet_acess=domains[l].Bool
                        for t in range(0,len(domains[l].Acess)):
                            lista_hosts.append(domains[l].Acess[t])
                except:
                    print("")

        source=lista_hosts[0].split(".")[-1]
        destination=lista_hosts[1].split(".")[-1]
        data = request.json
        intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))

        if(response.ok):
            jData = json.loads(response.content)

            #Chamar função com pesos para obter o caminho mais curto
            funce = topologyInformationWWeight(jData)
            G,color_map=funce.topologyInformation()

            pos = nx.spring_layout(G)  # positions for all nodes
            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
            print("AQUi")
            print(G.nodes)
            path = nx.shortest_path(G,source=int(source),target=int(destination),weight='weight')
            print(path)
            print("Chegou")
            path_edges = zip(path,path[1:])
            path_edges = set(path_edges)
            #Chamar função sem peso para criar imagem interpretável
            funce = topologyInformation(jData)
            G_w_weight,color_map_w_weight,lista=funce.topologyInformation()
            pos_w_weight = nx.spring_layout(G_w_weight)
            nx.draw(G_w_weight, with_labels = True,pos=pos_w_weight,node_color = color_map_w_weight,font_size=7)
            nx.draw_networkx_edges(G_w_weight,pos_w_weight,edgelist=path_edges,edge_color='r',width=5)
            nx.draw_networkx_nodes(G_w_weight,pos_w_weight,nodelist=path,node_color='r')
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
            #Add FLow
            switchs_names=[]
            ip_src=path[0]-100
            ip_dst=path[-1]-100

            for i in range(0,len(path)):
                if(i!=0 and i!=len(path)-1):
                    switch_name_src=switch_info[str(path[i])]
                    switch_name_src=switch_name_src.split("b")[1]
                    switchs_names.append(switch_name_src)
            print(switchs_names)
            #Insert new Flow
            for i in range(0,len(switchs_names)):
                if(i==0):
                    in_port=path[0]
                    print(in_port)
                    print(switchs_names)
                    print(switch_name_src)
                    out_port=str(switchs_names[i])+str(switchs_names[i+1])
                    print(out_port)
                elif(i==len(switchs_names)-1):
                    in_port=str(switchs_names[i])+str(switchs_names[i-1])
                    out_port=path[-1]
                else:
                    in_port=str(switchs_names[i])+str(switchs_names[i-1])
                    out_port=str(switchs_names[i])+str(switchs_names[i+1])
                for j in switch_info:
                    if(switch_info[j]=='b'+str(switchs_names[i])):
                        odl_id=j

                lista_source=[]
                lista_destination=[]
                lista_source.append(path[0]-100)
                lista_sw_source="openflow:"+str(path[1])
                lista_destination.append(path[-1]-100)
                lista_sw_destination="openflow:"+str(path[-2])

                url = "http://127.0.0.1:5000/addFlowIP"
                data={"Switch":"openflow:"+str(odl_id),"in-port":str(in_port), "out-port":str(out_port), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                print(data)
                res_ = requests.post(url, json=data)
                if res_.ok:
                    print("Done")
                else:
                    count=0
            url = "http://127.0.0.1:5000/addFlowArp"
            data={"Switch_src":str(lista_sw_source),"Switch_dst":str(lista_sw_destination),"HostSource":lista_source, "HostDestination":lista_destination}
            #data = json.dumps(data, indent = 4)
            print(data)
            res_ = requests.post(url, json=data)
            if res_.ok:
                print("Done")
            else:
                count=0
            #Guardar informação do Flow na db
            try:
                db = getMysqlConnection()
                cur = db.cursor()
                cur.execute('''INSERT INTO service_active (Switch_src,Switch_dst,Host_src,Host_dst) VALUES (%s, %s,%s,%s)''', (str(path[1]), str(path[-2]),str(path[0]),str(path[-1])))
                db.commit()
                print("Flow insert in DB")
            except Exception as e:
                print("Error in SQL:\n", e)
            finally:
                db.close()

            if(internet_acess):
                for i in range(0,len(service_list_hosts)):
                    path = nx.shortest_path(G,source=int(service_list_hosts[i]),target=107,weight='weight')
                    switchs_names=[]
                    ip_src=path[0]-100
                    ip_dst=path[-1]-100
                    url = "http://127.0.0.1:5000/addFlowIP"
                    for i in range(0,len(path)):
                        if(i!=0 and i!=len(path)-1):
                            switch_name_src=switch_info[str(path[i])]
                            switch_name_src=switch_name_src.split("b")[1]
                            switchs_names.append(switch_name_src)
                            #Insert new Flow
                    for i in range(0,len(switchs_names)):
                        if(i==0):
                            in_port=path[0]
                            print(in_port)
                            print(switchs_names)
                            print(switch_name_src)
                            out_port=str(switchs_names[i])+str(switchs_names[i+1])
                            print(out_port)
                        elif(i==len(switchs_names)-1):
                            in_port=str(switchs_names[i])+str(switchs_names[i-1])
                            out_port=path[-1]
                        else:
                            in_port=str(switchs_names[i])+str(switchs_names[i-1])
                            out_port=str(switchs_names[i])+str(switchs_names[i+1])
                        for j in switch_info:
                            if(switch_info[j]=='b'+str(switchs_names[i])):
                                odl_id=j

                        lista_source=[]
                        lista_destination=[]
                        lista_source.append(path[0]-100)
                        lista_sw_source="openflow:"+str(path[1])
                        lista_destination.append(path[-1]-100)
                        lista_sw_destination="openflow:"+str(path[-2])

                        url = "http://127.0.0.1:5000/addFlowIP"
                        data={"Switch":"openflow:"+str(odl_id),"in-port":str(in_port), "out-port":str(out_port), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                        print(data)
                        res_ = requests.post(url, json=data)
                        if res_.ok:
                            print("Done")
                        else:
                            count=0
                    url = "http://127.0.0.1:5000/addFlowArp"
                    data={"Switch_src":str(lista_sw_source),"Switch_dst":str(lista_sw_destination),"HostSource":lista_source, "HostDestination":lista_destination}
                    #data = json.dumps(data, indent = 4)
                    print(data)
                    res_ = requests.post(url, json=data)
                    if res_.ok:
                        print("Done")
                    else:
                        count=0
                    try:
                        db = getMysqlConnection()
                        cur = db.cursor()
                        cur.execute('''INSERT INTO service_active (Switch_src,Switch_dst,Host_src,Host_dst) VALUES (%s, %s,%s,%s)''', (str(path[1]), str(path[-2]),str(path[0]),str(path[-1])))
                        db.commit()
                        print("Flow insert in DB")
                    except Exception as e:
                        print("Error in SQL:\n", e)
                    finally:
                        db.close()

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
            insert_intent=Insert(intent)
            name_service=name
            name,gw=insert_intent.insert_intent()
            msg="Service "+name_service+" created successfully"
            print("Inserted")
            client = MessageBusClient(port=6666)
            client.run_in_thread()
            client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))
            m = Monitoring()
            print(flag)
            if(flag):
                flag=0
                sched = BackgroundScheduler(daemon=True)
                sched.add_job(m.monitoring,'interval',seconds=5)
                sched.start()

        else:
            msg="When trying to compile your request, an error occurred. Please try again "
            client = MessageBusClient(port=6666)
            client.run_in_thread()
            client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))


