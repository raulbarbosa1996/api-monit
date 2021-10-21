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


class GetHostsWithoutServices(Resource):

    def hosts_w_service(self):
        #Criar grafo da rede
        url = "http://127.0.0.1:5000/get"
        response=requests.get(url=url)
        if(response.ok):
            jData = json.loads(response.content)
            funce = topologyInformationWWeight(jData)
            G,color_map=funce.topologyInformation()
            pos = nx.spring_layout(G)  # positions for all nodes
            nx.draw(G, with_labels = True,pos=pos,node_color = color_map,font_size=7)
            nodes=list(G.nodes)
            #Obter todos os hosts com serviços
            hosts_w_services=set([])
            url = "http://127.0.0.1:5500/sr/intents"
            response=requests.get(url=url)
            intents=response.json()
            for i in range(0,len(intents)):
                cond=intents[i]['Conditions']
                for j in range(0,len(cond)):
                    constr=cond[j]['Constraints']
                    for l in range(0,len(constr)):
                        domains=constr[l]['Domains']
                        for x in range(0,len(domains)):
                            acess=domains[x]['Acess']
                            for t in range(0,len(acess)):
                                hosts_w_services.add(int(acess[t].split(".")[-1]))
            nodes=list(G.nodes)
            lista_all_hosts=[]
            for i in range(0,len(nodes)):
                if (color_map[i]=='blue' and nodes[i]!=107):
                    lista_all_hosts.append(nodes[i])
            hosts_list_wout_service=list(set(lista_all_hosts) - set(hosts_w_services))
            return hosts_list_wout_service






