import json
import re
import time
import uuid
from copy import copy, deepcopy
from datetime import datetime, timedelta

import medsenger_api
import requests

from config import DYNAMIC_CACHE

from sqlalchemy.orm.attributes import flag_modified, flag_dirty

from helpers import log, generate_event_description, DATACACHE, timezone_now, localize, fullfill_message
from managers.ContractsManager import ContractManager
from managers.FormManager import FormManager
from managers.Manager import Manager
from managers.MedicineManager import MedicineManager
from models import Patient, Contract, Algorithm


class AlgorithmsManager(Manager):
    def __init__(self, *args):
        super(AlgorithmsManager, self).__init__(*args)

    def get(self, algorithm_id):
        return Algorithm.query.filter_by(id=algorithm_id).first()

    def detach(self, template_id, contract):
        algorithms = list(filter(lambda x: x.template_id == template_id, contract.patient.algorithms))

        for algorithm in algorithms:
            self.db.session.delete(algorithm)

        self.__commit__()

        params = {
            'obj_id': list(map(lambda a: a.id, algorithms)),
            'action': 'detach',
            'object_type': 'algorithm',
            'algorithm_titles': list(map(lambda a: a.title, algorithms))
        }

        self.medsenger_api.add_record(contract.id, 'doctor_action',
                                      'Отключены алгоритмы', params=params)

        if DYNAMIC_CACHE:
            self.medsenger_api.update_cache(contract.id)

    def attach(self, template_id, contract, setup=None):
        algorithm = self.get(template_id)

        if algorithm:
            new_algorithm = algorithm.clone()
            new_algorithm.contract_id = contract.id
            new_algorithm.patient_id = contract.patient.id

            if setup:
                for step in algorithm.steps:
                    for condition in step['conditions']:
                        for block in condition['criteria']:
                            for criteria in block:
                                if criteria.get('ask_value') and setup.get(criteria['value_code']):
                                    criteria['value'] = setup.get(criteria['value_code'])

                if algorithm.common_conditions:
                    for index, condition in enumerate(algorithm.common_conditions):
                        for block in condition['criteria']:
                            for criteria in block:
                                if criteria.get('ask_value') and setup.get(criteria['value_code']):
                                    criteria['value'] = setup.get(criteria['value_code'])
                if setup.get('algorithm_{}_attach_date'.format(template_id)):
                    try:
                        new_algorithm.attach_date = datetime.strptime(
                            setup.get('algorithm_{}_attach_date'.format(template_id)),
                            '%Y-%m-%d')
                    except:
                        pass
                if setup.get('algorithm_{}_detach_date'.format(template_id)):
                    try:
                        new_algorithm.detach_date = datetime.strptime(
                            setup.get('algorithm_{}_detach_date'.format(template_id)),
                            '%Y-%m-%d')
                    except:
                        pass

            self.db.session.add(new_algorithm)
            self.__commit__()
            self.db.session.refresh(new_algorithm)

            self.change_step(new_algorithm, new_algorithm.initial_step)
            self.check_inits(new_algorithm, contract)
            self.check_init_timeouts(new_algorithm, contract)

            self.__commit__()
            self.db.session.refresh(new_algorithm)

            params = {
                'obj_id': new_algorithm.id,
                'action': 'attach',
                'object_type': 'algorithm',
                'params': new_algorithm.get_params()
            }
            self.medsenger_api.add_record(contract.id, 'doctor_action',
                                          'Подключен алгоритм "{}"'.format(new_algorithm.title), params=params)

            return True
        else:
            return False

    def clear(self, contract):
        Algorithm.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        params = {
            'action': 'clear',
            'object_type': 'algorithm'
        }
        self.medsenger_api.add_record(contract.id, 'doctor_action',
                                      'Отключены все алгоритмы.', params=params)

        return True

    def remove(self, id, contract):

        algorithm = Algorithm.query.filter_by(id=id).first_or_404()

        if algorithm.contract_id != contract.id and not contract.is_admin:
            return None

        Algorithm.query.filter_by(id=id).delete()

        self.__commit__()

        params = {
            'obj_id': algorithm.id,
            'action': 'detach',
            'object_type': 'algorithm'
        }

        self.medsenger_api.add_record(contract.id, 'doctor_action',
                                      'Отключен алгоритм "{}".'.format(algorithm.title), params=params)

        if DYNAMIC_CACHE:
            self.medsenger_api.update_cache(contract.id)

        return id

    def get_templates(self):
        return Algorithm.query.filter_by(is_template=True).all()

    def clear_cache(self, contract_id):
        to_del = []

        for A in DATACACHE:
            if A[2] == contract_id:
                to_del.append(A)

        for k in to_del:
            del DATACACHE[k]

    def get_from_cache(self, A):
        if A in DATACACHE:
            t, answer = DATACACHE[A]

            if time.time() - t < 30:
                return answer
            else:
                del DATACACHE[A]
        return None

    def save_to_cache(self, A, value):
        for k, v in list(DATACACHE.items()):
            if time.time() - v[0] > 30:
                del DATACACHE[k]

        DATACACHE[A] = (int(time.time()), value)

        return value

    def get_values(self, category_name, mode, contract_id, dimension='hours', hours=1, times=1, algorithm=None,
                   offset_dim='times', offset_count=0, zone=None):
        k = (category_name, mode, contract_id, dimension, hours, times, offset_dim, offset_count)
        cached = self.get_from_cache(k)
        if cached != None:
            return cached

        if category_name == "exact_date":
            return [datetime.now().strftime("%Y-%m-%d")], None
        if category_name == "contract_start_date":
            return self.save_to_cache(k, ([self.medsenger_api.get_patient_info(contract_id).get('start_date')], None))
        if category_name == "contract_end_date":
            return self.save_to_cache(k, ([self.medsenger_api.get_patient_info(contract_id).get('end_date')], None))

        if category_name == "algorithm_attach_date" and algorithm:
            if algorithm.attach_date:
                return [algorithm.attach_date.strftime("%Y-%m-%d")], None
            else:
                return None, None
        if category_name == "algorithm_detach_date" and algorithm:
            if algorithm.detach_date:
                return [algorithm.detach_date.strftime("%Y-%m-%d")], None
            else:
                return None, None

        if mode == 'value' or mode == 'category_value':
            answer = self.medsenger_api.get_records(contract_id, category_name, group=True, limit=1)
        else:
            time_from = datetime.now() - timedelta(hours=hours)
            time_to = datetime.now()
            offset = 0

            if offset_dim == 'hours':
                time_from -= timedelta(hours=offset_count)
                time_to -= timedelta(hours=offset_count)
            elif offset_dim == 'days':
                time_from -= timedelta(days=offset_count)
                time_to -= timedelta(days=offset_count)
            elif offset_dim == 'times':
                offset = offset_count

            if dimension == 'hours':
                answer = self.medsenger_api.get_records(contract_id, category_name,
                                                        time_from=int(
                                                            (datetime.now() - timedelta(hours=hours)).timestamp()),
                                                        offset=offset)
            else:
                answer = self.medsenger_api.get_records(contract_id, category_name, limit=times,
                                                        time_to=int(time_to.timestamp()),
                                                        offset=offset)
        if not answer:
            self.save_to_cache(k, (None, None))
            return None, None

        values = list(map(lambda x: x['value'], answer['values']))
        objects = answer['values']

        if not values:
            answer = None, None
        elif mode == 'value' and (
            time.time() - int(answer['values'][0].get('timestamp')) > 60 * 60 * 12 or time.time() - int(
            answer['values'][0].get('uploaded')) > 10):
            answer = None, None
        elif mode == 'value' or mode == 'category_value':
            answer = values, objects
        elif mode == 'sum':
            answer = [sum(values)], None
        elif mode == 'difference':
            answer = [max(values) - min(values)], None
        elif mode == 'delta':
            answer = [values[-1] - values[0]], None
        elif mode == 'average':
            avg = sum(values) / len(values)
            answer = [round(avg, 2)], None
        elif mode == 'max':
            answer = [max(values)], None
        elif mode == 'min':
            answer = [min(values)], None
        else:
            answer = None, None

        return self.save_to_cache(k, answer)

    def check_values(self, left, right, sign, modifier=0, multiplier=1):
        modifiers = []

        try:
            if isinstance(modifier, str) and "|" in modifier:
                modifiers = list(map(float, modifier.split('|')))
            else:
                modifiers = [float(modifier)]
        except:
            modifiers = [0]

        conditions = []

        if "date_" in sign:
            for modifier in modifiers:
                leftc = datetime.strptime(left, '%Y-%m-%d').date()
                rightc = (datetime.strptime(right, '%Y-%m-%d') + timedelta(days=modifier)).date()
                signc = sign.replace('date_', '')

                conditions.append((leftc, rightc, signc))
        else:
            for modifier in modifiers:
                try:
                    leftc = float(left)
                except:
                    leftc = left

                try:
                    rightc = float(right)
                except:
                    rightc = right

                try:
                    rightc = rightc * multiplier + modifier
                except:
                    pass

                conditions.append((leftc, rightc, sign))

        for left, right, sign in conditions:
            if sign == 'greater':
                return left > right
            if sign == 'less':
                return left < right
            if sign == 'greater_or_equal':
                return left >= right
            if sign == 'less_or_equal':
                return left <= right
            if sign == 'equal':
                return left == right
            if sign == 'not_equal':
                return left != right
            if sign == 'contains':
                return right in left

        return False

    def check_criteria(self, criteria, contract_id, buffer, descriptions, category_names, algorithm=None, contract=None,
                       is_init=False):
        category_name = criteria.get('category')
        mode = criteria.get('left_mode')

        if mode == 'step_init':
            return False

        if mode == 'init':
            return is_init

        if mode != 'time':
            objects = None
            dimension = criteria.get('left_dimension')
            offset_dim = criteria.get('left_offset_dimension', 'times')
            offset_count = criteria.get('left_offset', 0)

            if dimension == 'hours':
                left_values, objects = self.get_values(category_name, criteria['left_mode'], contract_id, dimension,
                                                       hours=criteria.get('left_hours'),
                                                       offset_dim=offset_dim, offset_count=offset_count,
                                                       algorithm=algorithm)
            else:
                left_values, objects = self.get_values(category_name, criteria['left_mode'], contract_id, dimension,
                                                       times=criteria.get('left_times'), offset_dim=offset_dim,
                                                       offset_count=offset_count, algorithm=algorithm)

            if criteria['right_mode'] == 'value':
                right_values = [criteria.get('value')]
            else:
                right_category = criteria.get('right_category')
                dimension = criteria.get('right_dimension')
                offset_dim = criteria.get('right_offset_dimension', 'times')
                offset_count = criteria.get('right_offset', 0)

                if right_category:
                    if dimension == 'hours':
                        right_values, _ = self.get_values(right_category, criteria['right_mode'], contract_id,
                                                          dimension,
                                                          hours=criteria.get('right_hours'),
                                                          offset_dim=offset_dim, offset_count=offset_count,
                                                          algorithm=algorithm)
                    else:
                        right_values, _ = self.get_values(right_category, criteria['right_mode'], contract_id,
                                                          dimension=dimension, times=criteria.get('right_times'),
                                                          offset_dim=offset_dim, offset_count=offset_count,
                                                          algorithm=algorithm)
                else:
                    if dimension == 'hours':
                        right_values, _ = self.get_values(category_name, criteria['right_mode'], contract_id,
                                                          dimension=dimension, hours=criteria.get('right_hours'),
                                                          offset_dim=offset_dim, offset_count=offset_count,
                                                          algorithm=algorithm)
                    else:
                        right_values, _ = self.get_values(category_name, criteria['right_mode'], contract_id,
                                                          dimension=dimension, times=criteria.get('right_times'),
                                                          offset_dim=offset_dim, offset_count=offset_count,
                                                          algorithm=algorithm)
            if not right_values or not left_values:
                return False
            found = False

            for i in range(len(left_values)):
                lvalue = left_values[i]

                for rvalue in right_values:
                    modifier = 0
                    multiplier = 1
                    if criteria.get('right_mode') != 'value':
                        modifier = criteria.get('value', 0)
                        multiplier = criteria.get('multiplier', 1)
                    result = self.check_values(lvalue, rvalue, criteria['sign'], modifier, multiplier)

                    if result:
                        current_answer = None
                        if objects:
                            current_answer = objects[i]

                        description = generate_event_description(criteria, lvalue, rvalue, category_names,
                                                                 current_answer)

                        if not criteria.get('hide_in_description'):
                            descriptions.append(description)

                        if current_answer:
                            buffer.append({
                                "id": current_answer['id'],
                                "comment": description
                            })

                    if result:
                        found = True
            return found

        else:
            date = criteria.get('value')
            add_hours = criteria.get('right_hours')
            sign = criteria.get('sign')

            date_obj = localize(datetime.strptime(date, '%Y-%m-%d'), algorithm.contract.timezone) + timedelta(
                hours=add_hours)
            now_obj = timezone_now(algorithm.contract.timezone)

            if sign == 'equal' and 0 <= (now_obj - date_obj).total_seconds() < 60 * 60:
                return True
            if sign == 'greater' and (now_obj - date_obj).total_seconds() > 0:
                return True
            if sign == 'less' and (now_obj - date_obj).total_seconds() < 0:
                return True
            return False

    def run_action(self, action, contract, descriptions, algorithm):
        has_message_to_patient = False
        report = ""
        if action['params'].get('send_report') and descriptions:
            report = '<br><br><strong>События:</strong><ul>' + ''.join(
                ["<li>{}</li>".format(description) for description in descriptions]) + "</ul>"

        if action['type'] == 'change_step':
            self.change_step(algorithm, action['params']['target'])

        if action['type'] == 'set_info_materials':
            self.medsenger_api.set_info_materials(contract.id, action['params']['materials'])

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

            self.medsenger_api.send_order(contract.id, order, agent_id, params)

        if action['type'] == 'patient_public_attachment':
            criteria = action['params'].get('criteria')
            comment = action['params'].get('text')
            info = self.medsenger_api.get_patient_info(contract.id)

            attachments = []

            for file in info['public_attachments']:
                if criteria in file.get('name').lower():
                    attachments.append({'public_attachment_id': file.get('id')})

            if attachments:
                has_message_to_patient = True
                self.medsenger_api.send_message(contract.id, comment,
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
                    self.medsenger_api.send_message(contract.id, text, only_patient=True,
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

            self.medsenger_api.send_message(contract.id, action['params']['text'] + report,
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

            self.medsenger_api.send_message(contract.id, fullfill_message(action['params']['text'] + report, contract,
                                                                          self.medsenger_api),
                                            only_doctor=True, action_name=action_name, action_link=action_link,
                                            is_urgent=is_urgent,
                                            need_answer=action['params'].get('need_answer'),
                                            action_deadline=action_deadline)
        if action['type'] == 'record':
            category_name = action['params'].get('category')
            value = action['params'].get('value')

            self.medsenger_api.add_record(contract.id, category_name, value)

        if action['type'] == 'medicine':
            name = action['params'].get('medicine_name')
            rules = action['params'].get('medicine_rules')

            self.medsenger_api.send_message(contract.id,
                                            'Внимание! В соответствие с алгоритмом, Вам требуется дополнительное принять препарат {}.<br>Комментарий: {}.'.format(
                                                name, rules), only_patient=True,
                                            is_urgent="warning")
            self.medsenger_api.send_message(contract.id,
                                            'Внимание! В соответствие с алгоритмом, пациенту отправлена просьба принять препарат {}.<br>Комментарий: {}.'.format(
                                                name, rules), only_doctor=True,
                                            is_urgent="warning")
        if action['type'] in ['form', 'attach_form', 'detach_form', 'attach_algorithm', 'detach_algorithm',
                              'attach_medicine', 'detach_medicine']:
            form_manager = FormManager(self.medsenger_api, self.db)
            contract_manager = ContractManager(self.medsenger_api, self.db)
            medicine_manager = MedicineManager(self.medsenger_api, self.db)

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
                    self.medsenger_api.send_message(contract.id,
                                                    'Опросник {} автоматически подключен.'.format(form.title),
                                                    only_doctor=True)

            if action['type'] == 'detach_form':
                form = form_manager.get(template_id)

                if form:
                    form_manager.detach(template_id, contract)
                    self.medsenger_api.send_message(contract.id,
                                                    'Опросник {} автоматически отключен.'.format(form.title),
                                                    only_doctor=True)

            if action['type'] == 'attach_algorithm':
                algorithm = self.get(template_id)

                if algorithm:
                    self.attach(template_id, contract)
                    self.medsenger_api.send_message(contract.id,
                                                    'Алгоритм {} автоматически подключен.'.format(algorithm.title),
                                                    only_doctor=True)

            if action['type'] == 'detach_algorithm':
                algorithm = self.get(template_id)

                if algorithm:
                    self.detach(template_id, contract)
                    self.medsenger_api.send_message(contract.id,
                                                    'Алгоритм {} автоматически отключен.'.format(algorithm.title),
                                                    only_doctor=True)

            if action['type'] == 'attach_medicine':
                medicine = medicine_manager.get(template_id)

                if medicine:
                    medicine_manager.attach(template_id, contract)
                    # self.medsenger_api.send_message(contract_id, 'Вам назначен препарат {} ({} / {}).'.format(
                    #    medicine.title, medicine.rules, medicine.timetable_description()),
                    #                               only_patient=True)
                    self.medsenger_api.send_message(contract.id,
                                                    'Внимание! Препарат {} ({} / {}) назначен автоматически.'.format(
                                                        medicine.title, medicine.rules,
                                                        medicine.timetable_description()),
                                                    only_doctor=True)

            if action['type'] == 'detach_medicine':
                medicine = medicine_manager.get(template_id)

                if medicine:
                    medicine_manager.detach(template_id, contract)

                    self.medsenger_api.send_message(contract.id, 'Препарат {} ({} / {}) отменен.'.format(
                        medicine.title, medicine.rules, medicine.timetable_description()),
                                                    only_patient=True)
                    self.medsenger_api.send_message(contract.id,
                                                    'Внимание! Препарат {} ({} / {}) отменен автоматически.'.format(
                                                        medicine.title, medicine.rules,
                                                        medicine.timetable_description()),
                                                    only_doctor=True)
        if action['type'] == 'script':
            form_manager = FormManager(self.medsenger_api, self.db)
            contract_manager = ContractManager(self.medsenger_api, self.db)
            medicine_manager = MedicineManager(self.medsenger_api, self.db)
            try:
                exec(action['params']['code'])
            except Exception as e:
                log(e)
        return has_message_to_patient

    def get_step(self, algorithm, step=None):
        if not step:
            step = algorithm.current_step

        if not step:
            if algorithm.initial_step:
                step = algorithm.initial_step
                algorithm.current_step = step
            else:
                step = algorithm.steps[0]['uid']
                algorithm.current_step = step
                algorithm.initial_step = step
            self.__commit__()

        return next(s for s in algorithm.steps if s['uid'] == step)

    def update_categories(self, algorithm):
        step = self.get_step(algorithm)

        algorithm.categories = '|'.join(
            map(lambda c: '|'.join(['|'.join(k['category'] for k in block) for block in c['criteria']]),
                step['conditions']))

        if algorithm.common_conditions:
            algorithm.categories = '|'.join([algorithm.categories, '|'.join(
                map(lambda c: '|'.join(['|'.join(k['category'] for k in block) for block in c['criteria']]),
                    algorithm.common_conditions))])

    def change_step(self, algorithm, step):
        new_step = self.get_step(algorithm, step)

        algorithm.current_step = new_step['uid']

        if new_step.get('reset_minutes'):
            algorithm.timeout_at = time.time() + 60 * int(new_step['reset_minutes'])
        else:
            algorithm.timeout_at = 0

        self.update_categories(algorithm)

        for condition in new_step['conditions']:
            if condition.get('timeout_on_init'):
                condition['last_fired'] = int(time.time())
            if any(any(criteria['left_mode'] == 'step_init' for criteria in block) for block in condition['criteria']):
                for action in condition['positive_actions']:
                    self.run_action(action, algorithm.contract, [], algorithm)
        self.__commit__()

    def check_timeouts(self, app):
        with app.app_context():
            algorithms = list(Algorithm.query.filter((Algorithm.contract_id != None) & (Algorithm.timeout_at != 0) & (
                Algorithm.timeout_at < time.time())).all())

            for algorithm in algorithms:
                self.timeout(algorithm)

    def check_detach_dates(self, app):
        with app.app_context():
            algorithms = list(Algorithm.query.filter(
                (Algorithm.detach_date == datetime.now().date()) & (Algorithm.is_template == False)).all())

            for algorithm in algorithms:
                self.db.session.delete(algorithm)
            self.__commit__()

    def timeout(self, algorithm):
        current_step = self.get_step(algorithm)
        algorithm.timeout_at = 0
        contract = algorithm.contract

        for action in current_step['timeout_actions']:
            self.run_action(action, contract, [], algorithm)

        self.__commit__()

    def run(self, algorithm):
        current_step = self.get_step(algorithm)
        contract = algorithm.contract
        fired = False
        has_message_to_patient = False

        additional_conditions = []
        if algorithm.common_conditions:
            additional_conditions = algorithm.common_conditions

        for condition in additional_conditions + current_step['conditions']:
            bypass = False

            criteria = condition['criteria']

            reset_minutes = int(condition.get('reset_minutes', 0))
            last_fired = int(condition.get('last_fired', 0))

            if time.time() - last_fired < max(reset_minutes * 60, 10):
                bypass = True
                print("bypassed")

            additions = []
            descriptions = []
            category_names = {category['name']: category['description'] for category in
                              self.medsenger_api.get_categories()}

            result = any([all(
                list(
                    map(lambda x: self.check_criteria(x, contract.id, additions, descriptions, category_names,
                                                      algorithm=algorithm), block)))
                for block in criteria])

            if result:
                if not condition.get('skip_additions'):
                    for addition in additions:
                        self.medsenger_api.send_addition(contract.id, addition['id'], {
                            "algorithm_id": algorithm.id,
                            "comment": addition["comment"]
                        })
                fired = True

                if not bypass:
                    for action in condition.get('positive_actions', []):
                        has_message = self.run_action(action, contract, descriptions, algorithm)
                        has_message_to_patient = has_message_to_patient or has_message
                    condition['last_fired'] = int(time.time())
            else:
                for action in condition.get('negative_actions', []):
                    self.run_action(action, contract, descriptions, algorithm)
        if fired:
            try:
                flag_modified(algorithm, "steps")
                flag_modified(algorithm, "common_conditions")
                self.__commit__()
            except Exception as e:
                log(e, False)

        if DYNAMIC_CACHE:
            self.medsenger_api.update_cache(contract.id)

        return fired, has_message_to_patient

    def search_params(self, contract):
        params = {}

        def search_condition(condition, step_index, condition_index, common=False):
            for block_index, block in enumerate(condition['criteria']):
                for criteria_index, criteria in enumerate(block):
                    if criteria.get('ask_value'):
                        pair = (criteria.get('value_name'), criteria.get('value'), criteria.get('value_code'))

                        loc = {
                            'algorithm': algorithm.id,
                            'step': step_index,
                            'condition': condition_index,
                            'block': block_index,
                            'criteria': criteria_index,
                            'common': common
                        }

                        if pair in params:
                            params[pair]['locations'].append(loc)
                        else:
                            params.update({
                                pair: {
                                    'name': pair[0],
                                    'value': pair[1],
                                    'code': pair[2],
                                    'locations': [loc]
                                }
                            })

        for algorithm in contract.algorithms:
            for step_index, step in enumerate(algorithm.steps):
                for condition_index, condition in enumerate(step['conditions']):
                    search_condition(condition, step_index, condition_index)

            if algorithm.common_conditions:
                for condition_index, condition in enumerate(algorithm.common_conditions):
                    search_condition(condition, None, condition_index, True)

        return [value for key, value in params.items()]

    def examine(self, contract, form):
        categories = form.categories.split('|')
        categories.append('action')

        patient = contract.patient

        algorithms = filter(lambda algorithm: any([cat in algorithm.categories.split('|') for cat in categories]),
                            patient.algorithms)

        fired = False
        has_message_to_patient = False

        for algorithm in algorithms:
            result, has_message = self.run(algorithm)
            has_message_to_patient = has_message_to_patient or has_message

        if not has_message_to_patient and form.thanks_text:
            self.medsenger_api.send_message(contract.id, text=form.thanks_text, only_patient=True,
                                            action_deadline=time.time() + 60 * 60)

        self.clear_cache(contract.id)

    def hook(self, contract, category_names):
        patient = contract.patient

        algorithms = list(
            filter(lambda algorithm: any(
                map(lambda cat: cat in algorithm.categories.split('|'), category_names.split('|'))),
                   patient.algorithms))

        for algorithm in algorithms:
            self.run(algorithm)

        return True

    def check_inits(self, algorithm, contract):
        category_names = {category['name']: category['description'] for category in
                          self.medsenger_api.get_categories()}

        if not algorithm.common_conditions:
            algorithm.common_conditions = []

        for condition in algorithm.common_conditions + self.get_step(algorithm).get('conditions', []):
            if any(any(criteria['category'] == 'init' for criteria in block) for block in condition['criteria']):

                result = any([all(
                    list(
                        map(lambda x: self.check_criteria(x, contract.id, [], [], category_names,
                                                          algorithm=algorithm, is_init=True), block))) for block in
                    condition['criteria']])

                if result:
                    for action in condition['positive_actions']:
                        self.run_action(action, contract, [], algorithm)

    def check_init_timeouts(self, algorithm, contract):
        if algorithm.common_conditions:
            for condition in algorithm.common_conditions:
                if condition.get('timeout_on_init'):
                    condition['last_fired'] = int(time.time())

    def create_or_edit(self, data, contract):
        try:
            algorithm_id = data.get('id')
            if not algorithm_id:
                algorithm = Algorithm()
            else:
                algorithm = Algorithm.query.filter_by(id=algorithm_id).first_or_404()

                if algorithm.contract_id != contract.id and not contract.is_admin:
                    return None

            algorithm.title = data.get('title')
            algorithm.steps = data.get('steps')
            algorithm.common_conditions = data.get('common_conditions')
            algorithm.description = data.get('description')
            algorithm.categories = data.get('categories')
            algorithm.template_id = data.get('template_id')
            algorithm.initial_step = data.get('steps')[0].get('uid')

            if data.get('attach_date'):
                try:
                    algorithm.attach_date = datetime.strptime(data.get('attach_date'), "%Y-%m-%d")
                except:
                    pass
            else:
                algorithm.attach_date = None

            if data.get('detach_date'):
                try:
                    algorithm.detach_date = datetime.strptime(data.get('detach_date'), "%Y-%m-%d")
                except:
                    pass
            else:
                algorithm.detach_date = None

            if data.get('is_template') and contract.is_admin:
                algorithm.clinics = data.get('clinics')
                algorithm.is_template = True
                algorithm.template_category = data.get('template_category')
            else:
                algorithm.patient_id = contract.patient_id
                algorithm.contract_id = contract.id

            if not algorithm_id:
                self.db.session.add(algorithm)

            self.__commit__()

            if not data.get('is_template'):
                params = {
                    'obj_id': algorithm.id,
                    'action': 'edit' if algorithm_id else 'create',
                    'object_type': 'algorithm',
                    'algorithm_params': algorithm.get_params()
                }
                self.medsenger_api.add_record(contract.id, 'doctor_action',
                                              '{} алгоритм "{}".'.format('Изменен' if algorithm_id else 'Подключен',
                                                                         algorithm.title), params=params)

            if algorithm.contract_id == contract.id:
                if not algorithm.current_step:
                    algorithm.current_step = data.get('steps')[0].get('uid')
                    self.change_step(algorithm, algorithm.initial_step)
                if not algorithm_id:
                    self.check_inits(algorithm, contract)
                    self.check_init_timeouts(algorithm, contract)
                self.update_categories(algorithm)

                self.__commit__()

            if DYNAMIC_CACHE:
                self.medsenger_api.update_cache(contract.id)

            return algorithm
        except Exception as e:
            log(e)
            return None
