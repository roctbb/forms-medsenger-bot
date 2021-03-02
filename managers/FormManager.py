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

            self.db.session.add(new_form)
            self.__commit__()

            return True
        else:
            return False

    def run(self, form, commit=True, contract_id=None):

        text = 'Пожалуйста, заполните анкету "{}".'.format(form.title)
        action = 'form/{}'.format(form.id)
        action_name = 'Заполнить анкету'

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

    def submit(self, answers, form_id, contract_id):
        form = Form.query.filter_by(id=form_id).first_or_404()

        packet = []

        for field in form.fields:
            if field['uid'] in answers:
                if field['type'] == 'radio':
                    category = field['params']['variants'][answers[field['uid']]]['category']
                    value = field['params']['variants'][answers[field['uid']]]['category_value']
                    packet.append((category, value))
                elif field['type'] == 'checkbox':
                    category = field['category']
                    packet.append((category, 1))
                else:
                    category = field['category']
                    packet.append((category, answers[field['uid']]))

        packet.append(('action', 'Заполнение анкеты ID {}'.format(form_id)))

        return bool(self.medsenger_api.add_records(contract_id, packet))

    def create_or_edit(self, data, contract):
        try:
            form_id = data.get('id')
            if not form_id:
                form = Form()
            else:
                form = Form.query.filter_by(id=form_id).first_or_404()

                if form.contract_id != contract.id and not contract.is_admin:
                    return None

            form.title = data.get('title')
            form.doctor_description = data.get('doctor_description')
            form.patient_description = data.get('patient_description')
            form.show_button = data.get('show_button')
            form.button_title = data.get('button_title')
            form.timetable = data.get('timetable')
            form.fields = data.get('fields')
            form.categories = data.get('categories')
            form.template_id = data.get('template_id')

            if data.get('is_template'):
                form.is_template = True
            else:
                form.patient_id = contract.patient_id
                form.contract_id = contract.id

            if not form_id:
                self.db.session.add(form)
            self.__commit__()

            return form
        except Exception as e:
            log(e)
            return None
