from flask import Blueprint
from tasks import threader
from manage import *
from helpers import *
from decorators import verify_request
from tasks import tasks

medsenger_blueprint = Blueprint('medsenger_endpoints', __name__, template_folder='templates')


@medsenger_blueprint.route('/status', methods=['POST'])
@verify_request(contract_manager, 'backend')
def status(data):
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": contract_manager.get_active_ids()
    }

    return jsonify(answer)


@medsenger_blueprint.route('/order', methods=['POST'])
@verify_request(contract_manager, 'backend')
def order(data):
    contract_id = data.get('contract_id')
    contract = contract_manager.get(contract_id)

    print(f"Got order data {data}")

    if data['order'] == 'need_conclusion':
        medicines = list(filter(lambda m: not m.canceled_at, contract.medicines))
        medicines = list(map(lambda m: m.title + (f' {m.dose}' if m.dose else ''), medicines))
        canceled_medicines = list(filter(lambda m: m.canceled_at, contract.medicines))
        canceled_medicines = list(map(lambda m: m.title + (f' {m.dose}' if m.dose else ''), canceled_medicines))

        params = {
            'medicines': medicines,
            'canceled_medicines': canceled_medicines
        }
        threader.async_order.delay(contract.id, 'conclusion_params', None, params)
        return 'ok'

    if data['order'] in ['get_medicines', 'get_compliance']:
        from_timestamp = data['params'].get('from_timestamp')
        to_timestamp = data['params'].get('to_timestamp')

        from_date = datetime.fromtimestamp(from_timestamp) if from_timestamp else None
        to_date = datetime.fromtimestamp(to_timestamp) if to_timestamp else None

        if data['order'] == 'get_medicines':
            medicines = medicine_manager.get_attached_medicines(contract.patient, from_date, to_date)
            return jsonify([medicine.as_dict() for medicine in medicines])
        if data['order'] == 'get_compliance':
            ordered_compliance = {
                "medicines": [],
                "forms": []
            }

            medicines = medicine_manager.get_attached_medicines(contract)
            forms = contract.forms

            def get_obj_compliance(obj):
                req, done = obj.count_compliance(start_date=from_date, end_date=to_date)
                return {
                    "id": obj.id,
                    "title": obj.title,
                    "done": done,
                    "requested": req
                }

            for medicine in medicines:
                ordered_compliance['medicines'].append(get_obj_compliance(medicine))
            for form in forms:
                ordered_compliance['forms'].append(get_obj_compliance(form))

            return jsonify(ordered_compliance)
        return 'ok'

    if data['order'] == 'new_timezone':
        contract_manager.actualize_timezone(contract, commit=True)

    if data['order'] in ['create_form', 'create_medicine', 'attach_form', 'detach_form', 'detach_medicine', 'remove_form', 'attach_algorithm', 'detach_algorithm', 'set_params']:
        if data['order'] == 'create_form':
            form = form_manager.create_or_edit(data['params'], contract)

            if form:
                tasks.request_cache_update.delay(contract.id)
                return str(form.id)
            else:
                abort(422)

        if data['order'] == 'create_medicine':
            medicine = medicine_manager.create_or_edit(data['params'], contract)

            if medicine:
                tasks.request_cache_update.delay(contract.id)
                return str(medicine.id)
            else:
                abort(422)

        if data['order'] == 'attach_form':
            form = form_manager.attach(data['params'].get('template_id'), contract)

            if not form:
                abort(422)

        if data['order'] == 'detach_form':
            form_manager.detach(data['params'].get('template_id'), contract)

        if data['order'] == 'detach_medicine':
            if data['params'].get('id'):
                medicine_manager.remove(data['params'].get('id'), contract, data['params'].get('bypass_notifications'))
            if data['params'].get('template_id'):
                medicine_manager.detach(data['params'].get('template_id'), contract)
            if data['params'].get('atx'):
                medicine_manager.detach_by_atx(data['params'].get('atx'), contract)

        if data['order'] == 'remove_form':
            form_manager.remove(data['params'].get('id'), contract)

        if data['order'] == 'attach_algorithm':
            form = algorithm_manager.attach(data['params'].get('template_id'), contract)

            if not form:
                abort(422)

        if data['order'] == 'detach_algorithm':
            algorithm_manager.detach(data['params'].get('template_id'), contract)

        if data['order'] == 'set_params':
            algorithm_manager.set_params(contract, data['params'])

        tasks.request_cache_update.delay(contract.id)
        return "ok"

    if data['order'] == 'get_params':
        return jsonify(algorithm_manager.search_params(contract))

    return "not found"


# contract management api

@medsenger_blueprint.route('/init', methods=['POST'])
@verify_request(contract_manager, 'backend')
def init(data):
    contract_id = data.get('contract_id')
    clinic_id = data.get('clinic_id')

    if not contract_id:
        abort(422)

    print("got init payload:", data)

    contract, is_new = contract_manager.add(contract_id, clinic_id)

    params = data.get('params')

    if params:
        custom_records = filter(lambda x: "record_" in x and params.get(x), params.keys())
        for record_selector in custom_records:
            parts = record_selector.lstrip("record_").split('|')

            try:
                record_category = parts[0]
                value = params.get(record_selector)

                if len(parts) == 2:
                    record_transformer = parts[1]

                    if record_transformer == "week_to_date":
                        value = int(value)
                        value = (datetime.now() - timedelta(days=((value - 1) * 7 + 3))).strftime('%Y-%m-%d')

                medsenger_api.add_record(contract_id, record_category, value)

            except Exception as e:
                log(e)

        forms = params.get('forms')
        exclude_algorithms = params.get('exclude_algorithms', "").split(',')

        if forms:
            if not is_new:
                form_manager.clear(contract)
                algorithm_manager.clear(contract)
                medicine_manager.clear(contract)

            for template_id in forms.split(','):
                form = form_manager.attach(template_id, contract, {
                    "timetable": params.get('form_timetable_{}'.format(template_id)),
                    "message": params.get('form_message_{}'.format(template_id)),
                    "times": params.get('form_times_{}'.format(template_id)),
                })

                if form.algorithm_id and str(form.algorithm_id) not in exclude_algorithms:
                    algorithm_manager.attach(form.algorithm_id, contract, params)

        print(gts() + f"attaching reminders")
        reminders = params.get('reminders')
        if reminders:
            for template_id in reminders.split(','):
                reminder_manager.attach(template_id, contract)

        print(gts() + f"attaching algorithms")
        algorithms = params.get('algorithms')
        if algorithms:
            for template_id in algorithms.split(','):
                algorithm_manager.attach(template_id, contract, params)

        print(gts() + f"attaching medicines")
        medicines = params.get('medicines')
        if medicines:
            for template_id in medicines.split(','):
                medicine_manager.attach(template_id, contract, params.get('medicine_timetable_{}'.format(template_id)))

        print(gts() + f"attaching custom forms")
        custom_forms = filter(lambda x: "form_" in x and params.get(x), params.keys())
        for custom_form in custom_forms:
            try:
                part = custom_form.split('_')[1]
                if not part.isnumeric():
                    continue

                form_id = int(part)

                form = form_manager.attach(form_id, contract, {
                    "timetable": params.get('form_timetable_{}'.format(form_id)),
                    "message": params.get('form_message_{}'.format(form_id)),
                    "times": params.get('form_times_{}'.format(form_id)),
                })

                if form.algorithm_id and str(form.algorithm_id) not in exclude_algorithms:
                    algorithm_manager.attach(form.algorithm_id, contract, params)
            except Exception as e:
                log(e)

        print(gts() + f"attaching custom medicines")
        custom_medicines = filter(lambda x: "medicine_" in x and params.get(x), params.keys())
        for custom_medicine in custom_medicines:
            try:
                part = custom_medicine.split('_')[1]
                if not part.isnumeric():
                    continue
                medicine_id = int(part)
                medicine_manager.attach(medicine_id, contract, params.get('medicine_timetable_{}'.format(medicine_id)))
            except Exception as e:
                log(e)

        print(gts() + f"attaching custom algorithms")
        custom_algorithms = filter(lambda x: "algorithm_" in x and params.get(x), params.keys())
        for custom_algorithm in custom_algorithms:
            try:
                part = custom_algorithm.split('_')[1]
                if not part.isnumeric():
                    continue
                algorithm_id = int(part)
                algorithm_manager.attach(algorithm_id, contract)
            except Exception as e:
                print(e)

        if params.get('examinations_deadline'):
            print(gts() + f"setting examinations")
            examinations_deadline = datetime.strptime(params.get('examinations_deadline'), '%Y-%m-%d')
            medsenger_api.add_record(contract_id, 'examinations_deadline', params.get('examinations_deadline'))
            has_examinations = False

            examinations = params.get('examinations')
            if examinations:
                for template_id in examinations.split(','):
                    examination_manager.attach(template_id, contract, examinations_deadline, False)
                    has_examinations = True

            custom_examinations = filter(lambda x: "examination_" in x and params.get(x), params.keys())
            for custom_examination in custom_examinations:
                try:
                    part = custom_examination.split('_')[1]
                    if not part.isnumeric():
                        continue
                    examination_id = int(part)

                    examination_manager.attach(examination_id, contract, examinations_deadline, False)
                    has_examinations = True
                except Exception as e:
                    log(e)

            custom_examination_groups = filter(lambda x: "examination_group_" in x and params.get(x), params.keys())
            for custom_examination_group in custom_examination_groups:
                try:
                    part = custom_examination_group.split('_')[2]
                    if not part.isnumeric():
                        continue
                    examination_group_id = int(part)

                    examination_manager.attach_group(examination_group_id, contract, examinations_deadline, False)
                    has_examinations = True
                except Exception as e:
                    log(e)

            if has_examinations:
                medsenger_api.send_message(contract.id,
                                           "Врач назначил Вам обследования. Их необходимо загрузить до <b>{}</b>.\n Для просмотра списка и загрузки результатов нажмите на кнопку:"
                                           .format(examinations_deadline.strftime('%d.%m.%Y')),
                                           only_patient=True, action_link='/examinations-list',
                                           action_name='Обследования', action_big=True)
                medsenger_api.send_message(contract.id,
                                           "Пациенту назначены обследования. Для просмотра списка и результатов нажмите на кнопку:"
                                           .format(examinations_deadline.strftime('%d.%m.%Y')),
                                           only_doctor=True, action_link='/examination-manager',
                                           action_name='Обследования', action_big=True)

    return "ok"


@medsenger_blueprint.route('/hook', methods=['POST'])
@verify_request(contract_manager, 'backend')
def hook(data):
    contract_id = int(data.get('contract_id'))
    category_names = data.get('category_names')
    tasks.examine_hook.s(contract_id, category_names).apply_async()
    return jsonify({
        "result": "ok",
    })


@medsenger_blueprint.route('/remove', methods=['POST'])
@verify_request(contract_manager, 'backend')
def remove(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    contract_manager.remove(contract_id)

    return "ok"


@medsenger_blueprint.route('/actions', methods=['POST'])
@verify_request(contract_manager, 'backend')
def actions(data):
    print(f"asked for actions for contract {data.get('contract_id')}")
    contract = contract_manager.get(data.get('contract_id'))
    forms = filter(lambda f: f.show_button, contract.forms)

    actions = [{'link': 'form/{}'.format(form.id), 'type': 'patient', 'name': form.button_title, 'id': form.id} for form
               in forms]

    return jsonify(actions)


@medsenger_blueprint.route('/params', methods=['POST'])
@verify_request(contract_manager, 'backend')
def params(data):
    print(f"asked for actions for params {data.get('contract_id')}")
    contract = contract_manager.get(data.get('contract_id'))
    return jsonify(algorithm_manager.search_params(contract))


@medsenger_blueprint.route('/params', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def get_params(args, data, contract):
    return jsonify(algorithm_manager.search_params(contract))


@medsenger_blueprint.route('/compliance', methods=['POST'])
@verify_request(contract_manager, 'backend')
def compliance(data):
    print(f"asked for compliance for params {data.get('contract_id')}")
    contract = contract_manager.get(data.get('contract_id'))
    sent, done = contract.patient.count_week_compliance()
    return jsonify({"sent": sent, "done": done})


@medsenger_blueprint.route('/message', methods=['POST'])
@verify_request(contract_manager, 'backend')
def message(data):
    return "ok"
