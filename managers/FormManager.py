import json
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

    def clear(self, contract):
        Form.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        return True

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

    def attach(self, template_id, contract, custom_timetable=None):
        form = self.get(template_id)

        if form:
            new_form = form.clone()
            new_form.contract_id = contract.id
            new_form.patient_id = contract.patient.id

            if new_form.categories:
                self.medsenger_api.add_hooks(contract.id, new_form.categories.split('|'))

            if custom_timetable:
                try:
                    new_form.timetable = custom_timetable
                except Exception as e:
                    log(e, False)

            self.db.session.add(new_form)
            self.__commit__()

            if new_form.timetable.get('send_on_init'):
                self.db.session.refresh(new_form)
                self.run(new_form)

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
        if form.warning_days and form.warning_timestamp == 0:
            if form.filled_timestamp and time.time() - form.filled_timestamp > 24 * 60 * 60 * form.warning_days:
                form.warning_timestamp = int(time.time())

                self.medsenger_api.send_message(form.contract_id,
                                                "Пациент не заполнял опросник {} уже {} дней.".format(form.title,
                                                                                                      form.warning_days))
                self.__commit__()

    def __instant_report__(self, contract_id, form, report):
        text = 'Пациент заполнил опросник "{}" и дал следующие ответы.<br><br>'.format(form.title)
        text += '<ul>{}</ul>'.format(''.join(list(map(lambda line: '<li><strong>{}</strong>: {};</li>'.format(*line), report))))

        deadline = time.time() + 1 * 60 * 60

        self.medsenger_api.send_message(contract_id, text, only_doctor=True)
        self.medsenger_api.send_message(contract_id, 'Спасибо за заполнение опросника "{}". Ответы отправлены вашему лечащему врачу.'.format(form.title), only_patient=True, action_deadline=deadline)

    def submit(self, answers, form_id, contract_id):
        form = Form.query.filter_by(id=form_id).first_or_404()
        form.warning_timestamp = 0
        form.filled_timestamp = int(time.time())

        packet = []
        report = []

        for field in form.fields:
            if field['uid'] in answers.keys():
                if field['type'] == 'radio':
                    category = field['params']['variants'][answers[field['uid']]]['category']

                    if category == 'none':
                        continue

                    value = field['params']['variants'][answers[field['uid']]]['category_value']
                    answer = field['params']['variants'][answers[field['uid']]].get('text')

                    params = {
                        "question_uid": field['uid'],
                        "question_text": field.get('text'),
                        "answer": answer
                    }

                    report.append((field.get('text'), answer))

                    if field['params']['variants'][answers[field['uid']]].get('custom_params'):
                        try:
                            params.update(
                                json.loads(field['params']['variants'][answers[field['uid']]].get('custom_params')))
                        except:
                            pass

                    packet.append((category, value, params))
                elif field['type'] == 'checkbox':
                    category = field['category']
                    value = field.get('category_value')

                    if not value:
                        report.append((field.get('text'), "Нет"))
                        continue
                    else:
                        report.append((field.get('text'), "Да"))

                    params = {
                        "question_iud": field['uid'],
                        "question_text": field.get('text'),
                        "answer": value
                    }

                    if field.get('params', {}).get('custom_params'):
                        try:
                            params.update(json.loads(field.get('params', {}).get('custom_params')))
                        except:
                            pass

                    packet.append((category, value, params))
                else:
                    category = field['category']
                    params = {
                        "question_uid": field['uid'],
                        "question_text": field.get('text'),
                        "answer": answers[field['uid']]
                    }

                    report.append((field.get('text'), answers[field['uid']]))

                    if field.get('params', {}).get('custom_params'):
                        try:
                            params.update(json.loads(field.get('params', {}).get('custom_params')))
                        except:
                            pass

                    if field['type'] in ['textarea', 'text'] and field.get('prefix'):
                        packet.append((category, "{}{}".format(field.get('prefix'), answers[field['uid']]), params))
                    else:
                        packet.append((category, answers[field['uid']], params))

        if form.template_id:
            packet.append(('action', 'Заполнение опросника ID {}'.format(form.template_id)))
        else:
            packet.append(('action', 'Заполнение опросника ID {}'.format(form_id)))


        params = {
            "form_id": form.id
        }

        if form.instant_report:
            self.__instant_report__(contract_id, form, report)

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
            form.thanks_text = data.get('thanks_text')
            form.show_button = data.get('show_button')
            form.button_title = data.get('button_title')
            form.timetable = data.get('timetable')
            form.fields = data.get('fields')
            form.categories = data.get('categories')
            form.template_id = data.get('template_id')
            form.warning_days = data.get('warning_days')
            form.instant_report = data.get('instant_report')

            if data.get('is_template') and contract.is_admin:
                form.is_template = True
                form.template_category = data.get('template_category')
                form.clinics = data.get('clinics')
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

            if form.timetable.get('send_on_init') and form.contract_id:
                self.db.session.refresh(form)
                self.run(form)

            return form
        except Exception as e:
            log(e)
            return None
