from datetime import datetime, timedelta


class Compliance:
    def current_month_compliance(self, action=None):
        return self.count_compliance(action, start_date=datetime.now().replace(day=1, minute=0, hour=0, second=0))

    def current_week_compliance(self, action=None):
        return self.count_compliance(action, start_date=datetime.now() - timedelta(days=7))

    def count_compliance(self, action=None, start_date=None, end_date=None):
        from . import Form, Medicine, ActionRequest

        if not action:
            if isinstance(self, Form):
                action = "form_{}".format(self.id)
            if isinstance(self, Medicine):
                action = "medicine_{}".format(self.id)

        request = ActionRequest.query.filter_by(contract_id=self.contract_id, action=action)

        if start_date:
            request = request.filter(ActionRequest.sent >= start_date)

        if end_date:
            request = request.filter(ActionRequest.sent <= end_date)

        records = request.all()

        return len(records), len(list(filter(lambda x: x.is_done, records)))
