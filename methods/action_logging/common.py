from tasks import threader
from .algorithms import *
from .forms import *
from .medicines import *
from .examinations import *


def log_action(object_type, action, contract, objects=None):
    text, params = None, None

    loggers = {
        "algorithm": log_algorithm_action,
        "form": log_form_action,
        "medicine": log_medicine_action,
        "examination": log_examination_action
    }

    if objects and object_type in loggers:
        text, params = loggers[object_type](action, contract, objects)

    if text:
        threader.async_record.delay(contract.id, 'doctor_action', text, params=params)
