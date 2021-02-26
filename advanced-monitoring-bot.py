from manage import *
from managers.AlgorithmsManager import AlgorithmsManager
from managers.ContractsManager import ContractManager
from managers.FormManager import FormManager
from managers.MedicineManager import MedicineManager
from managers.TimetableManager import TimetableManager
from medsenger_api import AgentApiClient
from helpers import *
from models import Form

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
contract_manager = ContractManager(medsenger_api, db)
form_manager = FormManager(medsenger_api, db)
medicine_manager = MedicineManager(medsenger_api, db)
timetable_manager = TimetableManager(medicine_manager, form_manager, medsenger_api, db)
algorithm_manager = AlgorithmsManager(medsenger_api, db)


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

    contract_manager.add(contract_id)
    return "ok"


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    contract_manager.remove(contract_id)
    return "ok"


@app.route('/actions', methods=['POST'])
@verify_json
def actions(data):
    return []


# settings and views

@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('settings', contract, medsenger_api.get_categories())


@app.route('/form/<form_id>', methods=['GET'])
@verify_args
def form_page(args, form, form_id):
    form_manager.calculate_deadline(form_manager.get(form_id).timetable)
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('form', contract, medsenger_api.get_categories(), form_id)


# settings api
@app.route('/api/settings/get_patient', methods=['GET'])
@only_doctor_args
def get_data(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    patient = contract.patient.as_dict()
    patient["info"] = medsenger_api.get_patient_info(contract_id)
    patient["current_contract"] = contract.as_dict()

    return jsonify(patient)


@app.route('/api/settings/get_templates', methods=['GET'])
@only_doctor_args
def get_templates(args, form):
    templates = {
        "forms": form_manager.get_templates_as_dicts(),
        "medicines": medicine_manager.get_templates_as_dicts(),
        "algorithms": algorithm_manager.get_templates_as_dicts()
    }

    return jsonify(templates)


@app.route('/api/settings/form', methods=['POST'])
@only_doctor_args
def create_form(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    form = form_manager.create_or_edit(request.json, contract)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@app.route('/api/settings/delete_form', methods=['POST'])
@only_doctor_args
def delete_form(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    result = form_manager.remove(request.json.get('id'), contract)

    if result:
        return jsonify({
            "deleted_id": result
        })
    else:
        abort(404)


@app.route('/api/settings/medicine', methods=['POST'])
@only_doctor_args
def create_medicine(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    form = medicine_manager.create_or_edit(request.json, contract)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@app.route('/api/settings/delete_medicine', methods=['POST'])
@only_doctor_args
def delete_medicine(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    result = medicine_manager.remove(request.json.get('id'), contract)

    if result:
        return jsonify({
            "result": "ok",
            "deleted_id": result
        })
    else:
        abort(404)


@app.route('/api/settings/algorithm', methods=['POST'])
@only_doctor_args
def create_algorithm(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    form = algorithm_manager.create_or_edit(request.json, contract)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@app.route('/api/settings/delete_algorithm', methods=['POST'])
@only_doctor_args
def delete_algorithm(args, form):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    result = algorithm_manager.remove(request.json.get('id'), contract)

    if result:
        return jsonify({
            "result": "ok",
            "deleted_id": result
        })
    else:
        abort(404)


@app.route('/api/form/<form_id>', methods=['GET'])
@verify_args
def get_form(args, form, form_id):
    form = form_manager.get(form_id)

    if form.contract_id != int(args.get('contract_id')) and not form.is_template:
        abort(401)

    return jsonify(form.as_dict())


@app.route('/api/form/<form_id>', methods=['POST'])
@verify_args
def post_form(args, form, form_id):
    form = form_manager.get(form_id)
    data = request.json
    contract_id = int(args.get('contract_id'))

    if form.contract_id != contract_id and not form.is_template:
        abort(401)

    if form_manager.submit(data, form_id, contract_id):
        contract = contract_manager.get(contract_id)
        algorithm_manager.examine(contract, form)

        return jsonify({
            "result": "ok",
        })
    else:
        abort(404)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    timetable_manager.run(app)
    app.run(HOST, PORT, debug=API_DEBUG)
