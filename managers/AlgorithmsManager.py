import time
import uuid
from copy import copy, deepcopy
from datetime import datetime, timedelta

from sqlalchemy.orm.attributes import flag_modified, flag_dirty

from helpers import log, generate_description
from managers.ContractsManager import ContractManager
from managers.FormManager import FormManager
from managers.Manager import Manager
from managers.MedicineManager import MedicineManager
from models import Patient, Contract, Algorithm


class AlgorithmsManager(Manager):
    def __init__(self, *args):
        super(AlgorithmsManager, self).__init__(*args)

    def __migrate__(self):
        algorithms = Algorithm.query.all()

        for algorithm in algorithms:
            algorithm.steps = [
                {
                    "uid": str(uuid.uuid4()),
                    "title": algorithm.title,
                    "conditions": [
                        {
                            "uid": str(uuid.uuid4()),
                            "criteria": algorithm.criteria,
                            "positive_actions": [action for action in algorithm.actions if not action['params'].get('is_negative')],
                            "negative_actions": [action for action in algorithm.actions if action['params'].get('is_negative')]
                        }
                    ],
                    "timeout_actions": [],
                    "reset_minutes": 0
                }
            ]
            algorithm.current_step = algorithm.steps[0]['uid']
            algorithm.initial_step = algorithm.steps[0]['uid']

        self.__commit__()

    def get(self, algorithm_id):
        return Algorithm.query.filter_by(id=algorithm_id).first_or_404()

    def detach(self, template_id, contract):
        algorithms = list(filter(lambda x: x.template_id == template_id, contract.patient.algorithms))

        for algorithm in algorithms:
            algorithm.delete()

        self.__commit__()

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

            self.db.session.add(new_algorithm)
            self.__commit__()
            self.db.session.refresh(new_algorithm)

            self.check_inits(new_algorithm, contract)

            return True
        else:
            return False

    def clear(self, contract):
        Algorithm.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        return True

    def remove(self, id, contract):

        algorithm = Algorithm.query.filter_by(id=id).first_or_404()

        if algorithm.contract_id != contract.id and not contract.is_admin:
            return None

        Algorithm.query.filter_by(id=id).delete()

        self.__commit__()
        return id

    def get_templates(self):
        return Algorithm.query.filter_by(is_template=True).all()

    def get_values(self, category_name, mode, contract_id, dimension='hours', hours=1, times=1):
        if category_name == "exact_time":
            return [datetime.now().strftime("%Y-%m-%d")], None

        if mode == 'value' or mode == 'category_value':
            offset = 0
        else:
            offset = 1

        if mode == 'value' or mode == 'category_value':
            answer = self.medsenger_api.get_records(contract_id, category_name, group=True, offset=offset)
        else:
            if dimension == 'hours':
                answer = self.medsenger_api.get_records(contract_id, category_name,
                                                        time_from=int(
                                                            (datetime.now() - timedelta(hours=hours)).timestamp()),
                                                        offset=offset)
            else:
                answer = self.medsenger_api.get_records(contract_id, category_name, limit=times, offset=offset)

        if not answer:
            return None, None

        values = list(map(lambda x: x['value'], answer['values']))
        objects = answer['values']

        if not values:
            return None, None
        if mode == 'value' and time.time() - int(answer['values'][0].get('timestamp')) > 10:
            return None, None
        if mode == 'value' or mode == 'category_value':
            return values, objects
        if mode == 'sum':
            return [sum(values)], None
        if mode == 'difference':
            return [max(values) - min(values)], None
        if mode == 'delta':
            return [values[-1] - values[0]], None
        if mode == 'average':
            return [sum(values) / len(values)], None
        if mode == 'max':
            return [max(values)], None
        if mode == 'min':
            return [min(values)], None

        return None, None

    def check_values(self, left, right, sign, modifier=0):

        try:
            modifier = float(modifier)
        except:
            modifier = 0

        if "date_" in sign:
            left = datetime.strptime(left, '%Y-%m-%d').date()
            right = (datetime.strptime(right, '%Y-%m-%d') + timedelta(days=modifier)).date()
            sign = sign.lstrip('date_')
        else:
            try:
                right = right + modifier
            except:
                pass

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

    def check_criteria(self, criteria, contract_id, buffer, descriptions, category_names):
        category_name = criteria.get('category')
        mode = criteria.get('left_mode')

        if mode in ['init', 'step_init']:
            return False

        if mode != 'time':
            objects = None
            dimension = criteria.get('left_dimension')
            if dimension == 'hours':
                left_values, objects = self.get_values(category_name, criteria['left_mode'], contract_id, dimension,
                                                       hours=criteria.get('left_hours'))
            else:
                left_values, objects = self.get_values(category_name, criteria['left_mode'], contract_id, dimension,
                                                       times=criteria.get('left_times'))

            if criteria['right_mode'] == 'value':
                right_values = [criteria.get('value')]
            else:
                right_category = criteria.get('right_category')
                dimension = criteria.get('right_dimension')
                if right_category:
                    if dimension == 'hours':
                        right_values, _ = self.get_values(right_category, criteria['right_mode'], contract_id,
                                                          dimension,
                                                          hours=criteria.get('right_hours'))
                    else:
                        right_values, _ = self.get_values(right_category, criteria['right_mode'], contract_id,
                                                          dimension=dimension, times=criteria.get('right_times'))
                else:
                    if dimension == 'hours':
                        right_values, _ = self.get_values(category_name, criteria['right_mode'], contract_id,
                                                          dimension=dimension, hours=criteria.get('right_hours'))
                    else:
                        right_values, _ = self.get_values(category_name, criteria['right_mode'], contract_id,
                                                          dimension=dimension, times=criteria.get('right_times'))

            if not right_values or not left_values:
                return False

            found = False

            for i in range(len(left_values)):
                lvalue = left_values[i]

                for rvalue in right_values:
                    modifier = 0
                    if criteria.get('right_mode') != 'value':
                        modifier = criteria.get('value')
                    result = self.check_values(lvalue, rvalue, criteria['sign'], modifier)

                    if result:
                        current_answer = None
                        if objects:
                            current_answer = objects[i]

                        description = generate_description(criteria, lvalue, rvalue, category_names, current_answer)

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

            date_obj = datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=add_hours)
            now_obj = datetime.now()

            if sign == 'equal' and 0 <= (now_obj - date_obj).total_seconds() < 60 * 60:
                return True
            if sign == 'greater' and (now_obj - date_obj).total_seconds() > 0:
                return True
            if sign == 'less' and (now_obj - date_obj).total_seconds() < 0:
                return True
            return False

    def run_action(self, action, contract_id, descriptions, algorithm):
        report = ""
        if action['params'].get('send_report') and descriptions:
            report = '<br><br><strong>События:</strong><ul>' + ''.join(
                ["<li>{}</li>".format(description) for description in descriptions]) + "</ul>"

        if action['type'] == 'change_step':
            self.change_step(algorithm, action['params']['target'])

        if action['type'] == 'order':
            order = action['params'].get('order')
            agent_id = action['params'].get('agent_id')
            params = deepcopy(action['params'].get('order_params', {}))

            if action['params'].get('send_report'):
                params["message"] = params.get("message", "") + report

            self.medsenger_api.send_order(contract_id, order, agent_id, params)


        if action['type'] == 'patient_message':
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

            self.medsenger_api.send_message(contract_id, action['params']['text'] + report,
                                            only_patient=True, action_name=action_name, action_link=action_link,
                                            is_urgent=action['params'].get('is_urgent'),
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

            self.medsenger_api.send_message(contract_id, action['params']['text'] + report,
                                            only_doctor=True, action_name=action_name, action_link=action_link,
                                            is_urgent=action['params'].get('is_urgent'),
                                            need_answer=action['params'].get('need_answer'),
                                            action_deadline=action_deadline)
        if action['type'] == 'record':
            category_name = action['params'].get('category')
            value = action['params'].get('value')

            self.medsenger_api.add_record(contract_id, category_name, value)

        if action['type'] == 'medicine':
            name = action['params'].get('medicine_name')
            rules = action['params'].get('medicine_rules')

            self.medsenger_api.send_message(contract_id,
                                            'Внимание! В соответствие с алгоритмом, Вам требуется дополнительное принять препарат {}.<br>Комментарий: {}.'.format(
                                                name, rules), only_patient=True,
                                            is_urgent=True)
            self.medsenger_api.send_message(contract_id,
                                            'Внимание! В соответствие с алгоритмом, пациенту отправлена просьба принять препарат {}.<br>Комментарий: {}.'.format(
                                                name, rules), only_doctor=True,
                                            is_urgent=True)
        if action['type'] in ['form', 'attach_form', 'detach_form', 'attach_algorithm', 'detach_algorithm',
                              'attach_medicine', 'detach_medicine']:
            form_manager = FormManager(self.medsenger_api, self.db)
            contract_manager = ContractManager(self.medsenger_api, self.db)
            medicine_manager = MedicineManager(self.medsenger_api, self.db)

            contract = contract_manager.get(contract_id)
            template_id = action['params'].get('template_id')

            if action['type'] == 'form':
                form = form_manager.get(template_id)

                if form:
                    form_manager.run(form, False, contract_id)

            if action['type'] == 'attach_form':
                form = form_manager.get(template_id)

                if form:
                    form_manager.attach(template_id, contract)
                    self.medsenger_api.send_message(contract_id,
                                                    'Опросник {} автоматически подключен.'.format(form.title),
                                                    only_doctor=True)

            if action['type'] == 'detach_form':
                form = form_manager.get(template_id)

                if form:
                    form_manager.detach(template_id, contract)
                    self.medsenger_api.send_message(contract_id,
                                                    'Опросник {} автоматически отключен.'.format(form.title),
                                                    only_doctor=True)

            if action['type'] == 'attach_algorithm':
                algorithm = self.get(template_id)

                if algorithm:
                    self.attach(template_id, contract)
                    self.medsenger_api.send_message(contract_id,
                                                    'Алгоритм {} автоматически подключен.'.format(algorithm.title),
                                                    only_doctor=True)

            if action['type'] == 'detach_algorithm':
                algorithm = self.get(template_id)

                if algorithm:
                    self.detach(template_id, contract)
                    self.medsenger_api.send_message(contract_id,
                                                    'Алгоритм {} автоматически отключен.'.format(algorithm.title),
                                                    only_doctor=True)

            if action['type'] == 'attach_medicine':
                medicine = self.get(template_id)

                if medicine:
                    medicine_manager.attach(template_id, contract)
                    self.medsenger_api.send_message(contract_id, 'Вам назначен препарат {} ({} / {}).'.format(
                        medicine.title, medicine.rules, medicine.timetable_description()),
                                                    only_patient=True)
                    self.medsenger_api.send_message(contract_id,
                                                    'Внимание! Препарат {} ({} / {}) назначен автоматически.'.format(
                                                        medicine.title, medicine.rules,
                                                        medicine.timetable_description()),
                                                    only_doctor=True)

            if action['type'] == 'detach_medicine':
                medicine = self.get(template_id)

                if medicine:
                    medicine_manager.detach(template_id, contract)

                    self.medsenger_api.send_message(contract_id, 'Препарат {} ({} / {}) отменен.'.format(
                        medicine.title, medicine.rules, medicine.timetable_description()),
                                                    only_patient=True)
                    self.medsenger_api.send_message(contract_id,
                                                    'Внимание! Препарат {} ({} / {}) отменен автоматически.'.format(
                                                        medicine.title, medicine.rules,
                                                        medicine.timetable_description()),
                                                    only_doctor=True)

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

    def change_step(self, algorithm, step):
        new_step = self.get_step(algorithm, step)

        algorithm.current_step = new_step['uid']

        if new_step.get('reset_minutes'):
            algorithm.timeout_at = time.time() + 60 * int(new_step['reset_minutes'])
        else:
            algorithm.timeout_at = 0

        algorithm.categories = '|'.join(map(lambda c: '|'.join(['|'.join(k['category'] for k in block) for block in c['criteria']]), new_step['conditions']))

        for condition in new_step['conditions']:
            if any(any(criteria['category'] == 'step_init' for criteria in block) for block in condition['criteria']):
                for action in condition['positive_actions']:
                    self.run_action(action, algorithm.contract.id, [], algorithm)
        self.__commit__()

    def check_timeouts(self, app):
        with app.app_context():
            algorithms = list(Algorithm.query.filter((Algorithm.contract_id != None) & (Algorithm.timeout_at != 0) & (Algorithm.timeout_at < time.time())).all())

            for algorithm in algorithms:
                self.timeout(algorithm)

    def timeout(self, algorithm):
        current_step = self.get_step(algorithm)
        algorithm.timeout_at = 0
        contract_id = algorithm.contract_id

        for action in current_step['timeout_actions']:
            self.run_action(action, contract_id, [], algorithm)

        self.__commit__()

    def run(self, algorithm):
        current_step = self.get_step(algorithm)
        contract_id = algorithm.contract_id
        fired = False

        for condition in current_step['conditions']:
            criteria = condition['criteria']

            reset_minutes = int(condition.get('reset_minutes', 0))
            last_fired = int(condition.get('last_fired', 0))
            if reset_minutes and last_fired:
                if time.time() - last_fired < reset_minutes * 60:
                    continue


            additions = []
            descriptions = []
            category_names = {category['name']: category['description'] for category in self.medsenger_api.get_categories()}

            result = any([all(
                list(map(lambda x: self.check_criteria(x, contract_id, additions, descriptions, category_names), block)))
                for block in criteria])

            if result:
                for addition in additions:
                    self.medsenger_api.send_addition(contract_id, addition['id'], {
                        "algorithm_id": algorithm.id,
                        "comment": addition["comment"]
                    })
                fired = True
                for action in condition.get('positive_actions', []):
                    self.run_action(action, contract_id, descriptions, algorithm)
                condition['last_fired'] = int(time.time())
            else:
                for action in condition.get('negative_actions', []):
                    self.run_action(action, contract_id, descriptions, algorithm)
        if fired:
            try:
                flag_modified(algorithm, "steps")
                self.__commit__()
            except Exception as e:
                log(e, False)
        return fired

    def search_params(self, contract):
        params = set()

        for algorithm in contract.algorithms:
            for step in algorithm.steps:
                for condition in step['conditions']:
                    for block in condition['criteria']:
                        for criteria in block:
                            if criteria.get('ask_value'):
                                params.add((criteria.get('value_name'),criteria.get('value')))
        return [{"name": n, "value": v} for n, v in params]

    def examine(self, contract, form):
        categories = form.categories.split('|')
        patient = contract.patient

        algorithms = filter(lambda algorithm: any([cat in algorithm.categories.split('|') for cat in categories]),
                            patient.algorithms)

        fired = False
        for algorithm in algorithms:
            fired = fired or self.run(algorithm)

        if not fired and form.thanks_text:
            self.medsenger_api.send_message(contract.id, text=form.thanks_text, only_patient=True, action_deadline=time.time() + 60 * 60)

    def hook(self, contract, category_name):
        patient = contract.patient

        algorithms = list(
            filter(lambda algorithm: category_name in algorithm.categories.split('|'), patient.algorithms))

        for algorithm in algorithms:
            self.run(algorithm)

        return True

    def check_inits(self, algorithm, contract):
        if 'init' in algorithm.categories.split('|') and algorithm.contract_id:
            for step in algorithm.steps:
                for condition in step['conditions']:
                    if any(any(criteria['category'] == 'init' for criteria in block) for block in condition['criteria']):
                        for action in condition['positive_actions']:
                            self.run_action(action, contract.id, [], algorithm)

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
            algorithm.description = data.get('description')
            algorithm.categories = data.get('categories')
            algorithm.template_id = data.get('template_id')
            algorithm.initial_step = data.get('steps')[0].get('uid')
            algorithm.current_step = data.get('steps')[0].get('uid')

            if data.get('is_template') and contract.is_admin:
                algorithm.clinics = data.get('clinics')
                algorithm.is_template = True
                algorithm.template_category = data.get('template_category')
            else:
                algorithm.patient_id = contract.patient_id
                algorithm.contract_id = contract.id

            if not algorithm_id:
                self.db.session.add(algorithm)

            self.check_inits(algorithm, contract)
            self.change_step(algorithm, algorithm.initial_step)

            return algorithm
        except Exception as e:
            log(e)
            return None
