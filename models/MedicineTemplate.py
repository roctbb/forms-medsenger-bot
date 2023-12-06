from infrastructure import db

class MedicineTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    clinic_id = db.Column(db.Integer, nullable=True)

    title = db.Column(db.String(255), nullable=True)
    rules = db.Column(db.Text, nullable=True)
    dose = db.Column(db.Text, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)

    def as_dict(self):
        return {
            "clinic_id": self.clinic_id,
            "title": self.title,
            "rules": self.rules,
            "dose": self.dose
        }

