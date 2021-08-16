import json
import threading
from datetime import datetime
from flask import request, abort, jsonify, render_template
from config import *
from sentry_sdk import capture_exception
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


def get_ui(page, contract, categories='[]', object_id=None):
    return render_template('index.html', page=page, object_id=object_id, contract_id=contract.id, api_host=MAIN_HOST.replace('8001', '8000'), local_host=LOCALHOST, agent_token=contract.agent_token,
                           agent_id=AGENT_ID, categories=json.dumps(categories), is_admin=str(bool(contract.is_admin)).lower(), lc=dir_last_updated('static'), clinic_id=contract.clinic_id)


def delayed(delay, f, args):
    timer = threading.Timer(delay, f, args=args)
    timer.start()


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


def generate_description(criteria, l_value, r_value, category_names, current_answer):
    if criteria.get('left_mode') == 'value' and criteria.get('right_mode') == 'value' and criteria.get('sign') in ['equal', 'contains'] and current_answer:
        if current_answer['params']['type'] != 'checkbox':
            return "<strong>{}</strong>: {}".format(current_answer['params']['question_text'], current_answer['params']['answer'])
        else:
            return "{}".format(current_answer['params']['answer'])

    signs = {
        "equal": "равно значению",
        "not_equal": "не равно значению",
        "greater": "больше, чем",
        "less": "меньше, чем",
        "greater_or_equal": "больше или равно значению",
        "less_or_equal": "меньше или равно значению",
        "contains": "содержит значение",
        "date_equal": "равно значению",
        "date_not_equal": "не равно значению",
        "date_greater": "больше, чем",
        "date_less": "меньше, чем",
        "date_greater_or_equal": "больше или равно значению",
        "date_less_or_equal": "меньше или равно значению",
    }

    left_modes = {
        "value": "Значение ",
        "sum": "Сумма ",
        "difference": "Разность крайних значений ",
        "delta": "Разброс ",
        "average": "Среднее значение ",
        "max": "Максимальному значение ",
        "min": "Минимальное значение "
    }

    right_modes = {
        "sum": "суммы",
        "difference": "разности крайних значений",
        "delta": "разброса",
        "average": "среднего",
        "max": "максимального",
        "min": "минимального"
    }

    right_dimensions = {
        'hours': 'часов',
        'times': 'раз'
    }

    LEFT_MODE = left_modes.get(criteria.get('left_mode'))
    LEFT_CATEGORY = category_names.get(criteria.get('category'))
    SIGN = signs[criteria.get('sign')]

    RIGHT_MODE = right_modes[criteria.get('right_mode')]
    MULTIPLIER = float(criteria.get('multiplier')) * 100
    RIGHT_DIM = right_dimensions[criteria.get('right_dimension')]

    if criteria.get('right_dimension') == 'hours':
        RIGHT_CNT = int(criteria.get('right_hours'))
        if RIGHT_CNT % 10 == 1 and RIGHT_CNT % 100 // 10 != 1:
            RIGHT_DIM = 'час'
        elif RIGHT_CNT % 10 in range(2, 5) and RIGHT_CNT % 100 // 10 != 1:
            RIGHT_DIM = 'часа'
    else:
        RIGHT_CNT = int(criteria.get('right_times'))
        if RIGHT_CNT % 10 in range(2, 5) and RIGHT_CNT % 100 // 10 != 1:
            RIGHT_DIM = 'раза'

    if criteria.get('sign') not in ['equal', 'contains'] or criteria.get('left_mode') != 'value':
        comment = "{} '{}' (<strong>{:.2f}</strong>) {} ".format(LEFT_MODE, LEFT_CATEGORY, l_value, SIGN)
    else:
        comment = "{} '{}' {} ".format(LEFT_MODE, LEFT_CATEGORY, SIGN)

    if criteria.get('right_mode') in ['value', 'category_value']:
        comment += "<strong>{:.2f}</strong>".format(criteria.get('value'))
    else:
        comment += "{}% от {} за {} {} (<strong>{:.2f}</strong>)".format(MULTIPLIER, RIGHT_MODE, RIGHT_CNT, RIGHT_DIM, r_value)

        if criteria.get('right_category'):
            comment += " '{}'".format(category_names.get(criteria.get('right_category')))

    return comment


def get_step(algorithm, step=None):
    if not step:
        step = algorithm.current_step

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
