from models import Intents
from types import SimpleNamespace
import json
import argparse
args = argparse.Namespace()
class GetServicesHosts:
    def __init__(self, intent):
        self.intent = intent
        self.conflict = False
        self.info=''

    def getServicesHosts(self,lista):
        condition_intent=self.intent.Conditions
        for m in range(0,len(condition_intent)):
            Policy=condition_intent[m].Policy
            for i in range(0,len(lista)):
                Cond=lista[i].Conditions
                for j in range(0,len(Cond)):
                    print(Policy)
                    if(1):
                        Constraints_list= Cond[j].Constraints
                        Constraints_intent=condition_intent[m].Constraints
                        if(Policy=='CreateService'):
                            contr=0
                            for q in range(0,len(Constraints_intent)):
                                for p in range (0,len(Constraints_list)):
                                    try:
                                        for r in range(0,len(Constraints_intent[q].Domains)):
                                            for t in range (0,len(Constraints_list[p].Domains)):
                                                if(Constraints_list[p].Domains[t].Bool):
                                                    Constraints_list[p].Domains[t].Acess.append("192.168.2.107")
                                                return Constraints_list[p].Domains[t].Acess

                                    except:
                                        print("")


    def get_sameTarget(self):
        #Obter o target do intent a comparar
        Intent_Target=self.intent.Intent_Target
        #Obter os intents com o mesmo target

        intents = Intents.intents_by_Intent_Target[Intent_Target.lower()]

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
                            "Bool":Domain.Bool,
                            "Name": Domain.Name,
                            "Performance": Domain.Performance,
                            "Acess": Domain.Acess,
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
            str=json.dumps(d)
            response_data.append(json.loads(str, object_hook=lambda d: SimpleNamespace(**d)))
        try:
            if(not response_data and self.intent.Action=="Update"):
                print("Conflito-Rede nao implementado")
                return True,self.info
        except:
            print("Sem ação")

        return self.getServicesHosts(response_data)
