from functools import reduce

from sqlalchemy.orm import backref

from infrastructure import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contracts = db.relationship('Contract', backref=backref('patient', uselist=False, lazy=True), lazy=True)
    forms = db.relationship('Form', backref=backref('patient', uselist=False), lazy=True)
    medicines = db.relationship('Medicine', backref=backref('patient', uselist=False), lazy=True)
    reminders = db.relationship('Reminder', backref=backref('patient', uselist=False), lazy=True)
    algorithms = db.relationship('Algorithm', backref=backref('patient', uselist=False), lazy=True)
    examinations = db.relationship('MedicalExamination', backref=backref('patient', uselist=False), lazy=True)

    def as_dict(self):
        today = datetime.now()
        today = today.date()
        return {
            "id": self.id,
            "month_compliance": self.count_month_compliance(),
            "contracts": [contract.as_dict() for contract in self.contracts],
            "forms": [form.as_dict() for form in self.forms],
            "examinations": [examination.as_dict() for examination in
                             sorted(self.examinations, key=lambda k: k.deadline_date) if
                             examination.deadline_date >= today],
            "expired_examinations": [examination.as_dict() for examination in
                                     sorted(self.examinations, key=lambda k: k.deadline_date) if
                                     examination.deadline_date < today],
            "medicines": sorted([medicine.as_dict() for medicine in self.medicines if
                                 medicine.canceled_at is None and not medicine.is_created_by_patient],
                                key=lambda m: m['title']),
            "canceled_medicines": sorted([medicine.as_dict() for medicine in self.medicines if
                                          medicine.canceled_at is not None and not medicine.is_created_by_patient],
                                         key=lambda m: m['title']),
            "patient_medicines": [medicine.as_dict() for medicine in self.medicines if
                                  medicine.canceled_at is None and medicine.is_created_by_patient],
            "canceled_patient_medicines": [medicine.as_dict() for medicine in self.medicines if
                                           medicine.canceled_at is not None and medicine.is_created_by_patient],
            "reminders": [reminder.as_dict() for reminder in sorted(self.reminders, key=lambda k: k.attach_date) if
                          reminder.canceled_at is None],
            "old_reminders": [reminder.as_dict() for reminder in
                              sorted(self.reminders, key=lambda k: k.attach_date, reverse=True) if
                              reminder.canceled_at is not None],
            "algorithms": [algorithm.as_dict() for algorithm in self.algorithms]
        }

    def count_month_compliance(self):
        def sum_compliance(compliance, object):
            sent, done = object.current_month_compliance()
            compliance[0] += sent
            compliance[1] += done
            return compliance

        return reduce(sum_compliance, list(self.forms) + list(self.medicines), [0, 0])

    def count_week_compliance(self):
        def sum_compliance(compliance, object):
            sent, done = object.current_week_compliance()
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