import time
from datetime import datetime, timedelta

from methods.action_logging import log_action
from methods.action_runner import run_action
from methods.algorithm_runner import check_criteria, clear_cache, run_algorithm
from sqlalchemy.orm.attributes import flag_modified, flag_dirty

from helpers import log, clear_categories, extract_conditions, extract_actions, extract_date, toInt
from managers.Manager import Manager
from models import Algorithm
from methods.hooks import *


class AlgorithmManager(Manager):
    def __init__(self, *args):
        super(AlgorithmManager, self).__init__()

    def get(self, algorithm_id):
        return Algorithm.query.filter_by(id=algorithm_id).first()

    def detach(self, template_id, contract):
        algorithms = list(filter(lambda x: x.template_id == template_id, contract.patient.algorithms))

        for algorithm in algorithms:
            remove_hooks_before_deletion(algorithm)
            log_action("algorithm", "detach", contract, algorithm)
            self.db.session.delete(algorithm)

        self.__commit__()

    def attach(self, template_id, contract, setup=None):
        algorithm = self.get(template_id)

        if algorithm:
            new_algorithm = algorithm.clone()
            new_algorithm.contract_id = contract.id
            new_algorithm.patient_id = contract.patient.id

            if setup:
                for condition in extract_conditions(algorithm):
                    for block in condition['criteria']:
                        for criteria in block:
                            if criteria.get('ask_value') and setup.get(criteria['value_code']):
                                criteria['value'] = setup.get(criteria['value_code'])

                    actions = extract_actions(algorithm)
                    for action in actions:
                        if action.get('params') and action['params'].get('script_params'):
                            for param in action['params'].get('script_params', []):
                                if setup.get(param['value_code']):
                                    param['value'] = setup.get(param['value_code'])

                attach_date = extract_date(setup.get('algorithm_{}_attach_date'.format(template_id)))
                detach_date = extract_date(setup.get('algorithm_{}_detach_date'.format(template_id)))

                if attach_date:
                    new_algorithm.attach_date = attach_date

                if detach_date:
                    new_algorithm.detach_date = detach_date

            self.db.session.add(new_algorithm)
            self.__commit__()
            self.db.session.refresh(new_algorithm)

            self.change_step(new_algorithm, new_algorithm.initial_step)
            self.check_inits(new_algorithm, contract)
            self.check_init_timeouts(new_algorithm, contract)

            self.__commit__()
            self.db.session.refresh(new_algorithm)
            create_hooks_after_creation(new_algorithm)

            log_action("algorithm", "attach", contract, new_algorithm)

            return True
        else:
            return False

    def clear(self, contract):
        Algorithm.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        clear_contract_hooks(contract)

        log_action("algorithm", "clear", contract)

        return True

    def remove(self, id, contract):

        algorithm = Algorithm.query.filter_by(id=id).first_or_404()

        if algorithm.contract_id != contract.id and not contract.is_admin:
            return None

        remove_hooks_before_deletion(algorithm)

        Algorithm.query.filter_by(id=id).delete()

        self.__commit__()

        log_action("algorithm", "remove", contract, algorithm)

        return id

    def get_templates(self):
        return Algorithm.query.filter_by(is_template=True).all()

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

        categories = []
        conditions = []

        if step and step.get('conditions'):
            conditions += step['conditions']

        if algorithm.common_conditions:
            conditions += algorithm.common_conditions

        for condition in conditions:
            for block in condition['criteria']:
                for k in block:
                    if k.get('category'):
                        categories.append(k['category'])
                    if k.get('right_category'):
                        categories.append(k["right_category"])


        algorithm.categories = "|".join(set(categories))

    def change_step(self, algorithm, step):
        new_step = self.get_step(algorithm, step)

        algorithm.current_step = new_step['uid']

        if new_step.get('reset_minutes'):
            algorithm.timeout_at = time.time() + 60 * toInt(new_step['reset_minutes'], 0)
        else:
            algorithm.timeout_at = 0

        self.update_categories(algorithm)

        for condition in new_step['conditions']:
            if condition.get('timeout_on_init'):
                condition['last_fired'] = int(time.time())
            if any(any(criteria['left_mode'] == 'step_init' for criteria in block) for block in condition['criteria']):
                for action in condition['positive_actions']:
                    run_action(action, algorithm.contract, [], algorithm)
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
            run_action(action, contract, [], algorithm)

        self.__commit__()

    def run(self, algorithm, included_types=[], excluded_types=['exact_date']):
        fired, has_messages = run_algorithm(algorithm, included_types=included_types, excluded_types=excluded_types)

        self.__commit__()

        return fired, has_messages

    def set_params(self, contract, params):

        print(f"Running set_params  {params} for contract ID {contract}")

        def update_condition(condition):
            for block_index, block in enumerate(condition.get('criteria', [])):
                for criteria_index, criteria in enumerate(block):
                    if criteria.get('ask_value'):
                        value_name = criteria.get('value_name')
                        value_code = criteria.get('value_code')

                        if value_code and value_code in params:
                            criteria["value"] = params[value_code]

                        if value_name and value_name in params:
                            criteria["value"] = params[value_name]

        def update_action_params(algorithm):
            actions = extract_actions(algorithm)

            for action in actions:
                if action.get('params') and action['params'].get('script_params'):
                    for param in action['params'].get('script_params', []):
                        value_name = param.get('value_name')
                        value_code = param.get('value_code')

                        if value_code and value_code in params:
                            param["value"] = params[value_code]

                        if value_name and value_name in params:
                            param["value"] = params[value_name]

        for algorithm in contract.algorithms:
            for step_index, step in enumerate(algorithm.steps):
                for condition_index, condition in enumerate(step['conditions']):
                    update_condition(condition)

            if algorithm.common_conditions:
                for condition_index, condition in enumerate(algorithm.common_conditions):
                    update_condition(condition)

            update_action_params(algorithm)

            try:
                flag_modified(algorithm, "steps")
                flag_modified(algorithm, "common_conditions")
            except Exception as e:
                log(e, False)

        self.__commit__()

    def search_params(self, contract):
        params = {}

        def search_condition_param(condition, step_index, condition_index, common=False):
            for block_index, block in enumerate(condition.get('criteria', [])):
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

        def search_actions_params(algorithm):
            actions = extract_actions(algorithm)

            for action in actions:
                if action.get('params') and action['params'].get('script_params'):
                    for param in action['params']['script_params']:
                        pair = (param.get('value_name'), param.get('value'), param.get('value_code'))

                        if pair in params:
                            params[pair]['locations'].append(action['loc'])
                        else:
                            params.update({
                                pair: {
                                    'name': pair[0],
                                    'value': pair[1],
                                    'code': pair[2],
                                    'locations': [action['loc']]
                                }
                            })

        for algorithm in contract.algorithms:
            for step_index, step in enumerate(algorithm.steps):
                for condition_index, condition in enumerate(step['conditions']):
                    search_condition_param(condition, step_index, condition_index)

            if algorithm.common_conditions:
                for condition_index, condition in enumerate(algorithm.common_conditions):
                    search_condition_param(condition, None, condition_index, True)

            search_actions_params(algorithm)

        return [value for key, value in params.items()]

    def examine(self, contract, form):
        categories = form.categories.split('|')
        categories.append('action')

        patient = contract.patient

        algorithms = filter(lambda algorithm: any([cat in algorithm.categories.split('|') for cat in categories]),
                            patient.algorithms)

        has_message_to_patient = False

        for algorithm in algorithms:
            result, has_message = self.run(algorithm)
            has_message_to_patient = has_message_to_patient or has_message

        if not has_message_to_patient and form.thanks_text:
            self.medsenger_api.send_message(contract.id, text=form.thanks_text, only_patient=True,
                                            action_deadline=time.time() + 60 * 60)

        clear_cache(contract.id)
        return True

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
                        map(lambda x: check_criteria(x, contract.id, [], [], category_names,
                                                     algorithm=algorithm, is_init=True), block))) for block in
                    condition['criteria']])

                if result:
                    for action in condition['positive_actions']:
                        run_action(action, contract, [], algorithm)

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

                remove_hooks_before_deletion(algorithm)

                if algorithm.contract_id != contract.id and not contract.is_admin:
                    return None

            algorithm.title = data.get('title')
            algorithm.steps = data.get('steps')
            algorithm.common_conditions = data.get('common_conditions')
            algorithm.description = data.get('description')
            algorithm.categories = clear_categories(data.get('categories'))
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
                if algorithm_id:
                    log_action("algorithm", "edit", contract, algorithm)
                else:
                    log_action("algorithm", "create", contract, algorithm)

            if algorithm.contract_id == contract.id:
                if not algorithm.current_step:
                    algorithm.current_step = data.get('steps')[0].get('uid')
                    self.change_step(algorithm, algorithm.initial_step)
                if not algorithm_id:
                    self.check_inits(algorithm, contract)
                    self.check_init_timeouts(algorithm, contract)
                self.update_categories(algorithm)

                self.__commit__()

                create_hooks_after_creation(algorithm)

            return algorithm
        except Exception as e:
            log(e)
            return None
