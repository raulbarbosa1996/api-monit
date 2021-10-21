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

def getMysqlConnection():
    return mysql.connector.connect(user='flask', host='0.0.0.0', port='4000', password='password', database='services_active',auth_plugin='mysql_native_password')


class Monitoring(Resource):

    def monitoring(self):
        m = GetHostsWithoutServices()
        hosts_list_wout_service=m.hosts_w_service()
        print(hosts_list_wout_service)
        url = "http://127.0.0.1:5000/monitoringInterfaces"
        response=requests.get(url=url)
        switchs_down=response.json()
        switchs_down=switchs_down['message']
        print(switchs_down)

        #url = "http://127.0.0.1:5500/sr/intents"
        #response=requests.get(url=url)
        #print(response.json())
        list_hosts={}
        list_of_list_hosts=[]
        for key, value in switchs_down.items():
            if value:
                switch=str(key).split(":")[-1]
                for i in range(0,len(value)):
                    host=value[0].split(":")[-1]
                    print(host)
                    try:
                        db = getMysqlConnection()
                        sqlstr = "SELECT Switch_src, Switch_dst,Host_src,Host_dst from service_active where Host_src='"+host+"' or Host_dst='"+host+"'"
                        print(sqlstr)
                        cur = db.cursor()
                        cur.execute(sqlstr)
                        output_json = cur.fetchall()
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
                                            print(type(value))
                                            for l in range(0,len(value)):
                                                for key, value in value[l].items():
                                                    port_switch=key.split(":")[-1]
                                                    #print(port_switch)
                                                    if(port_switch!=host and int(port_switch) in hosts_list_wout_service):
                                                        print(port_switch)


                        #list_hosts["Host_dst"] = output_json[0][1]
                        print(list_of_list_hosts)
                        #acess[t]=output_json[0][0]
                    except Exception as e:
                        print("Error in SQL:\n", e)
                        auxiliar=1
                    finally:
                        db.close()






