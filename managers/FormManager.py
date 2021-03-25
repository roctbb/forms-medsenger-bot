import time
from copy import copy
from datetime import datetime
from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Form


class FormManager(Manager):
    def __init__(self, *args):
        super(FormManager, self).__init__(*args)

    def get(self, form_id):
        return Form.query.filter_by(id=form_id).first_or_404()

    def get_templates(self):
        return Form.query.filter_by(is_template=True).all()

    def remove(self, id, contract):

        form = Form.query.filter_by(id=id).first_or_404()

        if form.contract_id != contract.id and not contract.is_admin:
            return None

        if form.contract_id:
            self.medsenger_api.remove_hooks(contract.id, form.categories.split('|'))

        Form.query.filter_by(id=id).delete()

        self.__commit__()
        return id

    def detach(self, template_id, contract):
        forms = list(filter(lambda x: x.template_id == template_id, contract.patient.forms))

        for form in forms:
            form.delete()

        self.__commit__()

    def attach(self, template_id, contract):
        form = self.get(template_id)

        if form:
            new_form = form.clone()
            new_form.contract_id = contract.id
            new_form.patient_id = contract.patient.id

            if new_form.categories:
                self.medsenger_api.add_hooks(contract.id, new_form.categories.split('|'))

            self.db.session.add(new_form)
            self.__commit__()

            return new_form
        else:
            return False

    def run(self, form, commit=True, contract_id=None):

        text = 'Пожалуйста, заполните опросник "{}".'.format(form.title)
        action = 'form/{}'.format(form.id)
        action_name = 'Заполнить опросник'

        if not contract_id:
            deadline = self.calculate_deadline(form.timetable)
            contract_id = form.contract_id
        else:
            deadline = None

        result = self.medsenger_api.send_message(contract_id, text, action, action_name, True, False, True, deadline)

        if result:
            form.last_sent = datetime.now()

            if commit:
                self.__commit__()

        return result

    def check_warning(self, form):
        if form.warning_days > 0 and form.warning_timestamp == 0:
            if time.time() - form.filled_timestamp > 24 * 60 * 60 * form.warning_days:
                form.warning_timestamp = int(time.time())

                self.medsenger_api.send_message(form.contract_id,
                                                "Пациент не заполнял опросник {} уже {} дней.".format(form.title,
                                                                                                      form.warning_days))
                self.__commit__()

    def submit(self, answers, form_id, contract_id):
        form = Form.query.filter_by(id=form_id).first_or_404()
        form.warning_timestamp = 0
        form.filled_timestamp = int(time.time())

        packet = []

        for field in form.fields:
            if answers.get(field['uid']) and answers.get(field['uid']) != False:
                if field['type'] == 'radio':
                    category = field['params']['variants'][answers[field['uid']]]['category']

                    if category == 'none':
                        continue

                    value = field['params']['variants'][answers[field['uid']]]['category_value']
                    packet.append((category, value, {
                        "question_uid": field['uid']
                    }))
                elif field['type'] == 'checkbox':
                    category = field['category']
                    value = field.get('category_value')

                    if not value:
                        continue

                    packet.append((category, value, {
                        "question_iud": field['uid']
                    }))
                else:
                    category = field['category']
                    packet.append((category, answers[field['uid']], {
                        "question_uid": field['uid']
                    }))


        packet.append(('action', 'Заполнение опросника ID {}'.format(form_id)))

        params = {
            "form_id": form.id
        }

        return bool(self.medsenger_api.add_records(contract_id, packet, params=params))

    def create_or_edit(self, data, contract):
        try:
            old_names = []
            form_id = data.get('id')
            if not form_id:
                form = Form()
            else:
                form = Form.query.filter_by(id=form_id).first_or_404()

                if form.contract_id != contract.id and not contract.is_admin:
                    return None

                old_names = form.categories.split('|')

            form.title = data.get('title')
            form.doctor_description = data.get('doctor_description')
            form.patient_description = data.get('patient_description')
            form.show_button = data.get('show_button')
            form.button_title = data.get('button_title')
            form.timetable = data.get('timetable')
            form.fields = data.get('fields')
            form.categories = data.get('categories')
            form.template_id = data.get('template_id')
            form.warning_days = data.get('warning_days')

            if data.get('is_template') and contract.is_admin:
                form.is_template = True
                form.template_category = data.get('template_category')
            else:
                form.patient_id = contract.patient_id
                form.contract_id = contract.id

                names = form.categories.split('|')

                to_remove = list(filter(lambda c: c not in names, old_names))
                if to_remove:
                    self.medsenger_api.remove_hooks(contract.id, to_remove)

                to_add = list(filter(lambda c: c not in old_names, names))
                if to_add:
                    self.medsenger_api.add_hooks(contract.id, to_add)

            if data.get('algorithm_id') and contract.is_admin:
                form.algorithm_id = data.get('algorithm_id')

            if not form_id:
                self.db.session.add(form)
            self.__commit__()

            return form
        except Exception as e:
            log(e)
            return None
