from infrastructure import db
from datetime import datetime

class MedicalExamination(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('medical_examination.id', ondelete="set null"), nullable=True)
    clinics = db.Column(db.JSON, nullable=True)
    exclude_clinics = db.Column(db.JSON, nullable=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    attach_date = db.Column(db.Date, nullable=True)
    upload_date = db.Column(db.Date, nullable=True)
    notification_date = db.Column(db.Date, nullable=True)
    deadline_date = db.Column(db.Date, nullable=True)

    asked = db.Column(db.Boolean, default=False)

    title = db.Column(db.String(255), nullable=True)
    template_category = db.Column(db.String(255), nullable=True)
    doctor_description = db.Column(db.Text, nullable=True)
    patient_description = db.Column(db.Text, nullable=True)

    no_expiration = db.Column(db.Boolean, nullable=True, default=False)
    expiration_days = db.Column(db.Integer, default=0)
    record_id = db.Column(db.Integer, nullable=True)

    next_run_timestamp = db.Column(db.Integer, nullable=True)

    def clone(self):
        new_examination = MedicalExamination()

        new_examination.title = self.title
        new_examination.template_category = self.template_category
        new_examination.doctor_description = self.doctor_description
        new_examination.patient_description = self.patient_description

        new_examination.no_expiration = self.no_expiration
        new_examination.expiration_days = self.expiration_days
        new_examination.attach_date = datetime.now()

        if self.is_template:
            new_examination.template_id = self.id
        else:
            new_examination.template_id = self.template_id

        return new_examination

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "template_category": self.template_category,
            "doctor_description": self.doctor_description,
            "patient_description": self.patient_description,
            "patient_id": self.patient_id,
            "contract_id": self.contract_id,
            "no_expiration": self.no_expiration,
            "expiration_days": self.expiration_days,
            "asked": self.asked,
            "record_id": self.record_id,
            "is_template": self.is_template,
            "clinics": self.clinics,
            "exclude_clinics": self.exclude_clinics,
            "template_id": self.template_id,
            "attach_date": self.attach_date.strftime('%Y-%m-%d') if self.attach_date else None,
            "upload_date": self.upload_date.strftime('%Y-%m-%d') if self.upload_date else None,
            "notification_date": self.notification_date.strftime('%Y-%m-%d') if self.notification_date else None,
            "deadline_date": self.deadline_date.strftime('%Y-%m-%d') if self.deadline_date else None,
        }

