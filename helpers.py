import json
import threading
from datetime import datetime, timedelta
from flask import request, abort, jsonify, render_template
from config import *
from sentry_sdk import capture_exception
from pytz import timezone
import sys, os

DATACACHE = {}


def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")


def log(error, terminating=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    if PRODUCTION:
        capture_exception(error)

    if terminating:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error, "CRITICAL")
    else:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error)


# decorators
def verify_args(func):
    def wrapper(*args, **kargs):
        if not request.args.get('contract_id'):
            abort(422)
        if request.args.get('api_key') != API_KEY:
            abort(401)
        try:
            return func(request.args, request.form, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def only_doctor_args(func):
    def wrapper(*args, **kargs):
        if not request.args.get('contract_id'):
            abort(422)
        if request.args.get('api_key') != API_KEY:
            abort(401)
        # if request.args.get('source') == 'patient':
        #    abort(401)
        try:
            return func(request.args, request.form, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def verify_json(func):
    def wrapper(*args, **kargs):
        if not request.json.get('contract_id') and "status" not in request.url:
            abort(422)
        if request.json.get('api_key') != API_KEY:
            abort(401)
        # return func(request.json, *args, **kargs)
        try:
            return func(request.json, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def get_ui(page, contract, categories='[]', object_id=None, is_preview=False, dashboard_parts=[]):
    return render_template('index.html', page=page, object_id=object_id,
                           contract_id=contract.id if contract else 'undefined',
                           api_host=MAIN_HOST.replace('8001', '8000'), local_host=LOCALHOST,
                           agent_token=contract.agent_token if contract else 'undefined',
                           agent_id=AGENT_ID, categories=json.dumps(categories),
                           is_admin=str(bool(contract.is_admin)).lower() if contract else 'false',
                           lc=dir_last_updated('static'), clinic_id=contract.clinic_id if contract else 'undefined',
                           is_preview=str(is_preview).lower(), dashboard_parts=json.dumps(dashboard_parts))


def delayed(delay, f, args):
    timer = threading.Timer(delay, f, args=args)
    timer.start()


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


def generate_event_description(criteria, l_value, r_value, category_names, current_answer):
    if criteria.get('left_mode') == 'value' and criteria.get('right_mode') == 'value' and criteria.get('sign') in [
        'equal', 'contains'] and current_answer:
        if not current_answer.get('params', {}).get('type'):
            return ""

        return current_answer['value'] + "."

    signs = {
        "equal": "равно",
        "not_equal": "не равно",
        "greater": "больше",
        "less": "меньше",
        "greater_or_equal": "больше или равно",
        "less_or_equal": "меньше или равно",
        "contains": "содержит",
        "date_equal": "равно",
        "date_not_equal": "не равно",
        "date_greater": "больше",
        "date_less": "меньше",
        "date_greater_or_equal": "больше или равно",
        "date_less_or_equal": "меньше или равно",
    }

    left_modes = {
        "value": "Значение ",
        "category_value": "Значение ",
        "sum": "Сумма ",
        "difference": "Разность крайних значений ",
        "delta": "Разброс ",
        "average": "Среднее значение ",
        "count": "Количество значений ",
        "max": "Максимальному значение ",
        "min": "Минимальное значение "
    }

    right_modes = {
        "sum": "сумме",
        "difference": "разности крайних значений",
        "delta": "разбросу",
        "count": "количеству значений",
        "average": "среднему значению",
        "max": "максимальному значению",
        "min": "минимальному значению"
    }

    LEFT_MODE = left_modes.get(criteria.get('left_mode'))
    LEFT_CATEGORY = category_names.get(criteria.get('category'))
    SIGN = signs[criteria.get('sign')]

    if criteria.get('sign') not in ['equal', 'contains'] or criteria.get('left_mode') != 'value':
        comment = "{} '{}' (<strong>{}</strong>) {} ".format(LEFT_MODE, LEFT_CATEGORY, l_value, SIGN)
    else:
        comment = "{} '{}' {} ".format(LEFT_MODE, LEFT_CATEGORY, SIGN)

    if criteria.get('right_mode') in ['value', 'category_value']:
        comment += "<strong>{}</strong>".format(criteria.get('value'))
    else:
        comment += "{} за {} часа (ов) (<strong>{}</strong>)".format(right_modes[criteria.get('right_mode')],
                                                                     criteria.get('right_hours'), r_value)

        if criteria.get('right_category'):
            comment += " '{}'".format(category_names.get(criteria.get('right_category')))

    return comment


def generate_contract_description(contract):
    description = ""

    if contract.forms:
        description += 'Назначены опросники:<br> - '
        description += '<br> - '.join(map(lambda x: x.get_description(), contract.forms))

        description += '<br><br>'
    else:
        description += 'Опросников пока не назначено. <br>'

    if contract.medicines:
        description += 'Назначены лекарства:<br> - '
        description += '<br> - '.join(map(lambda x: x.get_description(), contract.medicines))

        description += '<br>'
    else:
        description += 'Лекарств пока не назначено. '

    return description


def get_step(algorithm, step=None):
    if not step:
        step = algorithm.current_step

    if not step:
        step = algorithm.initial_step

    return next(s for s in algorithm.steps if s['uid'] == step)


def generate_timetable(start, end, times):
    if times < 1:
        return {
            "mode": "manual"
        }

    timetable = {
        "mode": "daily",
        "points": []
    }

    try:
        step = (end - start) / (times - 1)

        pos = start
        while pos <= end:
            timetable['points'].append({
                "hour": int(pos),
                "minute": int((pos - int(pos)) * 60)
            })

            pos += step
    except:
        timetable['points'].append({
            "hour": start,
            "minute": 0
        })

    return timetable


def timezone_now(zone=None):
    if isinstance(zone, str) and zone:
        tz = timezone(zone)
    elif zone:
        tz = zone
    else:
        tz = timezone('Europe/Moscow')

    return datetime.now(tz)


def localize(d, zone=None):
    if isinstance(zone, str) and zone:
        tz = timezone(zone)
    elif zone:
        tz = zone
    else:
        tz = timezone('Europe/Moscow')

    return tz.localize(d)


def fullfill_message(text, contract, medsenger_api):
    def fullfill(text, info, a, b):
        L = b.split('.')
        v = info
        for c in L:
            v = v.get(c)

            if not v:
                break

        return text.replace(a, str(v))

    keys = {
        'CONTRACT_DAYS': 'days',
        'PATIENT_NAME': 'name',
        'DOCTOR_NAME': 'doctor_name',
        'SCENARIO_NAME': 'scenario.name',
        'DOCTOR_PHONE': 'doctor_phone'
    }

    info = None

    for key in keys:
        if key in text:
            if not info:
                info = medsenger_api.get_patient_info(contract.id)
            text = fullfill(text, info, key, keys[key])

    if 'CONTRACT_DESCRIPTION' in text:
        text = text.replace('CONTRACT_DESCRIPTION', generate_contract_description(contract))

    return text


def clear_categories(categories_string):
    if categories_string:
        return '|'.join(set(categories_string.strip('|').split('|')))
    return categories_string
