from flask import Blueprint

from manage import *
from helpers import *
from decorators import verify_request
from tasks import tasks

api_blueprint = Blueprint('api_endpoints', __name__, template_folder='templates')


# settings api
@api_blueprint.route('/api/settings/get_patient', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def get_data(args, form, contract):
    patient = contract.patient.as_dict()
    patient["info"] = medsenger_api.get_patient_info(contract.id)
    patient["current_contract"] = contract.as_dict()

    return jsonify(patient)


@api_blueprint.route('/api/settings/get_patient_data', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_open_data(args, form, contract):
    patient = contract.patient.as_dict()

    return jsonify({
        "medicines": patient["medicines"],
        "patient_medicines": patient["patient_medicines"],
        "canceled_medicines": patient["canceled_medicines"],
        "canceled_patient_medicines": patient["canceled_patient_medicines"],
    })


@api_blueprint.route('/api/settings/get_templates', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def get_templates(args, form, contract):
    templates = {
        "forms": form_manager.get_templates_as_dicts(),
        "medicines": medicine_manager.get_templates_as_dicts(),
        "reminders": reminder_manager.get_templates_as_dicts(),
        "algorithms": algorithm_manager.get_templates_as_dicts(),
        "examinations": examination_manager.get_templates_as_dicts()
    }

    return jsonify(templates)


@api_blueprint.route('/api/settings/form', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def create_form(args, form, contract):
    form = form_manager.create_or_edit(request.json, contract)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@api_blueprint.route('/api/settings/delete_form', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def delete_form(args, form, contract):
    result = form_manager.remove(request.json.get('id'), contract)

    if result:
        return jsonify({
            "deleted_id": result
        })
    else:
        abort(404)


@api_blueprint.route('/api/settings/medicine', methods=['POST'])
@verify_request(contract_manager, 'patient')
def create_medicine(args, form, contract):
    form = medicine_manager.create_or_edit(request.json, contract)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@api_blueprint.route('/api/settings/medicine_history', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def edit_medicine_history(args, form, contract):
    form = medicine_manager.edit_history(request.json)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@api_blueprint.route('/api/settings/delete_medicine', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def delete_medicine(args, form, contract):
    medicine_manager.edit_history(request.json)
    result = medicine_manager.remove(request.json.get('id'), contract, request.json.get('deleted_by_patient'))

    if result:
        return jsonify({
            "result": "ok",
            "deleted_id": result
        })
    else:
        abort(404)


@api_blueprint.route('/api/settings/resume_medicine', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def resume_medicine(args, form, contract):
    medicine_manager.edit_history(request.json)
    result = medicine_manager.resume(request.json.get('id'), contract)

    if result:
        return jsonify({
            "result": "ok",
            "resumed_id": result
        })
    else:
        abort(404)


@api_blueprint.route('/api/settings/delete_reminder', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def delete_reminder(args, form, contract):
    result = reminder_manager.remove(request.json.get('id'), contract)

    if result:
        return jsonify({
            "deleted_id": result
        })
    else:
        abort(404)


@api_blueprint.route('/api/settings/reminder', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def create_reminder(args, form, contract):
    reminder = reminder_manager.create_or_edit(request.json, contract)

    if reminder:
        return jsonify(reminder.as_dict())
    else:
        abort(422)


@api_blueprint.route('/api/reminder/<reminder_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_reminder(args, form, contract, reminder_id):
    reminder = reminder_manager.get(reminder_id)

    if reminder.contract_id != int(args.get('contract_id')) and not reminder.is_template:
        abort(401)

    return jsonify(reminder.as_dict())


@api_blueprint.route('/api/reminder/<reminder_id>/set_state', methods=['POST'])
@verify_request(contract_manager, 'patient')
def set_reminder_state(args, form, contract, reminder_id):
    reminder = reminder_manager.get(reminder_id)
    data = request.json

    if reminder.contract_id != contract.id and not reminder.is_template:
        abort(401)

    if data['state'] == 'later':
        reminder_manager.set_next_date(reminder_id, contract, data['type'], data['count'])

    result = reminder_manager.set_state(reminder, data['state'])

    return jsonify(result)


@api_blueprint.route('/api/settings/algorithm', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def create_algorithm(args, form, contract):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    form = algorithm_manager.create_or_edit(request.json, contract)

    if form:
        return jsonify(form.as_dict())
    else:
        abort(422)


@api_blueprint.route('/api/settings/algorithms', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def save_algorithms(args, form, contract):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    for alg in request.json:
        form = algorithm_manager.create_or_edit(alg, contract)
        if not form:
            abort(422)
    return 'ok'


@api_blueprint.route('/api/settings/delete_algorithm', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def delete_algorithm(args, form, contract):
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


@api_blueprint.route('/api/form/<form_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_form(args, form, contract, form_id):
    form = form_manager.get(form_id)

    if form.contract_id != int(args.get('contract_id')) and not form.is_template:
        abort(401)
    answer = form.as_dict()
    if args.get('source') == 'patient' or args.get('agent_token') == contract.patient_agent_token:
        answer['preview'] = False
    else:
        answer['preview'] = True

    return jsonify(answer)


@api_blueprint.route('/api/outsource_form/<form_id>', methods=['GET'])
def get_form_outsource(form_id):
    form = form_manager.get(form_id)
    answer = form.as_dict()
    return jsonify(answer)


@api_blueprint.route('/api/form/<form_id>', methods=['POST'])
@verify_request(contract_manager, 'patient')
def post_form(args, form, contract, form_id):
    form = form_manager.get(form_id)
    data = request.json
    contract_id = int(args.get('contract_id'))

    if form.contract_id != contract_id and not form.is_template:
        abort(401)

    submit_chain = tasks.submit_form.s(True, data, form_id, contract_id)
    submit_chain |= tasks.examine_form.s(form_id, contract_id)
    submit_chain |= tasks.examine_contract_tasks.s(form_id, contract_id)
    submit_chain.apply_async()

    return jsonify({
        "result": "ok",
    })


@api_blueprint.route('/api/outsource_form/<form_id>', methods=['POST'])
def post_outsource_form(form_id):
    form = form_manager.get(form_id)
    data = request.json

    result, action_name, custom_params = form_manager.get_integral_evaluation(None, data, form)

    return jsonify({
        "result": custom_params,
    })


@api_blueprint.route('/api/send_form/<form_id>', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def send_form(args, form, contract, form_id):
    form = form_manager.get(form_id)
    contract_id = int(args.get('contract_id'))

    form_manager.run(form, contract_id=contract_id, commit=False)

    return jsonify({
        "result": "ok",
    })


@api_blueprint.route('/api/medicine/<medicine_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_medicine(args, form, contract, medicine_id):
    medicine = medicine_manager.get(medicine_id)

    if medicine.contract_id != int(args.get('contract_id')) and not medicine.is_template:
        abort(401)

    return jsonify(medicine.as_dict())


@api_blueprint.route('/api/medicine/<medicine_id>/disable_notifications', methods=['POST'])
@verify_request(contract_manager, 'patient')
def disable_notifications(args, form, contract, medicine_id):
    medicine = medicine_manager.get(medicine_id)

    if medicine.contract_id != int(args.get('contract_id')):
        abort(401)
    medicine.notifications_disabled = True
    db.session.commit()

    return jsonify(medicine.as_dict())


@api_blueprint.route('/api/medicine/<medicine_id>/enable_notifications', methods=['POST'])
@verify_request(contract_manager, 'patient')
def enable_notifications(args, form, contract, medicine_id):
    medicine = medicine_manager.get(medicine_id)

    if medicine.contract_id != int(args.get('contract_id')):
        abort(401)
    medicine.notifications_disabled = False
    db.session.commit()

    return jsonify(medicine.as_dict())


@api_blueprint.route('/api/confirm-medicine', methods=['POST'])
@verify_request(contract_manager, 'patient')
def post_medicines(args, form, contract):
    data = request.json

    if data['custom']:
        medsenger_api.add_record(contract.id, 'medicine', data['medicine'], params=data['params'])
    else:
        medicine_manager.submit(data['medicine'], contract.id, params=data['params'])
        if contract.tasks and 'medicine-{}'.format(data['medicine']) in contract.tasks:
            medsenger_api.finish_task(contract.id, contract.tasks['medicine-{}'.format(data['medicine'])])

    return get_ui('done', contract, [], role='patient')


@api_blueprint.route('/api/medicine-template', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_medicine_template(args, form, contract):
    medicines = medicine_template_manager.get_clinic_templates(contract.clinic_id)
    return jsonify(medicines)


@app.route('/api/settings/examination', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def create_examination(args, form, contract):
    examination = examination_manager.create_or_edit(request.json, contract)

    if examination:
        return jsonify(examination.as_dict())
    else:
        abort(422)


@app.route('/api/settings/delete_examination', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def delete_examination(args, form, contract):
    result = examination_manager.remove(request.json.get('id'), contract)

    if result:
        return jsonify({
            "deleted_id": result
        })
    else:
        abort(404)


@app.route('/api/examination/<examination_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_examination(args, form, contract, examination_id):
    examination = examination_manager.get(examination_id)

    if examination.contract_id != int(args.get('contract_id')) and not examination.is_template:
        abort(401)
    answer = examination.as_dict()

    if examination.record_id:
        record = medsenger_api.get_record_by_id(contract.id, examination.record_id)
        answer['files'] = [record['attached_files']]

    return jsonify(answer)


@app.route('/api/examination/<examination_id>', methods=['POST'])
@verify_request(contract_manager, 'patient')
def post_examination(args, form, contract, examination_id):
    examination = examination_manager.get(examination_id)
    data = request.json

    if examination.contract_id != contract.id and not examination.is_template:
        abort(401)

    submit_chain = tasks.submit_examination.s(True, data['files'], examination_id, contract.id, data['date'])
    submit_chain.apply_async()

    return jsonify({
        "result": "ok",
    })


@app.route('/api/settings/get_examination_files/<examination_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_examination_files(args, form, contract, examination_id):
    contract_id = int(args.get('contract_id'))
    examination = examination_manager.get(examination_id)
    record = medsenger_api.get_record_by_id(contract_id, examination.record_id)

    files = []
    for file_info in record['attached_files']:
        file = medsenger_api.get_file(contract_id, file_info['id'])

        files.append({
            'base64': file['base64'],
            'type': file_info.get('type', 'text/plain'),
            'name': file_info['name']
        })
    return jsonify(files)
