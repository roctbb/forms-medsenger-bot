from managers.Manager import Manager
from models import MedicineTemplate


class MedicineTemplateManager(Manager):
    def __init__(self, *args):
        super(MedicineTemplateManager, self).__init__(*args)

    def get_clinic_templates(self, clinic_id):
        medicines = MedicineTemplate.query.filter_by(clinic_id=clinic_id).all()
        return [medicine.as_dict() for medicine in medicines]
