from helpers import log
from managers.Manager import Manager
from models import Patient, Contract


class ContractManager(Manager):
    def __init__(self, *args):
        super(ContractManager, self).__init__(*args)

    def add(self, contract_id, clinic_id):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            patient_info = self.medsenger_api.get_patient_info(contract_id)

            try:
                patient_id = int(patient_info['id'])
            except:
                raise Exception("No patient info, contract_id = {}".format(contract_id))

            patient = Patient.query.filter_by(id=patient_id).first()
            if not patient:
                patient = Patient(id=patient_id)
                self.db.session.add(patient)

            contract = Contract(id=contract_id, patient_id=patient.id, clinic_id=clinic_id)
            self.db.session.add(contract)

        contract.is_active = True
        contract.clinic_id = clinic_id
        contract.agent_token = self.medsenger_api.get_agent_token(contract_id).get('agent_token')

        self.__commit__()

        return contract

    def remove(self, contract_id):
        try:
            contract = Contract.query.filter_by(id=contract_id).first()

            if not contract:
                raise Exception("No contract_id = {} found".format(contract_id))

            contract.is_active = False

            for object in contract.forms + contract.algorithms + contract.medicines:
                self.db.session.delete(object)


            self.__commit__()
        except Exception as e:
            log(e)

    def get_patient(self, contract_id):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            raise Exception("No contract_id = {} found".format(contract_id))

        return contract.patient

    def get(self, contract_id):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            raise Exception("No contract_id = {} found".format(contract_id))

        return contract

    def get_active_ids(self):
        return [contract.id for contract in Contract.query.filter_by(is_active=True).all()]

