from flask import request, abort
from models import *
from config import *
from helpers import log


def __get_params():
    contract_id = request.args.get('contract_id')
    api_key = request.args.get('api_key')
    agent_token = request.args.get('agent_token')
    source = request.args.get('source')

    if request.is_json and isinstance(request.json, dict):
        if not contract_id:
            contract_id = request.json.get('contract_id')
        if not api_key:
            api_key = request.json.get('api_key')
        if not agent_token:
            agent_token = request.json.get('agent_token')
        if not source:
            source = request.json.get('source')

    return contract_id, api_key, agent_token, source


def __get_contract(contract_manager, contract_id):
    try:
        contract = contract_manager.get(contract_id)

        if not contract.patient_agent_token or not contract.doctor_agent_token:
            contract_manager.request_token(contract, commit=True)

        return contract

    except:
        abort(404)


# decorators
def verify_request(contract_manager, expected_role):
    def request_verifier(func):
        def wrapper(*args, **kargs):
            contract_id, api_key, agent_token, source = __get_params()

            contract = None
            has_access = False

            if expected_role == 'backend':
                if api_key == API_KEY:
                    has_access = True
            else:
                contract = __get_contract(contract_manager, contract_id)

            if expected_role == 'doctor':
                if api_key == API_KEY and source == 'doctor':
                    has_access = True

                if agent_token == contract.doctor_agent_token:
                    has_access = True

            if expected_role == 'patient':
                if api_key == API_KEY and source in ['patient', 'doctor']:
                    has_access = True

                if agent_token in [contract.doctor_agent_token, contract.patient_agent_token]:
                    has_access = True

            if not has_access:
                abort(401)

            try:
                if expected_role == 'backend':
                    return func(request.json)
                else:
                    return func(request.args, request.form, contract, *args, **kargs)
            except Exception as e:
                log(e, True)
                abort(500)

        wrapper.__name__ = func.__name__
        return wrapper
    return request_verifier