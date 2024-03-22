from infrastructure import db
from datetime import datetime
from . import Compliance

class Medicine(db.Model, Compliance):
    id = db.Column(db.Integer, primary_key=True)

    template_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete="set null"), nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    clinics = db.Column(db.JSON, nullable=True)
    exclude_clinics = db.Column(db.JSON, nullable=True)
    template_category = db.Column(db.String(512), default="Общее", nullable=True)

    atx = db.Column(db.String(128), nullable=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    doctor_id = db.Column(db.Integer, nullable=True)
    clinic_id = db.Column(db.Integer, nullable=True)
    is_created_by_patient = db.Column(db.Boolean, default=False)

    title = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    rules = db.Column(db.Text, nullable=True)
    dose = db.Column(db.Text, nullable=True)
    verify_dose = db.Column(db.Boolean, default=False)
    notifications_disabled = db.Column(db.Boolean, default=False)

    timetable = db.Column(db.JSON, nullable=True)
    prescription_history = db.Column(db.JSON, nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    warning_days = db.Column(db.Integer, default=0)
    warning_timestamp = db.Column(db.Integer, default=0)
    filled_timestamp = db.Column(db.Integer, default=0)
    asked_timestamp = db.Column(db.Integer, default=0)
    detach_date = db.Column(db.Date, nullable=True)

    prescribed_at = db.Column(db.DateTime, server_default=db.func.now())
    canceled_at = db.Column(db.DateTime, nullable=True)
    is_hidden = db.Column(db.Boolean, default=False)

    medicine_database_id = db.Column(db.Integer, nullable=True)

    def as_dict(self):
        if self.contract_id:
            sent, done = self.current_month_compliance()
        else:
            sent, done = 0, 0

        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "clinic_id": self.clinic_id,
            "is_created_by_patient": self.is_created_by_patient,
            "title": self.title,
            "rules": self.rules,
            "dose": self.dose,
            "timetable": self.timetable,
            "prescription_history": self.prescription_history,
            "is_template": self.is_template,
            "clinics": self.clinics,
            "exclude_clinics": self.exclude_clinics,
            "template_category": self.template_category,
            "notifications_disabled": self.notifications_disabled,
            "verify_dose": self.verify_dose,
            "template_id": self.template_id,
            "warning_days": self.warning_days,
            "detach_date": self.detach_date.strftime('%Y-%m-%d') if self.detach_date else None,
            "prescribed_at": self.prescribed_at.strftime("%d.%m.%Y"),
            "prescribed_timestamp": self.prescribed_at.timestamp(),
            "canceled_at": self.canceled_at.strftime("%d.%m.%Y") if self.canceled_at else None,
            "sent": sent,
            "done": done,
            "medicine_database_id": self.medicine_database_id,
            "is_hidden": self.is_hidden
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

    def get_description(self, tt=False, title=True):
        medicine_description = "«{}»".format(self.title) if title else 'Дозировка: '
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
        new_medicine.atx = self.atx

        new_medicine.timetable = self.timetable
        new_medicine.warning_days = self.warning_days
        new_medicine.prescribed_at = datetime.now()

        if self.is_template:
            new_medicine.template_id = self.id
        else:
            new_medicine.template_id = self.template_id

        return new_medicine

