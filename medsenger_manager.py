from medsenger_api import AgentApiClient
from config import *

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG, use_grpc=USE_GRPC, grpc_host=GRPC_HOST, sentry_dsn=SENTRY)