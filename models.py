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

    last_sent = db.Column(db.DateTime(), nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "rules": self.rules,
            "timetable": self.timetable,
            "is_template": self.is_template
        }

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
            "is_template": self.is_template
        }

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

    def as_dict(self, native=False):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "criteria": self.criteria,
            "actions": self.actions,
            "is_template": self.is_template
        }
