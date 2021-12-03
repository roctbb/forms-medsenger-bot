import time
from datetime import datetime, timedelta, date
from functools import reduce

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from helpers import get_step

db = SQLAlchemy()


class Compliance:
    def current_month_compliance(self, action=None):
        return self.count_compliance(action, start_date=datetime.now().replace(day=1, minute=0, hour=0, second=0))

    def count_compliance(self, action=None, start_date=None, end_date=None):
        if not action:
            if isinstance(self, Form):
                action = "form_{}".format(self.id)
            if isinstance(self, Medicine):
                action = "medicine_{}".format(self.id)

        request = ActionRequest.query.filter_by(contract_id=self.contract_id, action=action)

        if start_date:
            request = request.filter(ActionRequest.sent >= start_date)

        if end_date:
            request = request.filter(ActionRequest.sent <= end_date)

        records = request.all()

        return len(records), len(list(filter(lambda x: x.is_done, records)))


# models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contracts = db.relationship('Contract', backref=backref('patient', uselist=False), lazy=True)
    forms = db.relationship('Form', backref=backref('patient', uselist=False), lazy=True)
    medicines = db.relationship('Medicine', backref=backref('patient', uselist=False), lazy=True)
    reminders = db.relationship('Reminder', backref=backref('patient', uselist=False), lazy=True)
    algorithms = db.relationship('Algorithm', backref=backref('patient', uselist=False), lazy=True)

    def as_dict(self):
        return {
            "id": self.id,
            "month_compliance": self.count_month_compliance(),
            "contracts": [contract.as_dict() for contract in self.contracts],
            "forms": [form.as_dict() for form in self.forms],
            "medicines": [medicine.as_dict() for medicine in self.medicines if medicine.canceled_at is None],
            "canceled_medicines": [medicine.as_dict() for medicine in self.medicines if medicine.canceled_at is not None],
            "reminders": sorted([reminder.as_dict() for reminder in self.reminders if reminder.canceled_at is None], key=lambda k: k["attach_date"]),
            "old_reminders": sorted([reminder.as_dict() for reminder in self.reminders if reminder.canceled_at is not None], key=lambda k: k["attach_date"], reverse=True),
            "algorithms": [algorithm.as_dict() for algorithm in self.algorithms]
        }

    def count_month_compliance(self):
        def sum_compliance(compliance, object):
            sent, done = object.current_month_compliance()
            compliance[0] += sent
            compliance[1] += done
            return compliance

        return reduce(sum_compliance, list(self.forms) + list(self.medicines), [0, 0])

    def count_full_compliance(self):
        def sum_compliance(compliance, object):
            sent, done = object.count_compliance()
            compliance[0] += sent
            compliance[1] += done
            return compliance

        return reduce(sum_compliance, list(self.forms) + list(self.medicines), [0, 0])


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=False)
    clinic_id = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    agent_token = db.Column(db.String(255), nullable=True)

    forms = db.relationship('Form', backref=backref('contract', uselist=False), lazy=True)
    medicines = db.relationship('Medicine', backref=backref('contract', uselist=False), lazy=True)
    reminders = db.relationship('Reminder', backref=backref('contract', uselist=False), lazy=True)
    algorithms = db.relationship('Algorithm', backref=backref('contract', uselist=False), lazy=True)
    tasks = db.Column(db.JSON, nullable=True)

    is_admin = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String(255), nullable=True)

    def as_dict(self, native=False):
        serialized = {
            "id": self.id,
            "clinic_id": self.clinic_id
        }

        if native:
            serialized['agent_token'] = self.agent_token

        return serialized


class Medicine(db.Model, Compliance):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    rules = db.Column(db.Text, nullable=True)
    dose = db.Column(db.Text, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    verify_dose = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete="set null"), nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    warning_days = db.Column(db.Integer, default=0)
    warning_timestamp = db.Column(db.Integer, default=0)
    filled_timestamp = db.Column(db.Integer, default=0)

    prescribed_at = db.Column(db.DateTime, server_default=db.func.now())
    canceled_at = db.Column(db.DateTime, nullable=True)

    def as_dict(self):
        if self.contract_id:
            sent, done = self.current_month_compliance()
        else:
            sent, done = 0, 0

        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "rules": self.rules,
            "dose": self.dose,
            "timetable": self.timetable,
            "is_template": self.is_template,
            "verify_dose": self.verify_dose,
            "template_id": self.template_id,
            "warning_days": self.warning_days,
            "prescribed_at": self.prescribed_at.strftime("%d.%m.%Y"),
            "canceled_at": self.canceled_at.strftime("%d.%m.%Y") if self.canceled_at else None,
            "sent": sent,
            "done": done
        }

    def timetable_description(self):
        if self.timetable['mode'] == 'daily':
            return '{} раз(а) в день'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'weekly':
            return '{} раз(а) в неделю'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'manual':
            return ''
        else:
            return '{} раз(а) в месяц'.format(len(self.timetable['points']))

    def get_description(self, tt=False):
        medicine_description = "«{}»".format(self.title)
        print(self.dose)
        if self.dose is not None:
            medicine_description += " {}".format(self.dose)
        if self.rules and not tt:
            medicine_description += " ({})".format(self.rules)
        elif self.rules:
            tt_description = self.timetable_description()

            if tt_description:
                tt_description = ' / ' + tt_description

            medicine_description += " ({}{})".format(self.rules, tt_description)
        elif tt:
            tt_description = self.timetable_description()

            if tt_description:
                medicine_description += '({})'.format(tt_description)

        return medicine_description

    def clone(self):
        new_medicine = Medicine()
        new_medicine.title = self.title
        new_medicine.rules = self.rules
        new_medicine.dose = self.dose
        new_medicine.verify_dose = self.verify_dose

        new_medicine.timetable = self.timetable
        new_medicine.warning_days = self.warning_days
        new_medicine.prescribed_at = datetime.now()

        if self.is_template:
            new_medicine.template_id = self.id
        else:
            new_medicine.template_id = self.template_id

        return new_medicine


class Form(db.Model, Compliance):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    doctor_description = db.Column(db.Text, nullable=True)
    patient_description = db.Column(db.Text, nullable=True)
    thanks_text = db.Column(db.Text, nullable=True)

    show_button = db.Column(db.Boolean, default=False)
    button_title = db.Column(db.String(255), nullable=True)

    custom_title = db.Column(db.String(255), nullable=True)
    custom_text = db.Column(db.String(255), nullable=True)

    fields = db.Column(db.JSON, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)

    has_integral_evaluation = db.Column(db.Boolean, default=False)
    integral_evaluation = db.Column(db.JSON, nullable=True)

    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('form.id', ondelete="set null"), nullable=True)
    categories = db.Column(db.String(512), nullable=True)

    algorithm_id = db.Column(db.Integer, db.ForeignKey('algorithm.id', ondelete="set null"), nullable=True)
    clinics = db.Column(db.JSON, nullable=True)
    exclude_clinics = db.Column(db.JSON, nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    warning_days = db.Column(db.Integer, default=0)
    warning_timestamp = db.Column(db.Integer, default=0)
    filled_timestamp = db.Column(db.Integer, default=0)

    template_category = db.Column(db.String(512), default="Общее", nullable=True)
    instant_report = db.Column(db.Boolean, default=False, nullable=False, server_default='false')

    init_text = db.Column(db.Text, nullable=True)

    def as_dict(self):
        if self.contract_id:
            sent, done = self.current_month_compliance()
        else:
            sent, done = 0, 0

        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "doctor_description": self.doctor_description,
            "patient_description": self.patient_description,
            "thanks_text": self.thanks_text,
            "fields": self.fields,
            "has_integral_evaluation": self.has_integral_evaluation,
            "integral_evaluation": self.integral_evaluation,
            "timetable": self.timetable,
            "show_button": self.show_button,
            "button_title": self.button_title,
            "custom_title": self.custom_title,
            "custom_text": self.custom_text,
            "is_template": self.is_template,
            "template_id": self.template_id,
            "algorithm_id": self.algorithm_id,
            "warning_days": self.warning_days,
            "template_category": self.template_category,
            "instant_report": self.instant_report,
            "clinics": self.clinics,
            "exclude_clinics": self.exclude_clinics,
            "sent": sent,
            "done": done
        }

    def clone(self):
        new_form = Form()
        new_form.title = self.title
        new_form.doctor_description = self.doctor_description
        new_form.patient_description = self.patient_description
        new_form.thanks_text = self.thanks_text
        new_form.show_button = self.show_button
        new_form.button_title = self.button_title
        new_form.custom_title = self.custom_title
        new_form.custom_text = self.custom_text
        new_form.fields = self.fields
        new_form.has_integral_evaluation = self.has_integral_evaluation
        new_form.integral_evaluation = self.integral_evaluation
        new_form.timetable = self.timetable
        new_form.algorithm_id = self.algorithm_id
        new_form.categories = self.categories
        new_form.warning_days = self.warning_days
        new_form.instant_report = self.instant_report

        if self.is_template:
            new_form.template_id = self.id
        else:
            new_form.template_id = self.template_id

        return new_form


class Algorithm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # actual
    steps = db.Column(db.JSON, nullable=True)
    common_conditions = db.Column(db.JSON, nullable=True)
    initial_step = db.Column(db.String(128), nullable=True)
    current_step = db.Column(db.String(128), nullable=True)
    timeout_at = db.Column(db.Integer, server_default="0")

    categories = db.Column(db.String(512), nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('algorithm.id', ondelete="set null"), nullable=True)
    attached_form = db.Column(db.Integer, nullable=True)

    template_category = db.Column(db.String(512), default="Общее", nullable=True)
    clinics = db.Column(db.JSON, nullable=True)

    attach_date = db.Column(db.Date, nullable=True)
    detach_date = db.Column(db.Date, nullable=True)

    def as_dict(self, native=False):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "description": self.description,
            "steps": self.steps,
            "common_conditions": self.common_conditions,
            "categories": self.categories,
            "is_template": self.is_template,
            "template_id": self.template_id,
            "template_category": self.template_category,
            "attached_form": self.attached_form,
            "clinics": self.clinics,
            "attach_date": self.attach_date.strftime('%Y-%m-%d') if self.attach_date else None,
            "detach_date": self.detach_date.strftime('%Y-%m-%d') if self.detach_date else None
        }

    def clone(self):

        attach = datetime.now().date()
        detach = None

        if self.attach_date and self.detach_date:
            length = abs((self.detach_date - self.attach_date).days)
            detach = attach + timedelta(days=length)

        new_algorithm = Algorithm()
        new_algorithm.title = self.title
        new_algorithm.description = self.description
        new_algorithm.steps = self.steps
        new_algorithm.common_conditions = self.common_conditions
        new_algorithm.categories = self.categories
        new_algorithm.attached_form = self.attached_form
        new_algorithm.initial_step = self.initial_step
        new_algorithm.attach_date = attach
        new_algorithm.detach_date = detach

        step = get_step(self)
        if not step.get('reset_minutes') or int(step['reset_minutes']) == 0:
            new_algorithm.timeout_at = 0
        else:
            new_algorithm.timeout_at = time.time() + 60 * int(step['reset_minutes'])

        if self.is_template:
            new_algorithm.template_id = self.id
        else:
            new_algorithm.template_id = self.template_id

        return new_algorithm


class ActionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    action = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    is_done = db.Column(db.Boolean, default=False)

    sent = db.Column(db.DateTime(), default=db.func.current_timestamp())
    done = db.Column(db.DateTime(), nullable=True)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    attach_date = db.Column(db.Date, nullable=True)
    detach_date = db.Column(db.Date, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)
    send_next = db.Column(db.DateTime(), nullable=True)

    type = db.Column(db.String(7), nullable=False)
    state = db.Column(db.Text, nullable=True)
    text = db.Column(db.Text, nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('reminder.id', ondelete="set null"), nullable=True)

    canceled_at = db.Column(db.DateTime, nullable=True)

    def timetable_description(self):
        if self.timetable['mode'] == 'daily':
            description = '{} раз(а) в день'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'weekly':
            description = '{} раз(а) в неделю'.format(len(self.timetable['points']))
        else:
            description = '{} раз(а) в месяц'.format(len(self.timetable['points']))
        delta = self.detach_date - self.attach_date
        description += ' в течение {} дней'.format(abs(delta.days))
        return description

    def as_dict(self):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "type": self.type,
            "state": self.state,
            "text": self.text,
            "attach_date": self.attach_date.strftime('%Y-%m-%d') if self.attach_date else None,
            "detach_date": self.detach_date.strftime('%Y-%m-%d') if self.detach_date else None,
            "timetable": self.timetable,
            "canceled_at": self.canceled_at.strftime("%d.%m.%Y") if self.canceled_at else None,
            "is_template": self.is_template,
            "template_id": self.template_id,
        }

    def clone(self):
        new_reminder = Reminder()
        new_reminder.type = self.type
        new_reminder.state = 'active'

        new_reminder.patient_text = self.text

        new_reminder.attach_date = self.attach_date
        new_reminder.detach_date = self.detach_date
        new_reminder.timetable = self.timetable

        if self.is_template:
            new_reminder.template_id = self.id
        else:
            new_reminder.template_id = self.template_id

        return new_reminder
