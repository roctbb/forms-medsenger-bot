from sqlalchemy.orm.attributes import flag_modified

from helpers import *
import time
from datetime import datetime, timedelta
from infrastructure import medsenger_api
from methods.action_runner import run_action


def clear_cache(contract_id):
    to_del = []

    for A in DATACACHE:
        if A[2] == contract_id:
            to_del.append(A)

    for k in to_del:
        del DATACACHE[k]


def get_from_cache(A):
    if A in DATACACHE:
        t, answer = DATACACHE[A]

        if time.time() - t < 30:
            return answer
        else:
            del DATACACHE[A]
    return None


def save_to_cache(A, value):
    for k, v in list(DATACACHE.items()):
        if time.time() - v[0] > 30:
            del DATACACHE[k]

    DATACACHE[A] = (int(time.time()), value)

    return value


def get_values(category_name, mode, contract_id, dimension='hours', hours=1, times=1, algorithm=None,
               offset_dim='times', offset_count=0, check_value=None, sign=None, zone=None):
    k = (category_name, mode, contract_id, dimension, hours, times, offset_dim, offset_count)
    cached = get_from_cache(k)
    if cached != None:
        return cached

    if category_name == "exact_date":
        return [datetime.now().strftime("%Y-%m-%d")], None
    if category_name == "contract_start_date":
        return save_to_cache(k, ([medsenger_api.get_patient_info(contract_id).get('start_date')], None))
    if category_name == "contract_end_date":
        return save_to_cache(k, ([medsenger_api.get_patient_info(contract_id).get('end_date')], None))

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
        answer = medsenger_api.get_records(contract_id, category_name, group=True, limit=1)
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
            answer = medsenger_api.get_records(contract_id, category_name,
                                               time_from=int(
                                                   (datetime.now() - timedelta(hours=hours)).timestamp()),
                                               offset=offset)
        else:
            answer = medsenger_api.get_records(contract_id, category_name, limit=times,
                                               time_to=int(time_to.timestamp()),
                                               offset=offset)
    if not answer:
        save_to_cache(k, (None, None))
        return None, None

    values = list(map(lambda x: x['value'], answer['values']))
    objects = answer['values']

    if not values:
        answer = None, None
    elif (mode == 'value' or mode == 'count') and (
            time.time() - int(answer['values'][0].get('timestamp')) > 60 * 60 * 24 or time.time() - int(
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
    elif mode == 'count':
        answer = [len([x for x in values if check_values(x, check_value, sign)])], None
    elif mode == 'average':
        avg = sum(values) / len(values)
        answer = [round(avg, 2)], None
    elif mode == 'max':
        answer = [max(values)], None
    elif mode == 'min':
        answer = [min(values)], None
    else:
        answer = None, None

    return save_to_cache(k, answer)


def check_values(left, right, sign, modifier=0, multiplier=1):
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
            try:
                leftc = extract_date(left)
                rightc = (extract_date(right) + timedelta(days=modifier)).date()
                signc = sign.replace('date_', '')

                conditions.append((leftc, rightc, signc))
            except:
                pass
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


def check_criteria(criteria, contract_id, buffer, descriptions, category_names, algorithm=None, contract=None,
                   is_init=False, record_ids=[]):
    category_name = criteria.get('category')
    mode = criteria.get('left_mode')

    if mode == 'step_init':
        return False

    if mode == 'init':
        return is_init

    if mode != 'time':
        dimension = criteria.get('left_dimension')
        offset_dim = criteria.get('left_offset_dimension', 'times')
        offset_count = criteria.get('left_offset', 0)
        check_value = criteria.get('check_value')
        sign = criteria.get('left_sign')

        if dimension == 'hours':
            left_values, objects = get_values(category_name, criteria['left_mode'], contract_id, dimension,
                                              hours=criteria.get('left_hours'),
                                              offset_dim=offset_dim, offset_count=offset_count,
                                              algorithm=algorithm, check_value=check_value, sign=sign)
        elif dimension == 'times':
            left_values, objects = get_values(category_name, criteria['left_mode'], contract_id, dimension,
                                              times=criteria.get('left_times'),
                                              offset_dim=offset_dim, offset_count=offset_count,
                                              algorithm=algorithm, check_value=check_value, sign=sign)
        else:
            left_values, objects = get_values(category_name, criteria['left_mode'], contract_id, 'hours',
                                              hours=criteria.get('left_for') * 24,
                                              offset_dim=offset_dim, offset_count=offset_count,
                                              algorithm=algorithm, check_value=check_value, sign=sign)

        if criteria['right_mode'] == 'value':
            right_values = [criteria.get('value')]
        else:
            right_category = criteria.get('right_category')
            dimension = criteria.get('right_dimension')
            offset_dim = criteria.get('right_offset_dimension', 'times')
            offset_count = criteria.get('right_offset', 0)

            if right_category:
                if dimension == 'hours':
                    right_values, _ = get_values(right_category, criteria['right_mode'], contract_id,
                                                 dimension,
                                                 hours=criteria.get('right_hours'),
                                                 offset_dim=offset_dim, offset_count=offset_count,
                                                 algorithm=algorithm)
                else:
                    right_values, _ = get_values(right_category, criteria['right_mode'], contract_id,
                                                 dimension=dimension, times=criteria.get('right_times'),
                                                 offset_dim=offset_dim, offset_count=offset_count,
                                                 algorithm=algorithm)
            else:
                if dimension == 'hours':
                    right_values, _ = get_values(category_name, criteria['right_mode'], contract_id,
                                                 dimension=dimension, hours=criteria.get('right_hours'),
                                                 offset_dim=offset_dim, offset_count=offset_count,
                                                 algorithm=algorithm)
                else:
                    right_values, _ = get_values(category_name, criteria['right_mode'], contract_id,
                                                 dimension=dimension, times=criteria.get('right_times'),
                                                 offset_dim=offset_dim, offset_count=offset_count,
                                                 algorithm=algorithm)
        if not right_values or not left_values:
            return False

        occurred = 0

        for i in range(len(left_values)):
            lvalue = left_values[i]

            for rvalue in right_values:
                modifier = 0
                multiplier = criteria.get('multiplier', 1) if criteria.get('multiplier', 1) else 1
                if criteria.get('right_mode') != 'value':
                    modifier = criteria.get('value', 0)
                result = check_values(lvalue, rvalue, criteria['sign'], modifier, multiplier)

                if result:

                    current_answer = None
                    if objects:
                        record_ids.extend([object['id'] for object in objects if object.get('id')])
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
                    occurred += 1

        should_occur = 1
        if mode == "value" and criteria.get('should_occur') and criteria.get('should_occur').isnumeric():
            should_occur = int(criteria.get('should_occur'))

        return occurred >= should_occur

    else:
        date = criteria.get('value')
        add_hours = criteria.get('right_hours')
        sign = criteria.get('sign')

        date_obj = localize(datetime.strptime(date, '%Y-%m-%d'), algorithm.contract.timezone) + timedelta(
            hours=add_hours)
        now_obj = timezone_now(algorithm.contract.get_actual_timezone())

        if sign == 'equal' and 0 <= (now_obj - date_obj).total_seconds() < 60 * 60:
            return True
        if sign == 'greater' and (now_obj - date_obj).total_seconds() > 0:
            return True
        if sign == 'less' and (now_obj - date_obj).total_seconds() < 0:
            return True
        return False


def should_observe_group(group, included_types, excluded_types):
    categories_in_group = set()

    for criteria in group:
        categories_in_group.add(criteria.get('category'))

    if included_types and not categories_in_group.intersection(included_types):
        return False

    if excluded_types and not categories_in_group.difference(excluded_types):
        return False

    return True

def check_criteria_groups(or_groups, contract, additions, descriptions, category_names, algorithm):
    all_record_ids = set()
    result = False
    for or_group in or_groups:
        and_result = True
        group_records_ids = None
        for criteria in or_group:
            record_ids = []
            and_result = and_result and check_criteria(criteria, contract.id, additions, descriptions,
                                                       category_names,
                                                       algorithm=algorithm, record_ids=record_ids)

            if group_records_ids is None:
                group_records_ids = set(record_ids)
            else:
                group_records_ids = group_records_ids & set(record_ids)

        result = result or and_result
        all_record_ids = all_record_ids | group_records_ids

    record_ids = list(all_record_ids)

    return result, record_ids

def run_algorithm(algorithm, included_types=[], excluded_types=['exact_date']):
    from managers import AlgorithmManager

    algorithm_manager = AlgorithmManager()

    included_types = set(included_types)
    excluded_types = set(excluded_types)

    current_step = algorithm_manager.get_step(algorithm)
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
                          medsenger_api.get_categories()}

        or_groups = [group for group in criteria if
                     should_observe_group(group, included_types, excluded_types)]

        result, record_ids = check_criteria_groups(or_groups, contract, additions, descriptions,
                                                          category_names, algorithm)

        if result:
            if not condition.get('skip_additions'):
                for addition in additions:
                    medsenger_api.send_addition(contract.id, addition['id'], {
                        "algorithm_id": algorithm.id,
                        "comment": addition["comment"]
                    })
            fired = True

            if not bypass:
                for action in condition.get('positive_actions', []):
                    has_message = run_action(action, contract, descriptions, algorithm, record_ids)
                    has_message_to_patient = has_message_to_patient or has_message
                condition['last_fired'] = int(time.time())
        else:
            for action in condition.get('negative_actions', []):
                run_action(action, contract, descriptions, algorithm, record_ids)
    if fired:
        try:
            flag_modified(algorithm, "steps")
            flag_modified(algorithm, "common_conditions")
        except Exception as e:
            log(e, False)

    return fired, has_message_to_patient
