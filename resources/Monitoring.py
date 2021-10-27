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
list_backup_host={}
switch=""
list_of_list_hosts=[]
host=""
new_switch=""
dict_hosts_down={}
def getMysqlConnection():
    return mysql.connector.connect(user='flask', host='0.0.0.0', port='4000', password='password', database='services_active',auth_plugin='mysql_native_password')


class Monitoring(Resource):

    def monitoring(self):
        global list_backup_host
        global switch
        global list_of_list_hosts
        global host
        global new_switch
        global dict_hosts_down
        m = GetHostsWithoutServices()
        hosts_list_wout_service=m.hosts_w_service()
        url = "http://127.0.0.1:5000/monitoringInterfaces"
        response=requests.get(url=url)
        switchs_down=response.json()
        switchs_down=switchs_down['message']
        print(switchs_down)
        list_hosts={}
        for key, value in switchs_down.items():
            if value:
                switch=str(key).split(":")[-1]
                for i in range(0,len(value)):
                    host=value[0].split(":")[-1]

                    if(host in list_backup_host):
                        print("Already solve")
                    else:
                        try:
                            db = getMysqlConnection()
                            sqlstr = "SELECT Switch_src, Switch_dst,Host_src,Host_dst from service_active where Host_src='"+host+"' or Host_dst='"+host+"'"
                            print(sqlstr)
                            cur = db.cursor()
                            cur.execute(sqlstr)
                            output_json = cur.fetchall()
                            print(output_json)
                            for j in range(0,len(output_json)):
                                list_hosts["Switch_src"] = output_json[j][0]
                                list_hosts["Switch_dst"] = output_json[j][1]
                                list_hosts["Host_src"] = output_json[j][2]
                                list_hosts["Host_dst"] = output_json[j][3]
                                print(list_hosts)
                                list_of_list_hosts.append(list_hosts)
                                #Criar nova alternativa
                                url = "http://127.0.0.1:5000/getAllPortInfo"
                                response = requests.get(url)
                                if(response.ok):
                                    jData = json.loads(response.content)
                                    for key, value in jData.items():
                                        if(key=='openflow:'+switch):
                                            if value:
                                                for l in range(0,len(value)):
                                                    for key, value in value[l].items():
                                                        port_switch=key.split(":")[-1]
                                                        if(port_switch!=host and int(port_switch) in hosts_list_wout_service):
                                                            print(port_switch)
                                                            new_switch=port_switch
                                                            flag=1
                                                            break


                                if(new_switch):
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
                                        res_ = requests.post(url, json=data)
                                        if res_.ok:
                                            print("Done")
                                        else:
                                            count=0
                                    #Adicionar novo Flow
                                    path=[]
                                    appont=""
                                    if(int(list_hosts["Host_src"])==int(host)):
                                        path.append(int(new_switch))
                                        path.append(int(list_hosts["Switch_src"]))
                                        path.append(int(list_hosts["Switch_dst"]))
                                        path.append(int(list_hosts["Host_dst"]))
                                    else:
                                        path.append(int(list_hosts["Host_src"]))
                                        path.append(int(list_hosts["Switch_src"]))
                                        path.append(int(list_hosts["Switch_dst"]))
                                        path.append(int(new_switch))
                                    try:
                                        dict_hosts_down[host].append(path)
                                    except:
                                        dict_hosts_down[host]=[path]
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

                                    if host in list_backup_host:
                                        try:
                                            list_backup_host[host].append(new_switch)
                                        except:
                                            list_backup_host[host]=new_switch
                                    else:
                                        list_backup_host[host] = new_switch

                            print(list_of_list_hosts)
                        except Exception as e:
                            print("Error in SQL:\n", e)
                        finally:
                            db.close()

            else:
                try:
                    if(key=='openflow:'+switch):
                        try:
                            if(list_backup_host):
                                print("Host up again")
                                print(list_of_list_hosts)
                                #Se o host voltar a estar ativo substituir
                                url = "http://127.0.0.1:5000/infoSW"
                                res = requests.get(url)
                                if(res.ok):
                                    switch_info = json.loads(res.content)
                                    #Delete FLOWS
                                    if(dict_hosts_down[host]):
                                        for i in range(0,len(dict_hosts_down[host])):
                                            path=dict_hosts_down[host][i]
                                            switchs_names=[]
                                            ip_src=path[0]-100
                                            ip_dst=path[-1]-100

                                            for i in range(0,len(path)):
                                                if(i!=0 and i!=len(path)-1):
                                                    switch_name_src=switch_info[str(path[i])]
                                                    switch_name_src=switch_name_src.split("b")[1]
                                                    switchs_names.append(switch_name_src)
                                            #Insert new Flow
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
                                                res_ = requests.post(url, json=data)
                                                if res_.ok:
                                                    print("Done")
                                                else:
                                                    count=0
                                    #Add Flow IPV4
                                    try:
                                        db = getMysqlConnection()
                                        sqlstr = "SELECT Switch_src, Switch_dst,Host_src,Host_dst from service_active where Host_src='"+host+"' or Host_dst='"+host+"'"
                                        print(sqlstr)
                                        cur = db.cursor()
                                        cur.execute(sqlstr)
                                        output_json = cur.fetchall()
                                        print(output_json)
                                        for j in range(0,len(output_json)):
                                            list_hosts["Switch_src"] = output_json[j][0]
                                            list_hosts["Switch_dst"] = output_json[j][1]
                                            list_hosts["Host_src"] = output_json[j][2]
                                            list_hosts["Host_dst"] = output_json[j][3]

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


                                    except Exception as e:
                                        print("Error in SQL:\n", e)
                                    finally:
                                        db.close()


                            list_backup_host.clear()
                        except:
                            print("Host back again")
                except:
                    print("No fails")






