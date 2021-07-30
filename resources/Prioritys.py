import networkx as nx
from flask_restful import Resource
import requests
from mycroft_bus_client import MessageBusClient, Message
from requests.auth import HTTPBasicAuth
import json
import matplotlib.pyplot as plt

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
        print(intent)

        #Obter hosts com regras atribuidas na base de dados ex :hosts=[3,5,1] priority=[Low, High, Low]
        priority=Priority()
        host,priority,lista=priority.get_all_prioritys()
        host_h=[]

        #Obter regra do utilizador
        intent_in=[]
        priority_in=[]
        cond=intent.Conditions
        for i in range(0,len(cond)):
            constr=cond[i].Constraints
            for j in range(0,len(constr)):
                try:
                    domains=constr[j].Domains
                    for l in range(0,len(domains)):
                        intent_in.append(domains[l].Domain)
                except:
                    print("")
                try:
                    domains=constr[j].Domains
                    for l in range(0,len(domains)):
                        priority_in.append(domains[l].Level)
                except:
                    print("")
        flag=0
        if(host):
            print("entrou")
            # Se o dominio que entrou já existir entao alteramos o valor da prioridade
            for i in range(0,len(intent_in)):
                for j in range(0,len(host)):
                    if(host[j]==intent_in[i]):
                        print("entrou 2")
                        priority[j]=priority_in[i]

                        if(intent.info!="Append" and intent.info!=""):
                            #apagar daqui
                            '''
                            posit=intent.info.split(" ")

                            print(lista[int(posit[-1])]['id'])
                            post = Intents.load(lista[int(posit[-1])]['id'])
                            var=post["Conditions"][0]["Constraints"][int(posit[0])]["Domains"]
                            for l in range(0,len(var)):
                                if(var[l]["Domain"]==host[j] and priority[j]=='Low' and priority_in[i]=='Low'):
                                    del post["Conditions"][0]["Constraints"][int(posit[0])]["Domains"][l]
                                    flag=1
                                    print("eliminou")
                                    if(not post["Conditions"][0]["Constraints"][int(posit[0])]["Domains"]):
                                        url='http://hostname_or_IP:Port/databasename/document_id/?rev='+str(intent._rev)
                                        x = requests.delete(url)
                                        print(x.text)
                                        #ate aqui
            if(flag):
                post.store()'''
        else:
            for i in range(0,len(priority_in)):
                    host.append(intent_in[i])
                    priority.append(priority_in[i])


        print(host)
        print(priority)
        list_hosts_wout_priority=[]
        list_hosts_min_priority=[]
        #Se o dominio in for Low
        for i in range(0,len(intent_in)):
            for j in range(0,len(host)):
                if(host[j]==intent_in[i] and priority[j]=='Low' and flag!=1):
                    list_hosts_min_priority.append(intent_in[i])
        print("prioridade minimaDeprio")
        print(list_hosts_min_priority)

        #Dividir hosts da base de dados consoante o tipo de priority
        for i in range(0,len(host)):
            if(priority[i]=="Low"):
                list_hosts_wout_priority.append(host[i])
            else:
                if(priority[i]=="High"):
                    host_h.append(host[i])

        #Obter todos os hosts da topologia
        url = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
        response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
        if(response.ok):
            jData = json.loads(response.content)
            funce = topologyInformation(jData)
            G,color_map,list_hosts=funce.topologyInformation()

            for i in range(0,len(list_hosts)):
                for j in range(0,len(host)):
                    #Se o host for o 7 (Internet) continuar
                    if(int((list_hosts[i]-100))==7):
                        continue
                    else:
                        list_hosts_wout_priority.append("192.168.2."+str(list_hosts[i]-100))

            list_hosts_wout_priority = list(set(list_hosts_wout_priority))
            list_hosts_wout_priority=list(set(list_hosts_wout_priority) - set(host_h))

            #Calcular Gbs para hosts com prioridade e sem prioridade
            gb_prioritary=4000
            size_gb_prioritary=4000*len(host_h)
            gb_Nprioritary= 10000-size_gb_prioritary
            try:
                gb_Nprioritary=int(gb_Nprioritary/len(list_hosts_wout_priority))
            except:
                gb_Nprioritary=500
            if(gb_Nprioritary>=4000):
                gb_Nprioritary=500


            print(host_h)
            print(list_hosts_wout_priority)
            #Fazer pedido de QOS para os hosts com prioridade
            try:
                for i in range(0,len(host_h)):

                    data={"source_ns":host_h[i],"destination_ns":"192.168.2.7", "max_rate":str(gb_prioritary)}
                    print(data)
                    url = "http://127.0.0.1:5000/double_sim"
                    res = requests.post(url, json=data)
                    if res.ok:
                        print("Ok")
                        print(res.json())
                    else:
                        print(res)
            except:
                msg="Hosts without priorities"

            #Fazer pedido de QOS para os hosts sem prioridade
            for j in range(0,len(list_hosts_wout_priority)):
                data_={"source_ns":list_hosts_wout_priority[j],"destination_ns":"192.168.2.7", "max_rate":str(gb_Nprioritary)}
                print(data_)
                url_ = "http://127.0.0.1:5000/double_sim"
                res_ = requests.post(url_, json=data_)
                if res_.ok:
                    print("Ok")
                    print(res_.json())
                else:
                    print(res)

            #Fazer pedido de QOS para os hosts com prioridade low
            for j in range(0,len(list_hosts_min_priority)):
                data_={"source_ns":list_hosts_min_priority[j],"destination_ns":"192.168.2.7", "max_rate":"500"}
                print(data_)
                url_ = "http://127.0.0.1:5000/double_sim"
                res_ = requests.post(url_, json=data_)
                if res_.ok:
                    print("Ok")
                    print(res_.json())
                else:
                    print(res)
            if(intent.info=="Append"):
                print("Updated")
                msg="There are already policies with defined priorities"
            else:
                if(intent.info==""):
                    insert_intent=Insert(intent)
                    name,gw=insert_intent.insert_intent()
                    print(name)
                    print(gw)
                    msg="Done"
                    print("Inserted")
                else:
                    if(flag==0):
                        posi=intent.info.split(" ")
                        msg="Priority for this service previously set, changing"
                        print("Aqui")
                        print(lista[int(posi[-1])]['id'])
                        post = Intents.load(lista[int(posi[-1])]['id'])
                        post["Conditions"][0]["Constraints"][int(posi[0])]["Domains"][int(posi[1])]["Level"]=posi[2]
                        post.store()
                    else:
                        msg="Priority for this service previously set, changing"
            client = MessageBusClient(port=6666)
            client.run_in_thread()
            client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))

