from managers.Manager import Manager
from tasks import threader


class HookManager(Manager):
    def __init__(self, *args):
        super().__init__(*args)

    def create_hooks_after_creation(self, algorithm):
        self._change_hooks(algorithm, "add")

    def remove_hooks_before_deletion(self, algorithm):
        self._change_hooks(algorithm, "remove")

    def clear_contract(self, contract):
        self.medsenger_api.remove_hooks(contract.id, [])

    def _change_hooks(self, algorithm, action="add"):
        patient = algorithm.patient
        if not algorithm.patient or not algorithm.categories:
            return
        current_categories = self._get_current_categories_for_patient(patient, algorithm.id)
        alg_categories = set(algorithm.categories.split('|'))
        categories_for_action = alg_categories.difference(current_categories)

        if action == "add":
            if categories_for_action:
                threader.async_add_hooks.delay(algorithm.contract_id, list(categories_for_action))
        else:
            threader.async_remove_hooks.delay(algorithm.contract_id, list(categories_for_action))

    def _get_current_categories_for_patient(self, patient, discard_id=None):
        current_categories = set()
        for other_algorithm in patient.algorithms:
            if discard_id and other_algorithm.id == discard_id:
                continue

            other_categories = other_algorithm.categories.split('|')
            if other_categories:
                current_categories = current_categories.union(set(other_categories))

        return current_categories
