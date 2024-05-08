from flask import Blueprint

from manage import *
from helpers import *
from decorators import verify_request
from tasks import tasks


actions_blueprint = Blueprint('actions_endpoints', __name__, template_folder='templates')

@actions_blueprint.route('/settings', methods=['GET'])
@verify_request(contract_manager, 'backend')
def get_settings(args, form, contract):
    return get_ui('settings', contract, medsenger_api.get_categories(), role='doctor')


@actions_blueprint.route('/preview_form/<form_id>', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def form_preview_page(args, form, contract, form_id):
    return get_ui('form', contract, medsenger_api.get_categories(), form_id, True, role='doctor')


@actions_blueprint.route('/preview_form/<form_id>/<record_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def form_preview_page_from_record(args, form, contract, form_id, record_id):
    record = medsenger_api.get_record_by_id(contract.id, record_id)
    answers = record['params'].get('form_answers', {}) if record['params'] else {}
    return get_ui('form', contract, medsenger_api.get_categories(), form_id, True,
                  params={'answers': answers}, role='patient')


@actions_blueprint.route('/form/<form_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def form_page(args, form, contract, form_id):
    return get_ui('form', contract, medsenger_api.get_categories(), form_id, role='patient')


@actions_blueprint.route('/outsource_form/<form_id>', methods=['GET'])
def outsource_form_page(form_id):
    return get_ui('outsource-form', None, [], form_id)


@actions_blueprint.route('/medicine/<medicine_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def medicine_page(args, form, contract, medicine_id):
    contract = contract_manager.get(args.get('contract_id'))
    medicine = medicine_manager.get(medicine_id)

    if medicine.verify_dose:
        return get_ui('verify-dose', contract, object_id=medicine_id)

    medicine_manager.submit(medicine_id, contract.id)

    if contract.tasks and 'medicine-{}'.format(medicine_id) in contract.tasks:
        medsenger_api.finish_task(contract.id, contract.tasks['medicine-{}'.format(medicine_id)])

    tasks.request_cache_update.delay(contract.id)

    return get_ui('done', contract, [], role='patient')


@actions_blueprint.route('/medicine-manager', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def medicine_editor_page(args, form, contract):
    return get_ui('settings', contract, medsenger_api.get_categories(), dashboard_parts=['meds'], role='doctor')


@actions_blueprint.route('/form-manager', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def forms_editor_page(args, form, contract):
    return get_ui('settings', contract, medsenger_api.get_categories(), dashboard_parts=['forms', 'algorithms'],
                  role='doctor')


@actions_blueprint.route('/reminder-manager', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def notification_editor_page(args, form, contract):
    return get_ui('settings', contract, medsenger_api.get_categories(), dashboard_parts=['reminders'], role='doctor')


@actions_blueprint.route('/medicines-list', methods=['GET'])
@verify_request(contract_manager, 'patient')
def medicines_list_page(args, form, contract):
    return get_ui('medicines-list', contract, medsenger_api.get_categories(), role='patient')





@actions_blueprint.route('/reminder/template/<template_id>', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def create_reminder_page(args, form, contract, template_id):
    return get_ui('create-reminder', contract, medsenger_api.get_categories(), template_id, role='doctor')


@actions_blueprint.route('/reminder/<reminder_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def reminder_page(args, form, contract, reminder_id):
    return get_ui('confirm-reminder', contract, medsenger_api.get_categories(), reminder_id, role='patient')

# examinations


@actions_blueprint.route('/examinations-list', methods=['GET'])
@verify_request(contract_manager, 'patient')
def examinations_list_page(args, form, contract):
    contract = contract_manager.get(args.get('contract_id'))
    return get_ui('examinations-list', contract, medsenger_api.get_categories())


@actions_blueprint.route('/examination-manager', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def examination_editor_page(args, form, contract):
    return get_ui('settings', contract, medsenger_api.get_categories(), dashboard_parts=['examinations'], role='doctor')


@actions_blueprint.route('/examination/<examination_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def examination_page(args, form, contract, examination_id):
    return get_ui('examination', contract, medsenger_api.get_categories(), examination_id, role='patient')


@actions_blueprint.route('/examination/template/<template_id>', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def attach_examination_page(args, form, contract, template_id):
    return get_ui('attach-examination', contract, medsenger_api.get_categories(), template_id,
                  role='doctor', dashboard_parts=['examinations'])
