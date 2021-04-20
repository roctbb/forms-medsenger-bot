from config import *
from managers.AlgorithmsManager import AlgorithmsManager
from medsenger_api import AgentApiClient
from models import db
from flask_script import Command

class MigrateLegacyStructure(Command):
    "prints hello world"

    def run(self):
        medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
        algorithm_manager = AlgorithmsManager(medsenger_api, db)
        algorithm_manager.__migrate__()

