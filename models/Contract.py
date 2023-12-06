from pytz import FixedOffset, timezone
from sqlalchemy.orm import backref

from infrastructure import db

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=False)
    clinic_id = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    doctor_agent_token = db.Column(db.String(255), nullable=True)
    patient_agent_token = db.Column(db.String(255), nullable=True)

    forms = db.relationship('Form', backref=backref('contract', uselist=False), lazy=True)
    medicines = db.relationship('Medicine', backref=backref('contract', uselist=False), lazy=True)
    reminders = db.relationship('Reminder', backref=backref('contract', uselist=False), lazy=True)
    algorithms = db.relationship('Algorithm', backref=backref('contract', uselist=False), lazy=True)
    examinations = db.relationship('MedicalExamination', backref=backref('contract', uselist=False), lazy=True)
    tasks = db.Column(db.JSON, nullable=True)

    is_admin = db.Column(db.Boolean, default=False)
    clinic_timezone = db.Column(db.String(255), nullable=True)
    patient_timezone_offset = db.Column(db.Integer, nullable=True)

    def as_dict(self, native=False):
        serialized = {
            "id": self.id,
            "clinic_id": self.clinic_id
        }

        if native:
            serialized['agent_token'] = self.agent_token

        return serialized

    def get_clinic_timezone(self):
        if not self.clinic_timezone:
            return None

        return timezone(self.clinic_timezone)

    def get_patient_timezone(self):
        if self.patient_timezone_offset is None:
            return None

        return FixedOffset(-1 * self.patient_timezone_offset)

    def get_actual_timezone(self):
        patient_timezone = self.get_patient_timezone()
        clinic_timezone = self.get_clinic_timezone()

        if patient_timezone is not None:
            zone = patient_timezone
        elif clinic_timezone is not None:
            zone = clinic_timezone
        else:
            zone = None

        return zone

