from manage import app, celery, form_manager, algorithm_manager, examination_manager, contract_manager, medsenger_api
import time


@celery.task
def submit_form(chain, answers, form_id, contract_id):
    if not chain:
        return chain

    with app.app_context():
        form = form_manager.get(form_id)
        return form_manager.submit(answers, form, contract_id)


@celery.task
def examine_form(chain, form_id, contract_id):
    if not chain:
        return chain

    with app.app_context():
        contract = contract_manager.get(contract_id)
        form = form_manager.get(form_id)
        return algorithm_manager.examine(contract, form)


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
