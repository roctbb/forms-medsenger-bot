from datetime import datetime

from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Medicine


class MedicineManager(Manager):
    def __init__(self, *args):
        super(MedicineManager, self).__init__(*args)

    def get_templates(self):
        return Medicine.query.filter_by(is_template=True).all()

    def get(self, medicine_id):
        medicine = Medicine.query.filter_by(id=medicine_id).first()

        if not medicine:
            raise Exception("No medicine_id = {} found".format(medicine_id))

        return medicine

    def submit(self, medicine_id, contract_id):
        medicine = self.get(medicine_id)

        self.medsenger_api.add_record(contract_id, 'medicine', medicine.title)

        return True


    def remove(self, id, contract):

        medicine = Medicine.query.filter_by(id=id).first_or_404()

        if medicine.contract_id != contract.id and not contract.is_admin:
            return None

        if medicine.contract_id:
            self.medsenger_api.send_message(contract.id,
                                            "Врач отменил препарат «{}» ({} / {}).".format(
                                                medicine.title, medicine.rules, medicine.timetable_description()))

        Medicine.query.filter_by(id=id).delete()

        self.__commit__()
        return id

    def run(self, medicine, commit=True):
        text = 'Пожалуйста, не забудьте принять лекарство "{}" ({}).'.format(medicine.title, medicine.rules)
        action = 'medicine/{}'.format(medicine.id)
        action_name = 'Подтвердить прием'
        deadline = self.calculate_deadline(medicine.timetable)

        result = self.medsenger_api.send_message(medicine.contract_id, text, action, action_name, True, False, True,
                                                 deadline)

        if result:
            medicine.last_sent = datetime.now()

            if commit:
                self.__commit__()

        return result

    def create_or_edit(self, data, contract):
        try:
            is_new = True
            medicine_id = data.get('id')
            if not medicine_id:
                medicine = Medicine()
            else:
                medicine = Medicine.query.filter_by(id=medicine_id).first_or_404()
                is_new = False
                if medicine.contract_id != contract.id and not contract.is_admin:
                    return None

            medicine.title = data.get('title')
            medicine.rules = data.get('rules')
            medicine.timetable = data.get('timetable')
            medicine.template_id = data.get('template_id')

            if data.get('is_template'):
                medicine.is_template = True
            else:
                medicine.patient_id = contract.patient_id
                medicine.contract_id = contract.id

                if is_new:
                    self.medsenger_api.send_message(contract.id, "Врач назначил препарат «{}» ({} / {}). Мы будем автоматически присылать напоминания об этом.".format(medicine.title, medicine.rules, medicine.timetable_description()))
                else:
                    self.medsenger_api.send_message(contract.id,
                                                    "Врач изменил параметры приема препарата «{}» ({} / {}). Мы будем автоматически присылать напоминания об этом.".format(
                                                        medicine.title, medicine.rules,
                                                        medicine.timetable_description()))

            if not medicine_id:
                self.db.session.add(medicine)
            self.__commit__()

            return medicine
        except Exception as e:
            log(e)
            return None
