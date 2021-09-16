import time
from datetime import datetime

from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Reminder


class ReminderManager(Manager):
    def __init__(self, *args):
        super(ReminderManager, self).__init__(*args)

    def get_templates(self):
        return Reminder.query.filter_by(is_template=True).all()

    def get(self, reminder_id):
        reminder = Reminder.query.filter_by(id=reminder_id).first()

        if not reminder:
            raise Exception("No reminder_id = {} found".format(reminder_id))

        return reminder

    def clear(self, contract):
        Reminder.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        return True

    def remove(self, id, contract):
        reminder = Reminder.query.filter_by(id=id).first_or_404()

        if reminder.contract_id != contract.id and not contract.is_admin:
            return None

        Reminder.query.filter_by(id=id).delete()

        self.__commit__()
        return id

    def create_or_edit(self, data, contract):
        try:
            reminder_id = data.get('id')
            if not reminder_id:
                reminder = Reminder()
            else:
                reminder = Reminder.query.filter_by(id=reminder_id).first_or_404()
                if reminder.contract_id != contract.id and not contract.is_admin:
                    return None

            reminder.type = data.get('type')
            reminder.different_text = data.get('different_text')
            reminder.patient_text = data.get('patient_text')
            reminder.doctor_text = data.get('doctor_text')

            reminder.attach_date = data.get('attach_date')
            reminder.detach_date = data.get('detach_date')
            reminder.timetable = data.get('timetable')

            if data.get('is_template'):
                reminder.is_template = True
            else:
                reminder.patient_id = contract.patient_id
                reminder.contract_id = contract.id

            if not reminder_id:
                self.db.session.add(reminder)
            self.__commit__()

            return reminder
        except Exception as e:
            log(e)
            return None

    def log_request(self, reminder, contract_id=None, description=None):
        if not contract_id:
            contract_id = reminder.contract_id
        if not description:
            description = ''
            if reminder.type == 'patient' or reminder.type == 'both':
                description += "Отправка напоминания пациенту: \"{}\". ".format(reminder.patient_text)
            if reminder.type == 'patient' or reminder.type == 'both':
                description += "Отправка напоминания врачу: \"{}\".".format(reminder.doctor_text)

        super().log_request("reminder_{}".format(reminder.id), contract_id, description)

    def run(self, reminder):
        result = None
        if reminder.type == 'patient' or reminder.type == 'both':
            result = self.medsenger_api.send_message(reminder.contract_id, reminder.patient_text, only_patient=True)
        if reminder.type == 'doctor' or reminder.type == 'both':
            result = self.medsenger_api.send_message(reminder.contract_id, reminder.doctor_text, only_doctor=True)
        return result
