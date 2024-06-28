import json
import threading
from datetime import timedelta, datetime

from flask import request, abort, jsonify, render_template
from sentry_sdk import capture_exception
import sys, os
from config import *
import os
from helpers.descriptions import generate_contract_description
from helpers.timing import timezone_now, localize

DATACACHE = {}


def get_ui(page, contract, categories='[]', object_id=None, is_preview=False, dashboard_parts=[], role='doctor', params={}):
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
                           is_preview=str(is_preview).lower(), dashboard_parts=json.dumps(dashboard_parts),
                           params=json.dumps(params))


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


def get_next_timestamp(object):
    timetable = object.timetable

    if timetable.get('mode') == 'manual':
        return None

    zone = object.contract.get_actual_timezone()
    now = timezone_now(zone)

    next_run_timestamp = object.next_run_timestamp

    if timetable.get('mode') == 'ndays':
        if not next_run_timestamp:
            if not object.last_sent:
                return now.timestamp()
            next_run_timestamp = object.last_sent.timestamp()

        next_run_timestamp += (24 * 60 * 60) * int(timetable.get('period'))
        return next_run_timestamp

    points = []
    days_delta = 0
    if timetable.get('mode') == 'daily':
        days_delta = 1
        points = [localize(datetime(year=now.year, month=now.month, day=now.day, hour=point['hour'], minute=point['minute'], second=0), zone)
                  for point in timetable['points']]

    if timetable.get('mode') == 'weekly':
        days_delta = 7
        for point in timetable['points']:
            day_diff = point['day'] - now.weekday()
            tmp_day = now + timedelta(days=day_diff)
            tmp_day.replace(hour=point['hour'], minute=point['minute'])

    if timetable.get('mode') == 'monthly':
        days_delta = 30
        points = [localize(datetime(year=now.year, month=now.month, day=point['day'], hour=point['hour'], minute=point['minute'], second=0), zone)
                  for point in timetable['points']]
    if timetable.get('mode') == 'dates':
        points = [localize(datetime.fromtimestamp(point['date'] / 1000), zone)
                  for point in timetable['points']]


    points.sort()
    filtered_points = [point for point in points if point > now]
    if len(filtered_points) > 0:
        next_run_timestamp = filtered_points[0].timestamp()
    else:
        if timetable.get('mode') == 'dates':
            return None
        next_run_timestamp = (points[0] + timedelta(days=days_delta)).timestamp()

    return next_run_timestamp


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


def extract_actions(algorithm):
    actions = []

    def set_action_loc(action, algorithm_id, step_index, condition_index, action_index, action_type, common=False):
        action['loc'] = {
            'algorithm': algorithm_id,
            'step': step_index,
            'condition': condition_index,
            'action': action_index,
            'action_type': action_type,
            'common': common
        }
        return action

    def search_actions_in_conditions(conditions, step_index, common=False):
        for condition_index, condition in enumerate(conditions):
            for action_index, action in enumerate(condition.get('positive_actions', [])):
                actions.append(set_action_loc(action, algorithm.id, step_index, condition_index,
                                              action_index, 'positive_actions', common))
            for action_index, action in enumerate(condition.get('negative_actions', [])):
                actions.append(set_action_loc(action, algorithm.id, step_index, condition_index,
                                              action_index, 'negative_actions', common))
            for action_index, action in enumerate(condition.get('timeout_actions', [])):
                actions.append(set_action_loc(action, algorithm.id, step_index, condition_index,
                                              action_index, 'timeout_actions', common))

    for step_index, step in enumerate(algorithm.steps):
        search_actions_in_conditions(step['conditions'], step_index)

        for action_index, action in enumerate(step.get('timeout_actions', [])):
            actions.append(set_action_loc(action, algorithm.id, step_index, None,
                                          action_index, 'step_timeout_actions'))

    if algorithm.common_conditions:
        search_actions_in_conditions(algorithm.common_conditions, None, True)

    return actions


def toInt(value, default=None):
    try:
        return int(value)
    except:
        return default
