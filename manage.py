from celery import Celery
from flask import Flask
from models import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from commands import MigrateLegacyStructure, ReinitTasks
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
from managers.AlgorithmsManager import AlgorithmsManager
from managers.ContractsManager import ContractManager
from managers.FormManager import FormManager
from managers.MedicineManager import MedicineManager
from managers.ReminderManager import ReminderManager
from managers.TimetableManager import TimetableManager
from managers.MedicineTemplateManager import MedicineTemplateManager
from medsenger_api import AgentApiClient

from config import *

if PRODUCTION:
    sentry_sdk.init(
        dsn=SENTRY,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0,
    )

app = Flask(__name__)
db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

db.init_app(app)

migrate = Migrate(app, db)

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('migrate_to_complex_algs', MigrateLegacyStructure)
manager.add_command('reinit_tasks', ReinitTasks)

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
contract_manager = ContractManager(medsenger_api, db)
form_manager = FormManager(medsenger_api, db)
medicine_manager = MedicineManager(medsenger_api, db)
reminder_manager = ReminderManager(medsenger_api, db)
timetable_manager = TimetableManager(medicine_manager, form_manager, reminder_manager, medsenger_api, db)
algorithm_manager = AlgorithmsManager(medsenger_api, db)
medicine_template_manager = MedicineTemplateManager(medsenger_api, db)



if __name__ == '__main__':
    manager.run()
