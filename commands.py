from config import *
from managers.AlgorithmsManager import AlgorithmsManager
from medsenger_api import AgentApiClient
import flask

from managers.FormManager import FormManager
from managers.MedicineManager import MedicineManager
from managers.ReminderManager import ReminderManager
from managers.TimetableManager import TimetableManager
from managers.ContractsManager import ContractManager
from models import db
from flask_script import Command


class MigrateLegacyStructure(Command):
    "legacy db structure migration"

    def run(self):
        medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
        algorithm_manager = AlgorithmsManager(medsenger_api, db)
        algorithm_manager.__migrate__()


class ReinitTasks(Command):
    def run(self):
        medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
        form_manager = FormManager(medsenger_api, db)
        medicine_manager = MedicineManager(medsenger_api, db)
        reminder_manager = ReminderManager(medsenger_api, db)
        contract_manager = ContractManager(medsenger_api, db)
        timetable_manager = TimetableManager(medicine_manager, form_manager, reminder_manager, contract_manager,
                                             medsenger_api, db)
        timetable_manager.update_daily_tasks(flask.current_app)
        print("done tasks")
