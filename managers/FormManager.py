from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Form


class FormManager(Manager):
    def __init__(self, *args):
        super(FormManager, self).__init__(*args)

    def create_form(self, data, contract=None):
        try:
            form = Form()

            form.title = data.get('title')
            form.doctor_description = data.get('doctor_description')
            form.patient_description = data.get('patient_description')
            form.show_button = data.get('show_button')
            form.button_title = data.get('button_title')
            form.timetable = data.get('timetable')
            form.fields = data.get('fields')

            if not contract:
                form.is_template = True
            else:
                form.patient_id = contract.patient_id
                form.contract_id = contract.id

            self.db.session.add(form)
            self.__commit__()

            return form
        except Exception as e:
            log(e)
            return None

