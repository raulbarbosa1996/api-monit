import json
from types import SimpleNamespace


class GetDataForPath:
    def __init__(self, data):
        self.intent = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


    def getData(self):
        cond=self.intent.Conditions
        for i in range(0,len(cond)):
            constr=cond[i].Constraints
            for j in range(0,len(constr)):
                domains=constr[j].Domains
                for x in range(0,len(domains)):
                    return domains[x].Source, domains[x].Destination