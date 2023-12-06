from flask import Flask
from flask_compress import Compress
from flask_cors import CORS
from flask_migrate import Migrate
from managers import *
from infrastructure import *

from config import *

app = Flask(__name__)

CORS(app)
Compress(app)

db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db.init_app(app)

migrate = Migrate(app, db)

contract_manager = ContractManager()
form_manager = FormManager()
medicine_manager = MedicineManager()
reminder_manager = ReminderManager()
timetable_manager = TimetableManager(medicine_manager, form_manager, reminder_manager)
examination_manager = ExaminationManager()
algorithm_manager = AlgorithmManager()
medicine_template_manager = MedicineTemplateManager()
