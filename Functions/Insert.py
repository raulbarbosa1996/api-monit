from models import Intents


class Insert:
    def __init__(self, intent):
        self.intent = intent


    def insert_intent(self):
        post=Intents(IntentType=self.intent.IntentType,Intent_State=self.intent.Intent_State,Intent_Target=self.intent.Intent_Target)
        cond=self.intent.Conditions
        Name=''
        Gw=''
        for i in range(0,len(cond)):
            post.Conditions.append(Policy=cond[i].Policy)
            constr=cond[i].Constraints
            for j in range(0,len(constr)):
                list_constraints=[]
                try:
                    list_constraints.append(constr[j].Level)
                except:
                    list_constraints.append(None)
                try:
                    list_constraints.append(constr[j].Bool)
                except:
                    list_constraints.append(None)

                post.Conditions[i].Constraints.append(Level=list_constraints[0],Bool=list_constraints[1])
                try:
                    domains=constr[j].Domains
                    for l in range(0,len(domains)):
                        list_domains=[]
                        try:
                            list_domains.append(domains[l].Action)
                            Name=domains[l].Action
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Traffic_Type)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Period)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Domain)
                            Gw=domains[l].Domain
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Limit)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Source)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Destination)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Level)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Bool)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Name)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Acess)
                        except:
                            list_domains.append(None)
                        try:
                            list_domains.append(domains[l].Performance)
                        except:
                            list_domains.append(None)
                        print(list_domains)
                        post.Conditions[i].Constraints[j].Domains.append(Action=list_domains[0],Traffic_Type=list_domains[1],Period=list_domains[2],Domain=list_domains[3],Limit=list_domains[4],Source=list_domains[5],Destination=list_domains[6],Level=list_domains[7],Bool=list_domains[8],Name=list_domains[9],Acess=list_domains[10],Performance=list_domains[11])
                except:
                    print("No Domains")
        post.store()
        return Name,Gw

