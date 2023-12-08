import json
import threading
from flask import request, abort, jsonify, render_template
from config import *
from sentry_sdk import capture_exception
import sys, os

from helpers import *

DATACACHE = {}

def log(error, terminating=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    if PRODUCTION:
        capture_exception(error)

    if terminating:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error, "CRITICAL")
    else:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error)


def get_ui(page, contract, categories='[]', object_id=None, is_preview=False, dashboard_parts=[], role='doctor'):
    token = 'undefined'

    if contract:
        if role == 'doctor':
            token = contract.doctor_agent_token
        else:
            token = contract.patient_agent_token

    return render_template('index.html', page=page, object_id=object_id,
                           contract_id=contract.id if contract else 'undefined',
                           api_host=MAIN_HOST, localhost=LOCALHOST, jshost=JSHOST,
                           agent_token=token,
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


def extract_conditions(algorithm):
    conditions = []

    for step in algorithm.steps:
        conditions.extend(step['conditions'])

    if algorithm.common_conditions:
        conditions.extend(algorithm.common_conditions)

    return conditions