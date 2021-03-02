from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()

# models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contracts = db.relationship('Contract', backref=backref('patient', uselist=False), lazy=True)
    forms = db.relationship('Form', backref=backref('patient', uselist=False), lazy=True)
    medicines = db.relationship('Medicine', backref=backref('patient', uselist=False), lazy=True)
    algorithms = db.relationship('Algorithm', backref=backref('patient', uselist=False), lazy=True)

    def as_dict(self):
        return {
            "id": self.id,
            "contracts": [contract.as_dict() for contract in self.contracts],
            "forms": [form.as_dict() for form in self.forms],
            "medicines": [medicine.as_dict() for medicine in self.medicines],
            "algorithms": [algorithm.as_dict() for algorithm in self.algorithms]
        }

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    agent_token = db.Column(db.String(255), nullable=True)

    forms = db.relationship('Form', backref=backref('contract', uselist=False), lazy=True)
    medicines = db.relationship('Medicine', backref=backref('contract', uselist=False), lazy=True)
    algorithms = db.relationship('Algorithm', backref=backref('contract', uselist=False), lazy=True)

    is_admin = db.Column(db.Boolean, default=False)

    def as_dict(self, native=False):
        serialized = {
            "id": self.id,
        }

        if native:
            serialized['agent_token'] = self.agent_token

        return serialized

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    rules = db.Column(db.Text, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete="set null"), nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "rules": self.rules,
            "timetable": self.timetable,
            "is_template": self.is_template,
            "template_id": self.template_id
        }

    def timetable_description(self):
        if self.timetable['mode'] == 'daily':
            return '{} раз(а) в день'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'weekly':
            return '{} раз(а) в неделю'.format(len(self.timetable['points']))
        else:
            return '{} раз(а) в месяц'.format(len(self.timetable['points']))

    def clone(self):
        new_medicine = Medicine()
        new_medicine.title = self.title
        new_medicine.rules = self.drules

        new_medicine.timetable = self.timetable
        new_medicine.actions = self.actions

        if self.is_template:
            new_medicine.template_id = self.id
        else:
            new_medicine.template_id = self.template_id

        return new_medicine

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    doctor_description = db.Column(db.Text, nullable=True)
    patient_description = db.Column(db.Text, nullable=True)

    show_button = db.Column(db.Boolean, default=False)
    button_title = db.Column(db.String(255), nullable=True)

    fields = db.Column(db.JSON, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)

    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('form.id', ondelete="set null"), nullable=True)
    categories = db.Column(db.String(512), nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "doctor_description": self.doctor_description,
            "patient_description": self.patient_description,
            "fields": self.fields,
            "timetable": self.timetable,
            "is_template": self.is_template,
            "template_id": self.template_id
        }

    def clone(self):
        new_form = Form()
        new_form.title = self.title
        new_form.doctor_description = self.doctor_description
        new_form.patient_description = self.patient_description
        new_form.show_button = self.show_button
        new_form.button_title = self.button_title
        new_form.fields = self.fields
        new_form.timetable = self.timetable
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

    criteria = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)

    categories = db.Column(db.String(512), nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('algorithm.id', ondelete="set null"), nullable=True)

    def as_dict(self, native=False):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "description": self.description,
            "criteria": self.criteria,
            "actions": self.actions,
            "categories": self.categories,
            "is_template": self.is_template,
            "template_id": self.template_id
        }

    def clone(self):
        new_algorithm = Algorithm()
        new_algorithm.title = self.title
        new_algorithm.description = self.description

        new_algorithm.criteria = self.criteria
        new_algorithm.actions = self.actions
        new_algorithm.categories = self.categories

        if self.is_template:
            new_algorithm.template_id = self.id
        else:
            new_algorithm.template_id = self.template_id

        return new_algorithm
