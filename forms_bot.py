from manage import *
from managers.AlgorithmsManager import AlgorithmsManager
from managers.ContractsManager import ContractManager
from managers.FormManager import FormManager
from managers.MedicineManager import MedicineManager
from managers.TimetableManager import TimetableManager
from medsenger_api import AgentApiClient
from helpers import *
from models import Form, Algorithm

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
contract_manager = ContractManager(medsenger_api, db)
form_manager = FormManager(medsenger_api, db)
medicine_manager = MedicineManager(medsenger_api, db)
timetable_manager = TimetableManager(medicine_manager, form_manager, medsenger_api, db)
algorithm_manager = AlgorithmsManager(medsenger_api, db)


@app.route('/')
def index():
    return "Waiting for the thunder"


@app.route('/debug-sentry')
def trigger_error():
    try:
        division_by_zero = 1 / 0
    except Exception as e:
        log(e, True)
        abort(500)


# monitoring and common api

@app.route('/status', methods=['POST'])
@verify_json
def status(data):
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": contract_manager.get_active_ids()
    }

    return jsonify(answer)


@app.route('/order', methods=['POST'])
@verify_json
def order(data):
    pass


# contract management api

@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract_id = data.get('contract_id')
    clinic_id = data.get('clinic_id')
    if not contract_id:
        abort(422)

    contract = contract_manager.add(contract_id, clinic_id)

    params = data.get('params')
    print(params)
    if params:
        forms = params.get('forms')
        exclude_algorithms = params.get('exclude_algorithms', "").split(',')

        if forms:
            form_manager.clear(contract)
            algorithm_manager.clear(contract)
            medicine_manager.clear(contract)

            for template_id in forms.split(','):
                form = form_manager.attach(template_id, contract, params.get('form_timetable_{}'.format(template_id)))
                if form.algorithm_id and form.algorithm_id not in exclude_algorithms:
                    algorithm_manager.attach(form.algorithm_id, contract, params)

        algorithms = params.get('algorithms')

        if algorithms:
            for template_id in algorithms.split(','):
                algorithm_manager.attach(template_id, contract, params)

        medicines = params.get('medicines')

        if medicines:
            for template_id in medicines.split(','):
                medicine_manager.attach(template_id, contract, params.get('medicine_timetable_{}'.format(template_id)))

        custom_forms = filter(lambda x: "form_" in x and params.get(x), params.keys())
        for custom_form in custom_forms:
            try:
                form_id = int(custom_form.split('_')[1])

                form = form_manager.attach(form_id, contract, params.get('form_timetable_{}'.format(form_id)))

                if form.algorithm_id and form.algorithm_id not in exclude_algorithms:
                    algorithm_manager.attach(form.algorithm_id, contract, params)
            except:
                pass

        custom_medicines = filter(lambda x: "medicine_" in x and params.get(x), params.keys())
        for custom_medicine in custom_medicines:
            try:
                medicine_id = int(custom_medicine.split('_')[1])
                medicine_manager.attach(medicine_id, contract, params.get('medicine_timetable_{}'.format(medicine_id)))
            except:
                pass

        custom_algorithms = filter(lambda x: "algorithm_" in x and params.get(x), params.keys())
        for custom_algorithm in custom_algorithms:
            try:
                algorithm_id = int(custom_algorithm.split('_')[1])
                algorithm_manager.attach(algorithm_id, contract)
            except:
                pass

    return "ok"


@app.route('/hook', methods=['POST'])
@verify_json
def hook(data):
    contract_id = int(data.get('contract_id'))
    contract = contract_manager.get(contract_id)
    category_name = data.get('category_name')

    if algorithm_manager.hook(contract, category_name):
        return jsonify({
            "result": "ok",
        })
    else:
        abort(500)


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
    contract = contract_manager.get(data.get('contract_id'))
    forms = filter(lambda f: f.show_button, contract.forms)

    actions = [{'link': 'form/{}'.format(form.id), 'type': 'patient', 'name': form.button_title} for form in forms]

    return jsonify(actions)


@app.route('/compliance', methods=['POST'])
@verify_json
def compliance(data):
    contract = contract_manager.get(data.get('contract_id'))
    sent, done = contract.patient.count_month_compliance()
    return jsonify({"sent": sent, "done": done})


# settings and views

@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('settings', contract, medsenger_api.get_categories())


@app.route('/form/<form_id>', methods=['GET'])
@verify_args
def form_page(args, form, form_id):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('form', contract, medsenger_api.get_categories(), form_id)


@app.route('/graph', methods=['GET'])
@verify_args
def graph_page(args, form):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('graph', contract)

@app.route('/graph/<category_id>', methods=['GET'])
@verify_args
def graph_page_with_args(args, form, category_id):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('graph', contract, object_id=category_id)


@app.route('/medicine/<medicine_id>', methods=['GET'])
@verify_args
def medicine_page(args, form, medicine_id):
    contract = contract_manager.get(args.get('contract_id'))
    medicine_manager.submit(medicine_id, contract.id)

    if contract.tasks and 'medicine-{}'.format(medicine_id) in contract.tasks:
        medsenger_api.finish_task(contract.id, contract.tasks['medicine-{}'.format(medicine_id)])

    return get_ui('done', contract, [])


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


@app.route('/api/graph/categories', methods=['GET'])
@verify_args
def graph_categories(args, form):
    contract_id = args.get('contract_id')
    categories = medsenger_api.get_available_categories(contract_id)

    return jsonify(categories)


@app.route('/api/graph/group', methods=['POST'])
@verify_args
def graph_data(args, form):
    contract_id = args.get('contract_id')
    group = request.json
    answer = [medsenger_api.get_records(contract_id, category_name) for category_name in
              group['categories'] + ['medicine', 'symptom']]
    answer = list(filter(lambda x: x != None, answer))

    return jsonify(answer)


@app.route('/api/form/<form_id>', methods=['GET'])
@verify_args
def get_form(args, form, form_id):
    form = form_manager.get(form_id)

    if form.contract_id != int(args.get('contract_id')) and not form.is_template:
        abort(401)
    answer = form.as_dict()
    if args.get('source') == 'patient':
        answer['preview'] = False
    else:
        answer['preview'] = True

    return jsonify(answer)


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

        if contract.tasks and 'form-{}'.format(form_id) in contract.tasks:
            medsenger_api.finish_task(contract.id, contract.tasks['form-{}'.format(form_id)])

        return jsonify({
                "result": "ok",
            })
    else:
        abort(404)


@app.route('/confirm-medicine', methods=['GET'])
@verify_args
def medicines_page(args, form):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('confirm-medicine', contract, medsenger_api.get_categories())


@app.route('/api/confirm-medicine', methods=['POST'])
@verify_args
def post_medicines(args, form):
    contract_id = int(args.get('contract_id'))
    contract = contract_manager.get(contract_id)

    data = request.json

    if data['custom']:
        medsenger_api.add_record(contract_id, 'medicine', data['medicine'])
    else:
        medicine_manager.submit(data['medicine'], contract.id)
        if contract.tasks and 'medicine-{}'.format(data['medicine']) in contract.tasks:
            medsenger_api.finish_task(contract.id, contract.tasks['medicine-{}'.format(data['medicine'])])

        return get_ui('done', contract, [])


with app.app_context():
    db.create_all()


def tasks():
    timetable_manager.run(app)


if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
