import time
from datetime import datetime, timedelta

from helpers import log, timezone_now
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

    def attach(self, template_id, contract, dates):
        reminder = self.get(template_id)

        if reminder:
            new_reminder = reminder.clone()
            new_reminder.contract_id = contract.id
            new_reminder.patient_id = contract.patient.id
            new_reminder.attach_date = datetime.now()

            if dates:
                new_reminder.timetable = {
                    "mode": "dates",
                    "points": [{"date": d} for d in dates],
                    "dates_enabled": True
                }

            self.db.session.add(new_reminder)
            self.__commit__()

            return reminder
        else:
            return False

    def clear(self, contract):
        Reminder.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        return True

    def remove(self, id, contract):
        reminder = Reminder.query.filter_by(id=id).first_or_404()

        if reminder.contract_id != contract.id and not contract.is_admin:
            return None

        reminder.canceled_at = datetime.now()

        self.__commit__()
        return id

    def set_state(self, reminder, state):
        result = None

        reminder.state = state
        self.__commit__()

        patient_text = ""
        doctor_text = ""
        action = None
        if state == 'done':
            action = 'выполнил назначение'
        elif state == 'reject':
            action = 'отказался от выполнения назначения'
        elif state == 'cancel':
            action = 'отключил напоминание'

        if reminder.type == 'patient':
            patient_text = 'Спасибо! Мы сообщили врачу.'
            doctor_text = 'Пациент {}:\n\n{}'.format(action, reminder.text)
        else:
            doctor_text = 'Спасибо!'

        deadline = (timezone_now(reminder.contract.get_actual_timezone()) + timedelta(days=1)).timestamp()

        if state == 'later':
            result = self.medsenger_api.send_message(reminder.contract_id, 'Напоминание автоматически отправится позже.',
                                                     only_patient=reminder.type == 'patient', only_doctor=reminder.type == 'doctor',
                                                     action_deadline=deadline)
            return result

        reminder.canceled_at = datetime.now()
        self.__commit__()

        if patient_text:
            result = self.medsenger_api.send_message(reminder.contract_id, patient_text, only_patient=True, action_deadline=deadline)
        if doctor_text:
            result = self.medsenger_api.send_message(reminder.contract_id, doctor_text, only_doctor=True, action_deadline=deadline)

        return result

    def set_next_date(self, id, contract, type, count):
        reminder = Reminder.query.filter_by(id=id).first_or_404()

        if reminder.contract_id != contract.id and not contract.is_admin:
            return None

        send_next = None

        if type == 'hour':
            send_next = timezone_now(contract.get_actual_timezone()) + timedelta(hours=count)
        elif type == 'day':
            send_next = timezone_now(contract.get_actual_timezone()) + timedelta(days=count)

        reminder.send_next = send_next
        reminder.state = 'later'

        self.__commit__()
        return reminder.id

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
            reminder.title = data.get('title')
            reminder.text = data.get('text')

            reminder.attach_date = data.get('attach_date')
            reminder.detach_date = data.get('detach_date')
            reminder.timetable = data.get('timetable')
            reminder.hide_actions = data.get('hide_actions')

            if contract.is_admin:
                reminder.has_order = data.get('has_order')

            if reminder.has_order:
                reminder.order = data.get('order')
                reminder.order_params = data.get('order_params')
                reminder.order_agent_id = data.get('order_agent_id')

            if contract.is_admin:
                reminder.has_action = data.get('has_action')

            if reminder.has_action:
                reminder.action = data.get('action')
                reminder.action_description = data.get('action_description')

            reminder.has_record_params = data.get('has_record_params')

            if reminder.has_record_params:
                reminder.record_params = data.get('record_params')

            reminder.state = data.get('state', 'active')

            if data.get('is_template'):
                reminder.is_template = True
            else:
                reminder.patient_id = contract.patient_id
                reminder.contract_id = contract.id

            if not reminder.is_template and reminder.has_record_params and not reminder_id:
                self.medsenger_api.add_record(contract.id, reminder.record_params['category'], reminder.record_params['date'])

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
            if reminder.type == 'patient':
                description += "Отправка напоминания пациенту: \"{}\". ".format(reminder.text)
            if reminder.type == 'patient' or reminder.type == 'both':
                description += "Отправка напоминания врачу: \"{}\".".format(reminder.text)

        super().log_request("reminder_{}".format(reminder.id), contract_id, description)

    def run(self, reminder, commit=True):
        result = None
        action_name = None
        action_link = None
        text = reminder.text

        if reminder.text:
            if not reminder.hide_actions:
                action_name = 'Отметить действие'
                action_link = 'reminder/{}'.format(reminder.id)

            if reminder.has_action:
                action_name = reminder.action_description
                action_link = reminder.action

            if reminder.has_record_params:
                date_parts = reminder.record_params['date'].split('-')
                text += '<br><b>{}:</b> {}.{}.{}'.format(reminder.record_params['description'],
                                                         date_parts[2], date_parts[1], date_parts[0])

            if reminder.type == 'patient':
                result = self.medsenger_api.send_message(reminder.contract_id, text, action_name=action_name,
                                                         action_onetime=True, action_big=False,
                                                         action_link=action_link, only_patient=True)
            if reminder.type == 'doctor':
                result = self.medsenger_api.send_message(reminder.contract_id, text, action_name=action_name,
                                                         action_onetime=True, action_big=False,
                                                         action_link=action_link, only_doctor=True)
        if reminder.has_order:
            params = reminder.order_params if reminder.order_params else None
            agent_id = reminder.order_agent_id if reminder.order_agent_id else None
            result = self.medsenger_api.send_order(reminder.contract_id, reminder.order, receiver_id=reminder.order_agent_id, params=reminder.order_params)

        if result:
            reminder.last_sent = datetime.now()
            if commit:
                self.__commit__()
                return result

        return result
