import time
from datetime import datetime
from tasks import threader
from config import DYNAMIC_CACHE
from helpers import log, gts
from managers.Manager import Manager
from models import Patient, Contract, Medicine
import requests
from config import MEDICINE_CATALOG_URL


class MedicineManager(Manager):
    def __init__(self, *args):
        super(MedicineManager, self).__init__(*args)

    def fill_atx(self, medicine):
        if not medicine.atx:
            try:
                answer = requests.get(MEDICINE_CATALOG_URL + '/search?title=' + medicine.title)
                atx = set(map(lambda m: m['atx'], answer.json()))

                if len(atx) == 1:
                    medicine.atx = atx.pop()
            except Exception as e:
                print(e)

    def detach(self, template_id, contract):
        medicines = list(filter(lambda x: x.template_id == template_id, contract.patient.medicines))

        for medicine in medicines:
            medicine.canceled_at = datetime.now()

        self.__commit__()

    def detach_by_atx(self, atx, contract):
        medicines = list(filter(lambda x: x.atx == atx, contract.patient.medicines))

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

            self.medsenger_api.send_message(contract.id, "Врач назначил препарат {}.{}"
                                            .format(new_medicine.get_description(True),
                                                    " Мы будем автоматически присылать напоминания о приемах." if
                                                    new_medicine.timetable['mode'] != "manual" else ''))
            self.db.session.add(new_medicine)
            self.__commit__()

            params = {
                'obj_id': new_medicine.id,
                'action': 'attach',
                'object_type': 'medicine',
                'description': new_medicine.get_description(True, False)
            }

            threader.async_record.delay(contract.id, 'doctor_action',
                                        'Назначен препарат "{}".'.format(new_medicine.title), params=params)

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
        if medicine.warning_days and medicine.warning_timestamp == 0 and medicine.asked_timestamp:
            time_from = medicine.asked_timestamp
            if medicine.prescribed_at:
                time_from = max(medicine.asked_timestamp, medicine.prescribed_at.timestamp())
            if time.time() - time_from > 24 * 60 * 60 * medicine.warning_days:
                medicine.warning_timestamp = int(time.time())

                self.medsenger_api.send_message(medicine.contract_id,
                                                "Пациент не сообщал о приеме лекарства {} уже {} дней.".format(
                                                    medicine.title, medicine.warning_days), only_doctor=True)
                self.__commit__()

    def submit(self, medicine_id, contract_id, params=None):
        medicine = self.get(medicine_id)
        medicine.warning_timestamp = 0
        medicine.asked_timestamp = 0
        medicine.filled_timestamp = int(time.time())

        self.__commit__()

        if params is None:
            params = {"medicine_id": medicine_id, 'dose': medicine.dose}
        else:
            params.update({"medicine_id": medicine_id})

        self.medsenger_api.add_record(contract_id, 'medicine', medicine.title, params=params)

        self.log_done("medicine_{}".format(medicine_id), contract_id)

        return True

    def clear(self, contract):
        print(gts() + f"clearing medicines from contract {contract.id}")
        Medicine.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        print(gts() + f"clearing medicines from contract {contract.id} done")
        return True

    def resume(self, id, contract):

        medicine = Medicine.query.filter_by(id=id).first_or_404()

        if medicine.contract_id != contract.id and not contract.is_admin:
            return None

        if medicine.contract_id:
            self.medsenger_api.send_message(contract.id,
                                            "Врач возобновил препарат {}.".format(medicine.get_description()))
            params = {
                'obj_id': medicine.id,
                'action': 'resume',
                'object_type': 'medicine',
                'description': medicine.get_description(True, False)
            }

            threader.async_record.delay(contract.id, 'doctor_action',
                                        'Возобновлен препарат "{}".'.format(medicine.title), params=params)

        medicine.canceled_at = None

        self.__commit__()

        return id

    def remove(self, id, contract, by_patient=False):

        medicine = Medicine.query.filter_by(id=id).first_or_404()

        if medicine.contract_id != contract.id and not contract.is_admin:
            return None

        if medicine.contract_id:
            if not by_patient:
                self.medsenger_api.send_message(contract.id,
                                                "Врач отменил препарат {}.".format(medicine.get_description()))
            params = {
                'obj_id': medicine.id,
                'action': 'cancel',
                'object_type': 'medicine',
                'description': medicine.get_description(True, False)
            }
            threader.async_record.delay(contract.id, 'doctor_action' if not by_patient else 'action',
                                        'Отменен препарат "{}".'.format(medicine.title), params=params)

        medicine.canceled_at = datetime.now()

        self.__commit__()

        return id

    def check_detach_dates(self, app):
        with app.app_context():
            medicines = list(Medicine.query.filter(
                (Medicine.detach_date == datetime.now().date()) & (Medicine.is_template == False) & (
                        Medicine.canceled_at == None)).all())

            for medicine in medicines:
                self.medsenger_api.send_message(medicine.contract_id,
                                                "Врач отменил препарат {}.".format(medicine.get_description()))
                params = {
                    'obj_id': medicine.id,
                    'action': 'cancel',
                    'object_type': 'medicine',
                    'description': medicine.get_description(True, False)
                }

                threader.async_record.delay(medicine.contract_id, 'doctor_action',
                                              'Отменен препарат "{}".'.format(medicine.title), params=params)

                record = {
                    'description': 'Отменен',
                    'comment': 'Автоматически',
                    'date': datetime.now().strftime('%d.%m.%Y')
                }

                if medicine.prescription_history:
                    history = medicine.prescription_history.copy()
                    history['last_updated'] = datetime.now().timestamp()
                    history['records'].append(record)
                    medicine.prescription_history = history
                else:
                    medicine.prescription_history = {'records': [record]}
                medicine.canceled_at = datetime.now()
            self.__commit__()

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
        threader.async_order.delay(medicine.contract_id, "medicine", 26, medicine.as_dict())

        if result:
            medicine.last_sent = datetime.now()

            if not medicine.asked_timestamp:
                medicine.asked_timestamp = time.time()

            if commit:
                self.__commit__()

        return result

    def edit_history(self, data):
        try:
            medicine_id = data.get('id')
            if not medicine_id:
                return None
            medicine = Medicine.query.filter_by(id=medicine_id).first_or_404()
            medicine.prescription_history = data.get('prescription_history')
            self.__commit__()

            return medicine

        except Exception as e:
            log(e)
            return None

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
            medicine.prescription_history = data.get('prescription_history')
            medicine.template_id = data.get('template_id')
            medicine.warning_days = data.get('warning_days')
            medicine.verify_dose = data.get('verify_dose', False)
            medicine.is_created_by_patient = data.get('is_created_by_patient', False)
            medicine.prescribed_at = datetime.now()

            try:
                medicine.medicine_database_id = int(data.get('medicine_database_id'))
            except:
                pass

            if data.get('is_template') or medicine.is_template:
                medicine.is_template = True
                medicine.template_category = data.get('template_category')
                if contract.is_admin:
                    medicine.clinics = data.get('clinics')
                    medicine.exclude_clinics = data.get('exclude_clinics')
                else:
                    medicine.doctor_id = data.get('doctor_id')
                    medicine.clinic_id = data.get('clinic_id')
            else:
                medicine.patient_id = contract.patient_id
                medicine.contract_id = contract.id

                detach_date = medicine.timetable.get('detach_date')
                medicine.detach_date = datetime.strptime(detach_date, "%Y-%m-%d") if detach_date else None
                action = 'назначил препарат' if is_new else 'изменил параметры приема препарата'
                params = {
                    'obj_id': medicine.id,
                    'action': 'create' if is_new else 'edit',
                    'object_type': 'medicine',
                    'description': medicine.get_description(True, False)
                }

                if not data.get('edited_by_patient'):
                    self.medsenger_api.send_message(contract.id,
                                                    "Врач {} {}.{}".format(
                                                        action, medicine.get_description(True),
                                                        " Мы будем автоматически присылать напоминания о приемах." if
                                                        medicine.timetable['mode'] != "manual" else ''))
                action = 'Назначен препарат' if is_new else 'Изменены параметры приема препарата'
                threader.async_record.delay(contract.id,
                                            'doctor_action' if not data.get('edited_by_patient') else 'action',
                                            '{} "{}".'.format(action, medicine.title), params=params)

            if not medicine_id:
                self.db.session.add(medicine)

            self.fill_atx(medicine)
            self.__commit__()

            return medicine
        except Exception as e:
            log(e)
            return None
