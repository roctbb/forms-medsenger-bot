class ComplianceManager:
    __manager = None

    @classmethod
    def instance(cls):
        if cls.__manager is None:
            cls.__manager = cls()

        return cls.__manager

    def __init__(self):
        self.__action_requests = {}

    def clear(self, contract_id):
        if contract_id in self.__action_requests:
            del self.__action_requests[contract_id]

    def get(self, contract_id):
        from models import ActionRequest

        if contract_id not in self.__action_requests:
            self.__action_requests[contract_id] = ActionRequest.query.filter_by(contract_id=contract_id).all()

        return self.__action_requests[contract_id]
