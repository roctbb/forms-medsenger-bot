from models import *
from manage import *
from tqdm import tqdm

with app.app_context():
    medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG, use_grpc=USE_GRPC, grpc_host=GRPC_HOST,
                                   sentry_dsn=SENTRY)
    manager = MedicineManager(medsenger_api, db)

    for medicine in tqdm(Medicine.query.all()):
        medicine_manager.fill_atx(medicine)

    db.session.commit()
