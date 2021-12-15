import time
from datetime import datetime

from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Medicine


class MedicineManager(Manager):
    def __init__(self, *args):
        super(MedicineManager, self).__init__(*args)

    def detach(self, template_id, contract):
        medicines = list(filter(lambda x: x.template_id == template_id, contract.patient.medicines))

        for medicine in medicines:
            medicine.canceled_at = datetime.now()

        self.__commit__()

    def attach(self, template_id, contract, custom_timetable=None, custom_params={}):
        medicine = self.get(template_id)

        if medicine:
            new_medicine = medicine.clone()
            new_medicine.contract_id = contract.id
            new_medicine.patient_id = contract.patient.id

            if custom_timetable:
                try:
                    new_medicine.timetable = custom_timetable
                except Exception as e:
                    log(e, False)

            if 'title' in custom_params:
                new_medicine.title = custom_params.get('title')

            if 'times' in custom_params:
                new_medicine.timetable = {
                    "mode": "daily",
                    "points": [
                        {
                            "hour": int(h),
                            "minute": int(m)
                        } for h, m in map(lambda x: x.split(':'), custom_params.get('times'))
                    ]
                }

            self.medsenger_api.send_message(contract.id,
                                            "Врач назначил препарат {}.{}".format(new_medicine.get_description(True),
                                                " Мы будем автоматически присылать напоминания об этом." if
                                                new_medicine.timetable['mode'] != "manual" else ''))
            self.db.session.add(new_medicine)
            self.__commit__()

            return medicine
        else:
            return False

    def get_templates(self):
        return Medicine.query.filter_by(is_template=True).all()

    def get(self, medicine_id):
        medicine = Medicine.query.filter_by(id=medicine_id).first()

        if not medicine:
            raise Exception("No medicine_id = {} found".format(medicine_id))

        return medicine

    def check_warning(self, medicine):
        if medicine.warning_days and medicine.warning_timestamp == 0:
            time_from = medicine.filled_timestamp
            if medicine.prescribed_at:
                time_from = max(medicine.filled_timestamp, medicine.prescribed_at.timestamp())
            if time.time() - time_from > 24 * 60 * 60 * medicine.warning_days:
                medicine.warning_timestamp = int(time.time())

                self.medsenger_api.send_message(medicine.contract_id,
                                                "Пациент не сообщал о приеме лекарства {} уже {} дней.".format(
                                                    medicine.title, medicine.warning_days), only_doctor=True)
                self.__commit__()

    def submit(self, medicine_id, contract_id, params=None):
        medicine = self.get(medicine_id)
        medicine.warning_timestamp = 0
        medicine.filled_timestamp = int(time.time())

        if params is None:
            params = {"medicine_id": medicine_id}
        else:
            params.update({"medicine_id": medicine_id})

        self.medsenger_api.add_record(contract_id, 'medicine', medicine.title, params=params)

        self.log_done("form_{}".format(medicine_id), contract_id)

        self.medsenger_api.update_cache(contract_id)

        return True

    def clear(self, contract):
        Medicine.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        return True

    def remove(self, id, contract):

        medicine = Medicine.query.filter_by(id=id).first_or_404()

        if medicine.contract_id != contract.id and not contract.is_admin:
            return None

        if medicine.contract_id:
            self.medsenger_api.send_message(contract.id, "Врач отменил препарат {}.".format(medicine.get_description()))

        medicine.canceled_at = datetime.now()

        self.__commit__()

        return id

    def log_request(self, medicine, contract_id=None, description=None):
        if not contract_id:
            contract_id = medicine.contract_id
        if not description:
            description = "Подтверждение приема лекарства {}".format(medicine.title)

        super().log_request("medicine_{}".format(medicine.id), contract_id, description)

    def run(self, medicine, commit=True):
        text = 'Пожалуйста, не забудьте принять лекарство {}.'.format(medicine.get_description())
        action = 'medicine/{}'.format(medicine.id)
        action_name = 'Подтвердить прием'
        deadline = self.calculate_deadline(medicine)

        result = self.medsenger_api.send_message(medicine.contract_id, text, action, action_name, True, False, True,
                                                 deadline)
        # telepat speaker
        self.medsenger_api.send_order(medicine.contract_id, "medicine", 26, medicine.as_dict())

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
            medicine.dose = data.get('dose')
            medicine.timetable = data.get('timetable')
            medicine.template_id = data.get('template_id')
            medicine.warning_days = data.get('warning_days')
            medicine.verify_dose = data.get('verify_dose', False)
            medicine.prescribed_at = datetime.now()

            if data.get('is_template') or medicine.is_template:
                medicine.is_template = True
            else:
                medicine.patient_id = contract.patient_id
                medicine.contract_id = contract.id

                action = 'назначил препарат' if is_new else 'изменил параметры приема препарата'
                self.medsenger_api.send_message(contract.id,
                                                "Врач {} {}.{}".format(
                                                    action, medicine.get_description(True),
                                                    " Мы будем автоматически присылать напоминания об этом." if
                                                    medicine.timetable['mode'] != "manual" else ''))

            if not medicine_id:
                self.db.session.add(medicine)
            self.__commit__()

            return medicine
        except Exception as e:
            log(e)
            return None
