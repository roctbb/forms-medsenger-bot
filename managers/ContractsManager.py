from helpers import log
from managers.Manager import Manager
from methods.hooks import clear_contract_hooks
from models import Patient, Contract


class ContractManager(Manager):
    def __init__(self, *args):
        super(ContractManager, self).__init__()

    def add(self, contract_id, clinic_id):
        contract = Contract.query.filter_by(id=contract_id).first()
        patient_info = self.medsenger_api.get_patient_info(contract_id)
        is_new = False
        if not contract:
            is_new = True
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
        contract.clinic_timezone = patient_info.get('timezone')
        contract.patient_timezone_offset = patient_info.get('timezone_offset')
        contract.clinic_id = clinic_id

        self.request_tokens(contract)

        self.__commit__()

        return contract, is_new

    def request_tokens(self, contract, commit=False):
        tokens = self.medsenger_api.get_agent_token(contract.id)

        contract.patient_agent_token = tokens.get('patient_agent_token')
        contract.doctor_agent_token = tokens.get('doctor_agent_token')

        if commit:
            self.__commit__()

    def remove(self, contract_id):
        try:
            contract = Contract.query.filter_by(id=contract_id).first()

            if not contract:
                raise Exception("No contract_id = {} found".format(contract_id))

            contract.is_active = False

            clear_contract_hooks(contract)

            for object in contract.forms + contract.algorithms + contract.medicines + contract.reminders + contract.examinations:
                self.db.session.delete(object)

            self.__commit__()
        except Exception as e:
            log(e)

    def get_patient(self, contract_id):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            raise Exception("No contract_id = {} found".format(contract_id))

        return contract.patient

    def get(self, contract_id, active=None):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            raise Exception("No contract_id = {} found".format(contract_id))

        return contract

    def get_active_ids(self):
        return [contract.id for contract in Contract.query.filter_by(is_active=True).all()]

    def actualize_timezone(self, contract, commit=False):
        info = self.medsenger_api.get_patient_info(contract.id)
        contract.clinic_timezone = info.get('timezone')
        contract.patient_timezone_offset = info.get('timezone_offset')

        if commit:
            self.__commit__()

    def actualize_timezones(self):
        for contract in Contract.query.filter_by(is_active=True).all():
            self.actualize_timezone(contract)

        self.__commit__()
