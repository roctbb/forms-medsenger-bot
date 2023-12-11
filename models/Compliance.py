from datetime import datetime, timedelta

class Compliance:
    def current_month_compliance(self, action=None):
        return self.count_compliance(action, start_date=datetime.now().replace(day=1, minute=0, hour=0, second=0))

    def current_week_compliance(self, action=None):
        return self.count_compliance(action, start_date=datetime.now() - timedelta(days=7))

    def count_compliance(self, action=None, start_date=None, end_date=None):
        from managers import ComplianceManager
        from . import Form, Medicine

        if not action:
            if isinstance(self, Form):
                action = "form_{}".format(self.id)
            if isinstance(self, Medicine):
                action = "medicine_{}".format(self.id)

        manager = ComplianceManager.getInstance()
        action_requests = filter(lambda r: r.action == action, manager.get(self.contract_id))

        if start_date:
            action_requests = filter(lambda r: r.sent >= start_date, action_requests)

        if end_date:
            action_requests = filter(lambda r: r.sent <= end_date, action_requests)

        action_requests = list(action_requests)

        return len(action_requests), len(list(filter(lambda x: x.is_done, action_requests)))
