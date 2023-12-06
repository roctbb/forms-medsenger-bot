from celery import Celery
from medsenger_api import AgentApiClient
from config import *
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

if PRODUCTION:
    sentry_sdk.init(
        dsn=SENTRY,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0,
    )

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG, use_grpc=USE_GRPC, grpc_host=GRPC_HOST,
                               sentry_dsn=SENTRY)
