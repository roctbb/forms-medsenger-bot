from infrastructure import db
from . import Compliance
from helpers import clear_categories

class Form(db.Model, Compliance):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    doctor_id = db.Column(db.Integer, nullable=True)
    clinic_id = db.Column(db.Integer, nullable=True)

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
    categories = db.Column(db.Text, nullable=True)

    algorithm_id = db.Column(db.Integer, db.ForeignKey('algorithm.id', ondelete="set null"), nullable=True)
    clinics = db.Column(db.JSON, nullable=True)
    exclude_clinics = db.Column(db.JSON, nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    warning_days = db.Column(db.Integer, default=0)
    warning_timestamp = db.Column(db.Integer, default=0)
    filled_timestamp = db.Column(db.Integer, default=0)
    asked_timestamp = db.Column(db.Integer, default=0)

    template_category = db.Column(db.String(512), default="Общее", nullable=True)
    instant_report = db.Column(db.Boolean, default=False, nullable=False, server_default='false')

    init_text = db.Column(db.Text, nullable=True)

    def timetable_description(self):
        if self.timetable['mode'] == 'daily':
            return '{} раз(а) в день'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'weekly':
            return '{} раз(а) в неделю'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'manual':
            return 'заполняется вручную или присылается алгоритмом'
        else:
            return '{} раз(а) в месяц'.format(len(self.timetable['points']))

    def get_description(self):
        return f"{self.title} ({self.timetable_description()})"

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
        new_form.categories = clear_categories(self.categories)
        new_form.warning_days = self.warning_days
        new_form.instant_report = self.instant_report

        if self.is_template:
            new_form.template_id = self.id
        else:
            new_form.template_id = self.template_id

        return new_form