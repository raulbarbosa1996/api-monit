import networkx as nx
from flask_restful import Resource
import requests
from mycroft_bus_client import MessageBusClient, Message
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt

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


class Prioritys(Resource):

    def get(self):
        #Obter hosts com prioridade da base de dados
        priority=Priority()
        host,priority=priority.get_all_prioritys()

        #Verificar quantos hosts existem sem prioridade (comparar hosts da topologia com os da db para verificar quais nao tem prioridade)
        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
        if(response.ok):
            jData = json.loads(response.content)
            funce = topologyInformation(jData)
            G,color_map,list_hosts=funce.topologyInformation()
            list_hosts_wout_priority=[]
            for i in range(0,len(list_hosts)):
                verify=0
                for j in range(0,len(host)):
                    val=host[j].split(".")
                    #print(int(val[-1]))
                    #print(list_hosts[i]-100)
                    if(int((list_hosts[i]-100))==int(val[-1]) or int((list_hosts[i]-100))==7):
                        verify=1
                if(verify==0):
                    list_hosts_wout_priority.append("192.168.2."+str(list_hosts[i]-100))
            print(list_hosts_wout_priority)
            print(host)

            #Calcular Gbs para hosts com prioridade e sem prioridade
            gb_prioritary=2000
            size_gb_prioritary=2000*len(host)
            gb_Nprioritary= 10000-size_gb_prioritary
            gb_Nprioritary=int(gb_Nprioritary/len(list_hosts_wout_priority))
            if(gb_Nprioritary>=2000):
                gb_Nprioritary=500

            #Fazer pedido de QOS para os hosts com prioridade
            for i in range(0,len(host)):

                data={"source_ns":host[i],"destination_ns":"192.168.2.7", "max_rate":str(gb_prioritary)}
                print(data)
                url = "http://127.0.0.1:5000/double_sim"
                res = requests.post(url, json=data)
                if res.ok:
                    print("Ok")
                    print(res.json())
            #Fazer pedido de QOS para os hosts sem prioridade
            for j in range(0,len(list_hosts_wout_priority)):

                data_={"source_ns":list_hosts_wout_priority[j],"destination_ns":"192.168.2.7", "max_rate":str(gb_Nprioritary)}
                print(data_)
                url_ = "http://127.0.0.1:5000/double_sim"
                res_ = requests.post(url_, json=data_)
                if res_.ok:
                    print("Ok")
                    print(res_.json())

    def post(self):
        #FALTA- apagar da db hosts que tem prioridade igual a high e vao passar para low (modificar codigo)
        data = request.json
        intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


        #Obter os hosts envolvidos no serviço
        data_services = GetServicesHosts(intent)
        lista_serviços = data_services.get_sameTarget()
        z = json.loads(data)
        z["Conditions"][0]["Constraints"][0]["Domains"][0]["Acess"] = lista_serviços
        data_s = json.dumps(z)
        intent = json.loads(data_s, object_hook=lambda d: SimpleNamespace(**d))
        print(intent)

        #Verificar se é para priorizar ou não
        cond=intent.Conditions
        for i in range(0,len(cond)):
            constr=cond[i].Constraints
            for j in range(0,len(constr)):
                try:
                    domains=constr[j].Domains
                    for l in range(0,len(domains)):
                        priority_in=domains[l].Level
                except:
                    print("")


        if(priority_in=='High'):
            print("Priorizar")
            print(lista_serviços)
            #Obter todos os hosts da topologia para sabermos quais sao prioritarios e quais nao sao
            list_hosts_wout_priority=[]
            url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
            response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
            if(response.ok):
                jData = json.loads(response.content)
                funce = topologyInformation(jData)
                G,color_map,list_hosts=funce.topologyInformation()
                for i in range(0,len(list_hosts)):
                    for j in range(0,len(lista_serviços)):
                        #Se o host for o 7 (Internet) continuar
                        if(int((list_hosts[i]-100))==7):
                            continue
                        else:
                            list_hosts_wout_priority.append("192.168.2."+str(list_hosts[i]))

                list_hosts_wout_priority = list(set(list_hosts_wout_priority))
                list_hosts_wout_priority=list(set(list_hosts_wout_priority) - set(lista_serviços))

                #Calcular Gbs para hosts com prioridade e sem prioridade
                gb_prioritary=4000
                size_gb_prioritary=gb_prioritary*len(lista_serviços)
                gb_Nprioritary= 10000-size_gb_prioritary
                try:
                    gb_Nprioritary=int(gb_Nprioritary/len(list_hosts_wout_priority))
                except:
                    gb_Nprioritary=500
                if(gb_Nprioritary>=4000):
                    gb_Nprioritary=500
                print(lista_serviços)
                print(list_hosts_wout_priority)

                #Obter caminhos do serviço
                path=[]
                for i in range(0,len(lista_serviços)):
                    try:
                        path.append(nx.shortest_path(G,source=int(lista_serviços[i].split(".")[-1]),target=int(lista_serviços[i+1].split(".")[-1]),weight='weight'))
                    except:
                        print("")
                print(path)

                #Fazer pedido de QOS para os hosts com prioridade
                try:
                    data={"source_ns":lista_serviços[0],"destination_ns":lista_serviços[1], "max_rate":str(gb_prioritary)}
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

                #Fazer pedido de QOS para os hosts sem prioridade


            else:
                print("despriorizar")
                print(lista_serviços)


