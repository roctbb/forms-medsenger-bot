from celery_manager import celery
from medsenger_manager import medsenger_api

@celery.task
def async_order(contract_id, order, agent_id=None, params=None):
    medsenger_api.send_order(contract_id, order, agent_id, params)

@celery.task
def async_record(contract_id, category_name, value, params=None):
    medsenger_api.add_record(contract_id, category_name, value, params)

@celery.task
def async_add_hooks(contract_id, categories):
    medsenger_api.add_hooks(contract_id, categories)

@celery.task
def async_remove_hooks(contract_id, categories):
    medsenger_api.remove_hooks(contract_id, categories)