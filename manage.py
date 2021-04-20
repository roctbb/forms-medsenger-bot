from flask import Flask
from models import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk

from config import *

app = Flask(__name__)
db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

sentry_sdk.init(
    dsn=SENTRY,
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.0,
)

db.init_app(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()
