from manage import *
from managers.ContractsManager import ContractManager
from medsenger_api import AgentApiClient
from helpers import *

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID,  API_DEBUG)
contract_manager = ContractManager(medsenger_api, db)

@app.route('/')
@verify_args
def index():
    return "Waiting for the thunder"

# monitoring and common api

@app.route('/status', methods=['POST'])
@verify_json
def status():
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": contract_manager.get_active_ids()
    }

    return jsonify(answer)

@app.route('/order', methods=['POST'])
@verify_json
def order():
    pass

# contract management api

@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    contract_manager.add_contract(contract_id)
    return "ok"


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    contract_manager.remove_contract(contract_id)
    return "ok"

@app.route('/actions', methods=['POST'])
@verify_json
def actions(data):
    return []

# settings and views

@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    contract = contract_manager.get_contract(args.get('contract_id'))
    urls = {
        "load": medsenger_api.ajax_url('/api/get_patient', contract.id, contract.agent_token)
    }
    return render_template('settings.html', urls=urls)

@app.route('/settings', methods=['POST'])
@verify_args
def post_settings(args, form):
    pass

@app.route('/form', methods=['GET'])
@verify_args
def get_form(args, form):
    pass

@app.route('/form', methods=['POST'])
@verify_args
def post_form(args, form):
    pass

# settings api
@app.route('/api/get_patient', methods=['GET'])
@only_doctor_args
def get_data(args, form):
    contract_id = args.get('contract_id')

    if not contract_id:
        abort(422)

    patient = contract_manager.get_patient(contract_id)
    contract = contract_manager.get_contract(contract_id)
    info = medsenger_api.get_patient_info(contract_id)

    return jsonify({
        "patient": patient.as_dict(),
        "contract": contract.as_dict(native=True),
        "info": info
    })



app.run(HOST, PORT, debug=API_DEBUG)