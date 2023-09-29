from datetime import datetime
from datetime import timedelta

from config import DYNAMIC_CACHE
from helpers import log
from managers.Manager import Manager
from models import MedicalExamination, MedicalExaminationGroup


class ExaminationManager(Manager):
    def __init__(self, *args):
        super(ExaminationManager, self).__init__(*args)

    def get_templates(self):
        return MedicalExamination.query.filter_by(is_template=True).all()

    def get(self, examination_id):
        examination = MedicalExamination.query.filter_by(id=examination_id).first()

        if not examination:
            raise Exception("No examination_id = {} found".format(examination_id))

        return examination

    def get_group(self, examination_group_id):
        examination_group = MedicalExaminationGroup.query.filter_by(id=examination_group_id).first()

        if not examination_group:
            raise Exception("No examination_group_id = {} found".format(examination_group_id))

        return examination_group

    def detach(self, template_id, contract):
        examinations = list(filter(lambda x: x.template_id == template_id, contract.patient.examinations))

        for examination in examinations:
            self.db.session.delete(examination)

        self.__commit__()

    def attach(self, template_id, contract, deadline_date, send_message=True):
        examination = self.get(template_id)

        if examination:
            new_examination = examination.clone()
            new_examination.contract_id = contract.id
            new_examination.patient_id = contract.patient.id

            new_examination.deadline_date = deadline_date

            if new_examination.no_expiration:
                new_examination.notification_date = deadline_date - timedelta(days=new_examination.expiration_days)
            else:
                new_examination.notification_date = datetime.now().date()

            if send_message:
                self.medsenger_api.send_message(contract.id,
                                                "Врач назначил обследование <b>{}</b> (срок действия {} сут.). Его необходимо загрузить до {}."
                                                .format(new_examination.title, new_examination.expiration_days,
                                                        new_examination.deadline_date.strftime('%d.%m.%Y')))
            self.db.session.add(new_examination)
            self.__commit__()

            params = {
                'obj_id': new_examination.id,
                'action': 'attach',
                'object_type': 'examination',
                'description': new_examination.doctor_description
            }
            self.medsenger_api.add_record(contract.id, 'doctor_action',
                                          'Назначено обследование "{}".'.format(new_examination.title), params=params)

            return new_examination
        else:
            return False

    def attach_group(self, group_id, contract, deadline_date, send_message=True):
        examination_group = self.get_group(group_id)

        for template_id in examination_group.examinations:
            self.attach(template_id, contract, deadline_date, send_message)

    def submit(self, examination, files, contract_id, date=None):
        if not date:
            date = datetime.now().time()
        examination.upload_date = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
        record = self.medsenger_api.add_record(contract_id, 'analysis_result', examination.title,
                                               files=files, params={'examination_id': examination.id},
                                               record_time=date, return_id=True)
        if record:
            examination.record_id = record[0]
        self.__commit__()
        self.log_done("examination_{}".format(examination.id), contract_id)

        if DYNAMIC_CACHE:
            self.medsenger_api.update_cache(contract_id)

        return True

    def clear(self, contract):
        MedicalExamination.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        return True

    def remove(self, examination_id, contract):
        examination = MedicalExamination.query.filter_by(id=examination_id).first_or_404()

        if examination.contract_id != contract.id and not contract.is_admin:
            return None

        if examination.contract_id:
            self.medsenger_api.send_message(contract.id, "Врач отменил обследование {}.".format(examination.title))
            params = {
                'obj_id': examination.id,
                'action': 'cancel',
                'object_type': 'examination',
                'description': examination.doctor_description
            }
            self.medsenger_api.add_record(contract.id, 'doctor_action',
                                          'Отменено обследование "{}".'.format(examination.title), params=params)

        self.db.session.delete(examination)
        self.__commit__()

        return examination_id

    def log_request(self, examination, contract_id=None, description=None):
        if not contract_id:
            contract_id = examination.contract_id
        if not description:
            description = "Загрузка обследования {}".format(examination.title)

        super().log_request("examination_{}".format(examination.id), contract_id, description)

    def run(self, examination):
        text = 'Пожалуйста, не забудьте загрузить обследование <b>{}</b>.'.format(examination.title)
        action = 'examination/{}'.format(examination.id)
        action_name = 'Загрузить обследование'

        result = self.medsenger_api.send_message(examination.contract_id, text, action, action_name,
                                                 True, False, True)

        if result:
            examination.asked = True
            self.__commit__()

        return result

    def create_or_edit(self, data, contract):
        try:
            is_new = True
            examination_id = data.get('id')
            if not examination_id:
                examination = MedicalExamination()
            else:
                examination = MedicalExamination.query.filter_by(id=examination_id).first_or_404()
                is_new = False
                if examination.contract_id != contract.id and not contract.is_admin:
                    return None

            examination.title = data.get('title')
            examination.doctor_description = data.get('doctor_description')
            examination.patient_description = data.get('patient_description')
            examination.expiration_days = data.get('expiration_days', 1)
            examination.no_expiration= data.get('no_expiration', False)
            examination.record_id = data.get('record_id')

            examination.template_id = data.get('template_id')

            if data.get('is_template') or examination.is_template:
                examination.is_template = True
                examination.template_category = data.get('template_category', 'Общее')

                if contract.is_admin:
                    examination.clinics = data.get('clinics')
                    examination.exclude_clinics = data.get('exclude_clinics')
            else:
                examination.patient_id = contract.patient_id
                examination.contract_id = contract.id
                examination.deadline_date = datetime.strptime(data.get('deadline_date'), '%Y-%m-%d')
                if examination.no_expiration:
                    examination.notification_date = examination.deadline_date - timedelta(days=examination.expiration_days)
                else:
                    examination.notification_date = datetime.now().date()

                params = {
                    'obj_id': examination.id,
                    'action': 'create' if is_new else 'edit',
                    'object_type': 'examination',
                    'description': examination.doctor_description
                }

                expiration_text = 'действует бессрочно' if examination.no_expiration else 'срок действия {} сут.'.format(examination.expiration_days)

                if is_new:
                    examination.attach_date = datetime.now()
                    self.medsenger_api.send_message(contract.id,
                                                    "Врач назначил обследование {} ({}). Его необходимо загрузить до {}."
                                                    .format(examination.title, expiration_text,
                                                            examination.deadline_date.strftime('%d.%m.%Y')))
                else:
                    self.medsenger_api.send_message(contract.id,
                                                    "Врач изменил параметры обследования {} ({}). Его необходимо загрузить до {}."
                                                    .format(examination.title, expiration_text,
                                                            examination.deadline_date.strftime('%d.%m.%Y')))

                action = 'Назначено обследование' if is_new else 'Изменены параметры обследования'
                self.medsenger_api.add_record(contract.id, 'doctor_action',
                                              '{} "{}".'.format(action, examination.title), params=params)

            if not examination_id:
                self.db.session.add(examination)
            self.__commit__()

            return examination
        except Exception as e:
            log(e)
            return None
