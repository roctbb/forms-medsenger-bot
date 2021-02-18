from helpers import log
from managers.Manager import Manager
from models import Patient, Contract, Medicine


class MedicineManager(Manager):
    def __init__(self, *args):
        super(MedicineManager, self).__init__(*args)

    def delete(self, id, contract):

        medicine = Medicine.query.filter_by(id=id).first_or_404()

        if medicine.contract_id != contract.id:
            return None

        Medicine.query.filter_by(id=id).delete()

        self.__commit__()
        return id


    def create_or_edit(self, data, contract):
        try:
            medicine_id = data.get('id')
            if not medicine_id:
                medicine = Medicine()
            else:
                medicine = Medicine.query.filter_by(id=medicine_id).first_or_404()

            medicine.title = data.get('title')
            medicine.rules = data.get('rules')
            medicine.timetable = data.get('timetable')

            if data.get('is_template'):
                medicine.is_template = True
            else:
                medicine.patient_id = contract.patient_id
                medicine.contract_id = contract.id

            if not medicine_id:
                self.db.session.add(medicine)
            self.__commit__()

            return medicine
        except Exception as e:
            log(e)
            return None

