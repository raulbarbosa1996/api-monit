


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


def getMysqlConnection():
    return mysql.connector.connect(user='flask_', host='0.0.0.0', port='4000', password='password', database='services_active',auth_plugin='mysql_native_password')

def getMysqlConnection_backup():
    return mysql.connector.connect(user='flask_', host='0.0.0.0', port='4000', password='password', database='services_active_backup',auth_plugin='mysql_native_password')

class GetSwitchFromHost(Resource):
    def GetSwitchFromHost(self):
        #Obter informação switchs
        url = "http://127.0.0.1:5000/infoSW"
        res = requests.get(url)
        if(res.ok):
            switch_info = json.loads(res.content)
            #print(switch_info)
            hosts_to_arp=[]
            for key, value in switch_info.items():
                try:
                    db = getMysqlConnection()

                    sqlstr = "SELECT DISTINCT Host_src from service_active where Switch_src='"+key+"'"
                    #print(sqlstr)
                    cur = db.cursor()
                    cur.execute(sqlstr)
                    output_json = cur.fetchall()
                    #print(output_json)

                    hosts_to_arp.append(output_json)



                except Exception as e:
                    print("Error in SQL:\n", e)
                finally:
                    db.close()
            #print(hosts_to_arp)

            lista_listas=[]
            for i in range(0,len(hosts_to_arp)):
                #print(hosts_to_arp[i])
                lista=[]
                for j in range(0,len(hosts_to_arp[i])):
                    #print(hosts_to_arp[i][j][0])
                    lista.append(int(hosts_to_arp[i][j][0])-100)
                    #print(type(hosts_to_arp[i][j]))
                    if(lista in lista_listas):
                        continue
                    else:
                        lista_listas.append(lista)

            print(lista_listas)


        return lista_listas


    def GetSwitchFromHost_backup(self):
        #Obter informação switchs
        url = "http://127.0.0.1:5000/infoSW"
        res = requests.get(url)
        if(res.ok):
            switch_info = json.loads(res.content)
            #print(switch_info)
            hosts_to_arp=[]
            for key, value in switch_info.items():
                try:
                    db = getMysqlConnection()

                    sqlstr = "SELECT DISTINCT Host_src from service_active where Switch_src='"+key+"'"
                    #print(sqlstr)
                    cur = db.cursor()
                    cur.execute(sqlstr)
                    output_json = cur.fetchall()
                    #print(output_json)

                    hosts_to_arp.append(output_json)



                except Exception as e:
                    print("Error in SQL:\n", e)
                finally:
                    db.close()
            #print(hosts_to_arp)

            lista_listas=[]
            for i in range(0,len(hosts_to_arp)):
                #print(hosts_to_arp[i])
                lista=[]
                for j in range(0,len(hosts_to_arp[i])):
                    #print(hosts_to_arp[i][j][0])
                    lista.append(int(hosts_to_arp[i][j][0])-100)
                    #print(type(hosts_to_arp[i][j]))
                    if(lista in lista_listas):
                        continue
                    else:
                        lista_listas.append(lista)

            print(lista_listas)


        return lista_listas

    def GetSwitch(self,lista):
        url = "http://127.0.0.1:5000/get"
        response=requests.get(url=url)
        if(response.ok):
            jData = json.loads(response.content)
            funce = topologyInformationWWeight(jData)
            G,color_map=funce.topologyInformation()
            pos = nx.spring_layout(G)  # positions for all nodes
            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
            switchs=[]
            for i in range(0,len(lista)):
                switchs.append(G.neighbors(lista[i][0]))
            print(lista)


