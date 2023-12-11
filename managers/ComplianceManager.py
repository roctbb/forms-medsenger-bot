class ComplianceManager:
    _singleton_instance = None

    @classmethod
    def instance(cls):
        if cls._singleton_instance is None:
            cls._singleton_instance = cls()
        return cls._singleton_instance

    def __init__(self):
        self.__action_requests = {}

    def clear(self, contract_id):
        if contract_id in self.__action_requests:
            del self.__action_requests[contract_id]

    def get(self, contract_id):
        if contract_id not in self.__action_requests:
            self._load_action_requests(contract_id)
        return self.__action_requests[contract_id]

    def _load_action_requests(self, contract_id):
        from models import ActionRequest
        self.__action_requests[contract_id] = ActionRequest.query.filter_by(contract_id=contract_id).all()
