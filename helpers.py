from datetime import datetime
from flask import request, abort, jsonify, render_template
from config import *


def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")


def log(error, terminating=False):
    if terminating:
        print(gts(), error, "CRITICAL")
    else:
        print(gts(), error)


# decorators
def verify_args(func):
    def wrapper(*args):
        if request.args.get('api_key') != API_KEY:
            abort(401)
        try:
            return func(request.args, request.form, *args)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def only_doctor_args(func):
    def wrapper(*args):
        if request.args.get('api_key') != API_KEY:
            abort(401)
        if request.args.get('source') == 'patient':
            abort(401)
        try:
            return func(request.args, request.form, *args)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def verify_json(func):
    def wrapper(*args):
        if request.json.get('api_key') != API_KEY:
            abort(401)
        try:
            return func(request.json, *args)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper
