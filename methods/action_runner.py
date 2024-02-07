from helpers import *
from copy import deepcopy
import requests
import time
import re
from infrastructure import medsenger_api, db
from methods.hooks import *


def run_action(action, contract, descriptions, algorithm, record_ids=[]):
    from managers import ContractManager, FormManager, MedicineManager, AlgorithmManager, ReminderManager

    form_manager = FormManager()
    medicine_manager = MedicineManager()
    algorithm_manager = AlgorithmManager()

    has_message_to_patient = False
    report = ""
    if action['params'].get('send_report') and descriptions:
        report = '<br><br><ul>' + ''.join(
            ["<li>{}</li>".format(description) for description in descriptions]) + "</ul>"

    if action['type'] == 'change_step':
        remove_hooks_before_deletion(algorithm)
        AlgorithmManager().change_step(algorithm, action['params']['target'])
        create_hooks_after_creation(algorithm)

    if action['type'] == 'send_addition':
        for record_id in record_ids:
            params = {
                "algorithm_id": algorithm.id,
                "comment": "Помечено алгоритмом"
            }

            try:
                params.update(json.loads(action['params']['json_params']))
            except Exception as e:
                log(e, False)

            medsenger_api.send_addition(contract.id, record_id, params)

    if action['type'] == 'set_info_materials':
        medsenger_api.set_info_materials(contract.id, action['params']['materials'])

    if action['type'] == 'order':
        order = action['params'].get('order')
        agent_id = action['params'].get('agent_id')
        params = deepcopy(action['params'].get('order_params', {}))

        if action['params'].get('send_report'):
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except:
                    params = {}

            params["message"] = params.get("message", "") + report

        threader.async_order.delay(contract.id, order, agent_id, params)

    if action['type'] == 'patient_public_attachment':
        criteria = action['params'].get('criteria')
        comment = action['params'].get('text')
        info = medsenger_api.get_patient_info(contract.id)

        attachments = []

        for file in info['public_attachments']:
            if criteria in file.get('name').lower():
                attachments.append({'public_attachment_id': file.get('id')})

        if attachments:
            has_message_to_patient = True
            medsenger_api.send_message(contract.id, comment,
                                       only_patient=True,
                                       action_deadline=int(time.time()) + 60 * 60, attachments=attachments)

    if action['type'] == 'send_file_by_link':
        link = action['params'].get('link')
        text = action['params'].get('text')

        if link:
            try:
                answer = requests.get(link)
                if "Content-Disposition" in answer.headers.keys():
                    fname = re.findall("filename=(.+)", answer.headers["Content-Disposition"])[0]
                else:
                    fname = link.split("/")[-1]
                has_message_to_patient = True
                medsenger_api.send_message(contract.id, text, only_patient=True,
                                           attachments=[medsenger_api.prepare_binary(fname, answer.content)])

            except Exception as e:
                log(e, False)

    if action['type'] == 'patient_message':
        has_message_to_patient = True
        if action['params'].get('add_action'):
            action_name = action['params'].get('action_name')
            action_link = action['params'].get('action_link')
        else:
            action_name = None
            action_link = None

        if action['params'].get('add_deadline') and action['params'].get('action_deadline'):
            action_deadline = time.time() + int(action['params'].get('action_deadline')) * 60 * 60
        else:
            action_deadline = None

        is_urgent = action['params'].get('is_urgent')
        is_warning = action['params'].get('is_warning')

        if is_warning:
            is_urgent = "warning"

        medsenger_api.send_message(contract.id, action['params']['text'] + report,
                                   only_patient=True, action_name=action_name, action_link=action_link,
                                   is_urgent=is_urgent,
                                   action_deadline=action_deadline)
    if action['type'] == 'doctor_message':
        if action['params'].get('add_action'):
            action_name = action['params'].get('action_name')
            action_link = action['params'].get('action_link')
        else:
            action_name = None
            action_link = None

        if action['params'].get('add_deadline') and action['params'].get('action_deadline'):
            action_deadline = time.time() + int(action['params'].get('action_deadline')) * 60 * 60
        else:
            action_deadline = None

        is_urgent = action['params'].get('is_urgent')
        is_warning = action['params'].get('is_warning')

        if is_warning:
            is_urgent = "warning"

        medsenger_api.send_message(contract.id, fullfill_message(action['params']['text'] + report, contract,
                                                                 medsenger_api),
                                   only_doctor=True, action_name=action_name, action_link=action_link,
                                   is_urgent=is_urgent,
                                   need_answer=action['params'].get('need_answer'),
                                   action_deadline=action_deadline)
    if action['type'] == 'record':
        category_name = action['params'].get('category')
        value = action['params'].get('value')

        medsenger_api.add_record(contract.id, category_name, value)

    if action['type'] == 'medicine':
        name = action['params'].get('medicine_name')
        rules = action['params'].get('medicine_rules')

        medsenger_api.send_message(contract.id,
                                   'Внимание! В соответствие с алгоритмом, Вам требуется дополнительное принять препарат {}.<br>Комментарий: {}.'.format(
                                       name, rules), only_patient=True,
                                   is_urgent="warning")
        medsenger_api.send_message(contract.id,
                                   'Внимание! В соответствие с алгоритмом, пациенту отправлена просьба принять препарат {}.<br>Комментарий: {}.'.format(
                                       name, rules), only_doctor=True,
                                   is_urgent="warning")
    if action['type'] in ['form', 'attach_form', 'detach_form', 'attach_algorithm', 'detach_algorithm',
                          'attach_medicine', 'detach_medicine']:

        template_id = int(action['params'].get('template_id'))

        if action['type'] == 'form':
            has_message_to_patient = True
            form = form_manager.get(template_id)

            if form:
                form_manager.run(form, False, contract.id)

        if action['type'] == 'attach_form':
            form = form_manager.get(template_id)

            if form:
                form_manager.attach(template_id, contract)
                medsenger_api.send_message(contract.id,
                                           'Опросник {} автоматически подключен.'.format(form.title),
                                           only_doctor=True)

        if action['type'] == 'detach_form':
            form = form_manager.get(template_id)

            if form:
                form_manager.detach(template_id, contract)

                medsenger_api.send_message(contract.id,
                                           'Опросник {} автоматически отключен.'.format(form.title),
                                           only_doctor=True)

        if action['type'] == 'attach_algorithm':
            algorithm = algorithm_manager.get(template_id)

            if algorithm:
                algorithm_manager.attach(template_id, contract)
                medsenger_api.send_message(contract.id,
                                           'Алгоритм {} автоматически подключен.'.format(algorithm.title),
                                           only_doctor=True)

        if action['type'] == 'detach_algorithm':
            algorithm = algorithm_manager.get(template_id)

            if algorithm:
                algorithm_manager.detach(template_id, contract)
                medsenger_api.send_message(contract.id,
                                           'Алгоритм {} автоматически отключен.'.format(algorithm.title),
                                           only_doctor=True)

        if action['type'] == 'attach_medicine':
            medicine = medicine_manager.get(template_id)

            if medicine:
                medicine_manager.attach(template_id, contract)
                # medsenger_api.send_message(contract_id, 'Вам назначен препарат {} ({} / {}).'.format(
                #    medicine.title, medicine.rules, medicine.timetable_description()),
                #                               only_patient=True)
                medsenger_api.send_message(contract.id,
                                           'Внимание! Препарат {} ({} / {}) назначен автоматически.'.format(
                                               medicine.title, medicine.rules,
                                               medicine.timetable_description()),
                                           only_doctor=True)

        if action['type'] == 'detach_medicine':
            medicine = medicine_manager.get(template_id)

            if medicine:
                medicine_manager.detach(template_id, contract)

                medsenger_api.send_message(contract.id, 'Препарат {} ({} / {}) отменен.'.format(
                    medicine.title, medicine.rules, medicine.timetable_description()),
                                           only_patient=True)
                medsenger_api.send_message(contract.id,
                                           'Внимание! Препарат {} ({} / {}) отменен автоматически.'.format(
                                               medicine.title, medicine.rules,
                                               medicine.timetable_description()),
                                           only_doctor=True)
    if action['type'] == 'script':
        form_manager = FormManager(medsenger_api, db)
        contract_manager = ContractManager(medsenger_api, db)
        medicine_manager = MedicineManager(medsenger_api, db)
        reminder_manager = ReminderManager(medsenger_api, db)
        algorithm_params = algorithm.get_params()

        def get_param_value_by_code(code):
            param = list(filter(lambda p: p['code'] == code, algorithm_params))
            return param[0]['value'] if len(param) else None

        try:
            exec(action['params']['code'])
        except Exception as e:
            log(e)
    return has_message_to_patient
