from manage import app, celery, form_manager, algorithm_manager, examination_manager, contract_manager, medsenger_api
from config import DYNAMIC_CACHE


@celery.task
def submit_form(chain, answers, form_id, contract_id, submit_from_patient=True):
    if not chain:
        return chain

    with app.app_context():
        form = form_manager.get(form_id)
        return form_manager.submit(answers, form, contract_id, submit_from_patient)


@celery.task
def request_cache_update(contract_id):
    if DYNAMIC_CACHE:
        medsenger_api.update_cache(contract_id)


@celery.task
def request_chained_cache_update(chain, contract_id):
    if DYNAMIC_CACHE:
        medsenger_api.update_cache(contract_id)

    return chain


@celery.task
def examine_form(chain, form_id, contract_id, submit_from_patient=True):
    if not chain:
        return chain

    with app.app_context():
        contract = contract_manager.get(contract_id)
        form = form_manager.get(form_id)
        return algorithm_manager.examine(contract, form, submit_from_patient)


@celery.task
def submit_examination(chain, files, examination_id, contract_id, date):
    if not chain:
        return chain

    with app.app_context():
        examination = examination_manager.get(examination_id)
        return examination_manager.submit(examination, files, contract_id, date)


@celery.task
def examine_contract_tasks(chain, form_id, contract_id):
    if not chain:
        return chain

    with app.app_context():
        contract = contract_manager.get(contract_id)

        if contract.tasks and 'form-{}'.format(form_id) in contract.tasks:
            medsenger_api.finish_task(contract.id, contract.tasks['form-{}'.format(form_id)])
        return True


@celery.task
def examine_hook(contract_id, category_names):
    with app.app_context():
        contract = contract_manager.get(contract_id)
        return algorithm_manager.hook(contract, category_names)


@celery.task
def run_algorithm(chain, algorithm_id, included_categories=[], excluded_categories=[]):
    if not chain:
        return chain

    with app.app_context():
        return algorithm_manager.run(algorithm_manager.get(algorithm_id), included_categories, excluded_categories)


@celery.task
def run_examination(chain, examination_id):
    if not chain:
        return chain

    with app.app_context():
        return examination_manager.run(examination_manager.get(examination_id))
