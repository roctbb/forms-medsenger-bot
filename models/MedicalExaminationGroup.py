from infrastructure import db

class MedicalExaminationGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=True)

    examinations = db.Column(db.JSON, nullable=True)

    clinics = db.Column(db.JSON, nullable=True)
    exclude_clinics = db.Column(db.JSON, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "examinations": self.examinations,
            "clinics": self.clinics,
            "exclude_clinics": self.exclude_clinics
        }
