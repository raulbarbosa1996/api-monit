

from Functions.Insert import Insert

from Functions.GetPrioritys import Priority
from models import Intents
from mycroft_bus_client import MessageBusClient, Message
import json
import requests
from types import SimpleNamespace


from flask import  jsonify, request, make_response

from flask_restful import Resource

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

class IntentsResource(Resource):
    def get(self):
        intents = Intents.all()
        response_data = []
        for intent in intents:
            cond=[]
            for con in intent.Conditions:
                constraints=[]
                for constr in con.Constraints:
                    Domains=[]
                    for Domain in constr.Domains:
                        dom={
                            "Domain": Domain.Domain,
                            "Action": Domain.Action,
                            "Traffic_Type": Domain.Traffic_Type,
                            "Period": Domain.Period,
                            "Limit": Domain.Limit,
                            "Source": Domain.Source,
                            "Destination": Domain.Destination,
                            "Level":Domain.Level,
                            "Bool":Domain.Bool
                        }
                        Domains.append(dom)

                    constra={
                        "Domains": Domains,
                        "Level": constr.Level,
                        "Bool": constr.Bool,
                    }
                    constraints.append(constra)
                const={
                    "Policy": con.Policy,
                    "Constraints":constraints
                }

                cond.append(const)
            d = {
                'id': intent.id,
                'Intent_Target': intent.Intent_Target,
                'IntentType': intent.IntentType,
                'Conditions': cond,
                'Intent_State': intent.Intent_State
            }
            response_data.append(d)
        return make_response(jsonify(response_data), 200)

    def post(self):
        data = request.json
        intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        print(intent)
        #Tenho que receber a var info

        if(intent.info!="Append"):
            insert_intent=Insert(intent)
            name,gw=insert_intent.insert_intent()
            print(name)
            print(gw)
            msg="Done"

        else:
            print("Updated")
            msg="There are already policies with defined priorities"
        print("Inserted")
        client = MessageBusClient(port=6666)
        client.run_in_thread()
        client.emit(Message('speak', data={'utterance': msg},context={'context':'switch'}))





