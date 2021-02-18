from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Form


class FormManager(Manager):
    def __init__(self, *args):
        super(FormManager, self).__init__(*args)

    def delete(self, id, contract):

        form = Form.query.filter_by(id=id).first_or_404()

        if form.contract_id != contract.id:
            return None

        Form.query.filter_by(id=id).delete()

        self.__commit__()
        return id


    def create_or_edit(self, data, contract):
        try:
            form_id = data.get('id')
            if not form_id:
                form = Form()
            else:
                form = Form.query.filter_by(id=form_id).first_or_404()

            form.title = data.get('title')
            form.doctor_description = data.get('doctor_description')
            form.patient_description = data.get('patient_description')
            form.show_button = data.get('show_button')
            form.button_title = data.get('button_title')
            form.timetable = data.get('timetable')
            form.fields = data.get('fields')
            form.categories = data.get('categories')

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

