from flask import Blueprint
from flask_restful import Api

from resources.CreateService import CreateService
from resources.Stats import Stats
from resources.Topology import Topology
from resources.IntentResource import IntentsResource
from resources.Prioritys import Prioritys
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

api.add_resource(Topology,'/topology')
api.add_resource(Stats,'/NetworkOtimization')
api.add_resource(IntentsResource, '/intents')
api.add_resource(Prioritys, '/priority')
api.add_resource(CreateService, '/CreateService')