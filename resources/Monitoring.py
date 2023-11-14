import networkx as nx
from apscheduler.schedulers.background import BackgroundScheduler
from flask_restful import Resource
from flask import request, jsonify, copy_current_request_context
import requests
from mycroft_bus_client import MessageBusClient, Message
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt
import time
import mysql.connector
from itertools import combinations
import random
from resources.GetHostsWithoutServices import *
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
from resources.GetSwitchFromHost import GetSwitchFromHost

list_backup_host={}
switch=[]
list_of_list_hosts=[]
host=[]
new_switch=""
dict_hosts_down={}
t=0
new_list=[]
old_list=[]
def getMysqlConnection():
    return mysql.connector.connect(user='flask_', host='0.0.0.0', port='4000', password='password', database='services_active',auth_plugin='mysql_native_password')


class Monitoring(Resource):

    def monitoring(self):
        global list_backup_host
        global switch
        global list_of_list_hosts
        global host
        global new_list
        global dict_hosts_down
        global t
        m = GetHostsWithoutServices()
        hosts_list_wout_service=m.hosts_w_service()
        url = "http://127.0.0.1:5000/monitoringInterfaces"
        response=requests.get(url=url)
        switchs_down=response.json()
        switchs_down=switchs_down['message']
        print(switchs_down)
        list_hosts={}

        #Consideramos o host4 como o backup
        for key, value in switchs_down.items():
            if value :#FALTA VERIFICAR SE PERTENCE A SERVICO
                if str(key).split(":")[-1] in switch:
                    print("Switch repeated")
                else:
                    switch.append(str(key).split(":")[-1])
                for i in range(0,len(value)):
                    if value[i].split(":")[-1] in host:
                        print("nao insere")
                    else:
                        host.append(value[i].split(":")[-1])
                print(host)
                for x in range(0,len(host)):
                    if(host[x] in list_backup_host):
                        print(list_backup_host)
                        print("Already solve")

                    else:
                        try:
                            db = getMysqlConnection()
                            sqlstr = "SELECT Switch_src, Switch_dst,Host_src,Host_dst from service_active where Host_src='"+host[x]+"' or Host_dst='"+host[x]+"'"
                            print(sqlstr)
                            cur = db.cursor()
                            cur.execute(sqlstr)
                            output_json = cur.fetchall()
                            print(output_json)
                            for j in range(0,len(output_json)):
                                list_hosts={}
                                list_hosts["Switch_src"] = output_json[j][0]
                                list_hosts["Switch_dst"] = output_json[j][1]
                                list_hosts["Host_src"] = output_json[j][2]
                                list_hosts["Host_dst"] = output_json[j][3]
                                print("Flow numero "+str(j))
                                print(list_hosts)
                                list_hosts_copy = list_hosts.copy()
                                list_of_list_hosts.append(list_hosts_copy)
                                new_switch='104'#backup
                                #Criar nova alternativa
                                '''url = "http://127.0.0.1:5000/getAllPortInfo"
                                response = requests.get(url)
                                if(response.ok):
                                    jData = json.loads(response.content)
                                    for key, value in jData.items():
                                        if(key=='openflow:'+switch[t]):
                                            if value:
                                                for l in range(0,len(value)):
                                                    for key, value in value[l].items():
                                                        new_switch='104
                                                        port_switch=key.split(":")[-1]
                                                        if(port_switch!=host[x] and int(port_switch) in hosts_list_wout_service):
                                                            print(port_switch)
                                                            new_switch=port_switch
                                                            flag=1
                                                            break'''



                                count=1
                                #Se tivermos solução para substituir o host down
                                url = "http://127.0.0.1:5000/infoSW"
                                res = requests.get(url)
                                if(res.ok):
                                    switch_info = json.loads(res.content)

                                #Delete Flow IPV4
                                path=[]
                                path.append(int(list_hosts["Host_src"]))
                                path.append(int(list_hosts["Switch_src"]))
                                path.append(int(list_hosts["Switch_dst"]))
                                path.append(int(list_hosts["Host_dst"]))
                                switchs_names=[]
                                ip_src=path[0]-100
                                ip_dst=path[-1]-100
                                for i in range(0,len(path)):
                                    if(i!=0 and i!=len(path)-1):
                                        switch_name_src=switch_info[str(path[i])]
                                        switch_name_src=switch_name_src.split("b")[1]
                                        switchs_names.append(switch_name_src)
                                for i in range(0,len(switchs_names)):
                                    if(i==0):
                                        in_port=path[0]
                                        out_port=str(switchs_names[i])+str(switchs_names[i+1])

                                    elif(i==len(switchs_names)-1):
                                        in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                        out_port=path[-1]
                                    else:
                                        in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                        out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                    for j in switch_info:
                                        if(switch_info[j]=='b'+str(switchs_names[i])):
                                            odl_id=j
                                    url = "http://127.0.0.1:5000/deleteFlowIPV4"
                                    data={"Switch":"openflow:"+str(odl_id),"in-port":str(in_port), "out-port":str(out_port), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                                    print("delete")
                                    print(data)
                                    res_ = requests.delete(url, json=data)
                                    if res_.ok:
                                        print("Done")
                                        try:
                                            db = getMysqlConnection()
                                            src=str(ip_src+100)
                                            dst=str(ip_dst+100)
                                            sql = "DELETE FROM service_active WHERE Host_src = '"+host[x]+"' or Host_dst = '"+host[x]+"'"
                                            cur = db.cursor()
                                            cur.execute(sql)
                                            db.commit()
                                            print(cur.rowcount, "record(s) deleted")
                                        except Exception as e:
                                            print("Error in SQL:\n", e)
                                        finally:
                                            db.close()
                                    else:
                                        count=0

                                #Adicionar novo Flow
                                path=[]
                                appont=""
                                if(int(list_hosts["Host_src"])==int(host[x])):
                                    path.append(int(new_switch))
                                    path.append(int(list_hosts["Switch_src"]))
                                    path.append(int(list_hosts["Switch_dst"]))
                                    path.append(int(list_hosts["Host_dst"]))
                                else:
                                    path.append(int(list_hosts["Host_src"]))
                                    path.append(int(list_hosts["Switch_src"]))
                                    path.append(int(list_hosts["Switch_dst"]))
                                    path.append(int(new_switch))
                                print("AQUIIIIIIIIIIII")
                                print(path)
                                try:
                                    dict_hosts_down[host[x]].append(path)
                                except:
                                    dict_hosts_down[host[x]]=[path]
                                switchs_names=[]
                                ip_src=path[0]-100
                                ip_dst=path[-1]-100
                                for i in range(0,len(path)):
                                    if(i!=0 and i!=len(path)-1):
                                        switch_name_src=switch_info[str(path[i])]
                                        switch_name_src=switch_name_src.split("b")[1]
                                        switchs_names.append(switch_name_src)

                                for i in range(0,len(switchs_names)):
                                    if(i==0):
                                        in_port=path[0]
                                        out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                    elif(i==len(switchs_names)-1):
                                        in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                        out_port=path[-1]
                                    else:
                                        in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                        out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                    for j in switch_info:
                                        if(switch_info[j]=='b'+str(switchs_names[i])):
                                            odl_id=j

                                    #ADICIONAR Novo FLow DB
                                    try:
                                        db = getMysqlConnection()
                                        cur = db.cursor()
                                        cur.execute('''INSERT INTO service_active (Switch_src,Switch_dst,Host_src,Host_dst) VALUES (%s, %s,%s,%s)''', (str(path[1]), str(path[-2]),str(path[0]),str(path[-1])))
                                        db.commit()
                                        print("Flow insert in DB")
                                    except Exception as e:
                                        print("Error in SQL Insert:\n", e)
                                    finally:
                                        db.close()
                                    lista_source=[]
                                    lista_destination=[]
                                    lista_source.append(path[0]-100)
                                    lista_sw_source="openflow:"+str(path[1])
                                    lista_destination.append(path[-1]-100)
                                    lista_sw_destination="openflow:"+str(path[-2])
                                    url = "http://127.0.0.1:5000/addFlowIP"
                                    data={"Switch":"openflow:"+str(odl_id),"in-port":str(in_port), "out-port":str(out_port), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                                    print("add")
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

                                if host[x] in list_backup_host:
                                    try:
                                        list_backup_host[host[x]].append(new_switch)
                                    except:
                                        list_backup_host[host[x]]=new_switch
                                else:
                                    list_backup_host[host[x]] = new_switch

                        except Exception as e:
                            print("Error in SQL:\n", e)
                        finally:
                            db.close()

                        m = GetSwitchFromHost()
                        list_to_connect_internet=m.GetSwitchFromHost()

                        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
                        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))

                        if(response.ok):
                            jData = json.loads(response.content)
                            url = "http://127.0.0.1:5000/addFlowArp"
                            #Chamar função com pesos para obter o caminho mais curto
                            funce = topologyInformationWWeight(jData)
                            G,color_map=funce.topologyInformation()

                            pos = nx.spring_layout(G)  # positions for all nodes
                            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
                            for i in range(0,len(list_to_connect_internet)):
                                try:
                                    print(list_to_connect_internet[i][0])
                                    path = nx.shortest_path(G,source=list_to_connect_internet[i][0]+100,target=107,weight='weight')
                                    lista_sw_source="openflow:"+str(path[1])
                                    lista_sw_destination="openflow:"+str(path[-2])
                                    data={"Switch_src":str(lista_sw_source),"Switch_dst":str(lista_sw_destination),"HostSource":list_to_connect_internet[i], "HostDestination":[7]}
                                    #data = json.dumps(data, indent = 4)
                                    print(data)
                                    res_ = requests.post(url, json=data)
                                    if res_.ok:
                                        print("Done")
                                    else:
                                        count=0

                                except:
                                    print("fim")
                            client = MessageBusClient(host='192.168.1.70',port=6666)
                            client.run_in_thread()
                            client.emit(Message('speak', data={'utterance': "Service failing but a solution has been identified"},context={'context':'switch'}))
                t+=1

            else:
                        try:
                            for w in range(0,len(switch)):
                                if(key=='openflow:'+switch[w]):
                                    for l in range(0,len(host)):
                                        try:
                                            if(list_backup_host):
                                                print("Host up again")
                                                print(list_backup_host)
                                                print(list_of_list_hosts)
                                                #colar aqui
                                                url = "http://127.0.0.1:5000/infoSW"
                                                res = requests.get(url)
                                                if(res.ok):
                                                    switch_info = json.loads(res.content)
                                                    if(dict_hosts_down[host[l]]):
                                                        for i in range(0,len(dict_hosts_down[host[l]])):
                                                            path=dict_hosts_down[host[l]][i]
                                                            switchs_names=[]
                                                            ip_src=path[0]-100
                                                            ip_dst=path[-1]-100

                                                            for i in range(0,len(path)):
                                                                if(i!=0 and i!=len(path)-1):
                                                                    switch_name_src=switch_info[str(path[i])]
                                                                    switch_name_src=switch_name_src.split("b")[1]
                                                                    switchs_names.append(switch_name_src)
                                                            #Delete old Flows
                                                            for i in range(0,len(switchs_names)):
                                                                if(i==0):
                                                                    in_port=path[0]
                                                                    out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                                                elif(i==len(switchs_names)-1):
                                                                    in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                                                    out_port=path[-1]
                                                                else:
                                                                    in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                                                    out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                                                for j in switch_info:
                                                                    if(switch_info[j]=='b'+str(switchs_names[i])):
                                                                        odl_id=j

                                                                url = "http://127.0.0.1:5000/deleteFlowIPV4"
                                                                data={"Switch":"openflow:"+str(odl_id),"in-port":str(in_port), "out-port":str(out_port), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                                                                print("delete")
                                                                print(data)
                                                                res_ = requests.delete(url, json=data)
                                                                if res_.ok:
                                                                    print("Done")
                                                                    try:
                                                                        db = getMysqlConnection()
                                                                        src=str(ip_src+100)
                                                                        dst=str(ip_dst+100)
                                                                        sql = "DELETE FROM service_active WHERE (Host_src = '"+src+"' and Host_dst = '"+dst+"') or (Host_src = '"+dst+"' and Host_dst = '"+src+"')"
                                                                        cur = db.cursor()
                                                                        cur.execute(sql)
                                                                        db.commit()
                                                                        print(cur.rowcount, "record(s) deleted")
                                                                    except Exception as e:
                                                                        print("Error in SQL:\n", e)
                                                                    finally:
                                                                        db.close()
                                                                else:
                                                                    count=0
                                                        #Adicionar novo flow
                                                        for i in range(0,len(list_of_list_hosts)):
                                                            path=[]
                                                            path.append(int(list_of_list_hosts[i]["Host_src"]))
                                                            path.append(int(list_of_list_hosts[i]["Switch_src"]))
                                                            path.append(int(list_of_list_hosts[i]["Switch_dst"]))
                                                            path.append(int(list_of_list_hosts[i]["Host_dst"]))
                                                            switchs_names=[]
                                                            ip_src=path[0]-100
                                                            ip_dst=path[-1]-100
                                                            for i in range(0,len(path)):
                                                                if(i!=0 and i!=len(path)-1):
                                                                    switch_name_src=switch_info[str(path[i])]
                                                                    switch_name_src=switch_name_src.split("b")[1]
                                                                    switchs_names.append(switch_name_src)

                                                            for i in range(0,len(switchs_names)):
                                                                if(i==0):
                                                                    in_port=path[0]
                                                                    out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                                                elif(i==len(switchs_names)-1):
                                                                    in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                                                    out_port=path[-1]
                                                                else:
                                                                    in_port=str(switchs_names[i])+str(switchs_names[i-1])
                                                                    out_port=str(switchs_names[i])+str(switchs_names[i+1])
                                                                for j in switch_info:
                                                                    if(switch_info[j]=='b'+str(switchs_names[i])):
                                                                        odl_id=j
                                                                #ADICIONAR Novo FLow DB
                                                                try:
                                                                    db = getMysqlConnection()
                                                                    cur = db.cursor()
                                                                    cur.execute('''INSERT INTO service_active (Switch_src,Switch_dst,Host_src,Host_dst) VALUES (%s, %s,%s,%s)''', (str(path[1]), str(path[-2]),str(path[0]),str(path[-1])))
                                                                    db.commit()
                                                                    print("Flow insert in DB")
                                                                except Exception as e:
                                                                    print("Error in SQL Insert:\n", e)
                                                                finally:
                                                                    db.close()
                                                                lista_source=[]
                                                                lista_destination=[]
                                                                lista_source.append(path[0]-100)
                                                                lista_sw_source="openflow:"+str(path[1])
                                                                lista_destination.append(path[-1]-100)
                                                                lista_sw_destination="openflow:"+str(path[-2])
                                                                url = "http://127.0.0.1:5000/addFlowIP"
                                                                data={"Switch":"openflow:"+str(odl_id),"in-port":str(in_port), "out-port":str(out_port), "ipv4-src":"192.168.2."+str(ip_src), "ipv4-dst":"192.168.2."+str(ip_dst)}
                                                                print("add")
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
                                                        m = GetSwitchFromHost()
                                                        list_to_connect_internet=m.GetSwitchFromHost()

                                                        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
                                                        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))

                                                        if(response.ok):
                                                            jData = json.loads(response.content)
                                                            url = "http://127.0.0.1:5000/addFlowArp"
                                                            #Chamar função com pesos para obter o caminho mais curto
                                                            funce = topologyInformationWWeight(jData)
                                                            G,color_map=funce.topologyInformation()

                                                            pos = nx.spring_layout(G)  # positions for all nodes
                                                            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
                                                            for i in range(0,len(list_to_connect_internet)):
                                                                try:
                                                                    print(list_to_connect_internet[i][0])
                                                                    path = nx.shortest_path(G,source=list_to_connect_internet[i][0]+100,target=107,weight='weight')
                                                                    lista_sw_source="openflow:"+str(path[1])
                                                                    lista_sw_destination="openflow:"+str(path[-2])
                                                                    data={"Switch_src":str(lista_sw_source),"Switch_dst":str(lista_sw_destination),"HostSource":list_to_connect_internet[i], "HostDestination":[7]}
                                                                    #data = json.dumps(data, indent = 4)
                                                                    print(data)
                                                                    res_ = requests.post(url, json=data)
                                                                    if res_.ok:
                                                                        print("Done")
                                                                    else:
                                                                        count=0
                                                                except:
                                                                    print("fim")
                                                #list_backup_host.remove(host[l])
                                                del list_backup_host[host[l]]
                                                client = MessageBusClient(host='192.168.1.70',port=6666)
                                                client.run_in_thread()
                                                client.emit(Message('speak', data={'utterance': "Service is again active as previously defined"},context={'context':'switch'}))
                                        except:
                                            print("Error backup list")
                        except:
                            print("No fails")
            new_list=host




