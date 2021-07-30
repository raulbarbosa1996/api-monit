from models import Intents
from types import SimpleNamespace
import json
import argparse

class Priority:

    def __init__(self):
        self.list = []
        self.host = []
        self.priority = []

    def get_all_prioritys(self):
        intents = Intents.all()
        response_data = []
        for intent in intents:
            cond=[]
            for con in intent.Conditions:
                constraints=[]
                if(con.Policy!="Priority"):
                    continue
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
                        self.host.append(Domain.Domain)
                        self.priority.append(Domain.Level)
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
            self.list.append(d)

        return self.host,self.priority,self.list