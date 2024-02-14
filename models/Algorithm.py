from infrastructure import db
from datetime import datetime, timedelta
from helpers import clear_categories, get_step, extract_conditions, extract_actions, toInt
import time


class Algorithm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # actual
    steps = db.Column(db.JSON, nullable=True)
    common_conditions = db.Column(db.JSON, nullable=True)
    initial_step = db.Column(db.String(128), nullable=True)
    current_step = db.Column(db.String(128), nullable=True)
    timeout_at = db.Column(db.Integer, server_default="0")

    categories = db.Column(db.Text, nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('algorithm.id', ondelete="set null"), nullable=True)
    attached_form = db.Column(db.Integer, nullable=True)

    template_category = db.Column(db.String(512), default="Общее", nullable=True)
    clinics = db.Column(db.JSON, nullable=True)

    attach_date = db.Column(db.Date, nullable=True)
    detach_date = db.Column(db.Date, nullable=True)

    def as_dict(self, native=False):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "description": self.description,
            "steps": self.steps,
            "common_conditions": self.common_conditions,
            "categories": self.categories,
            "is_template": self.is_template,
            "template_id": self.template_id,
            "template_category": self.template_category,
            "attached_form": self.attached_form,
            "clinics": self.clinics,
            "attach_date": self.attach_date.strftime('%Y-%m-%d') if self.attach_date else None,
            "detach_date": self.detach_date.strftime('%Y-%m-%d') if self.detach_date else None
        }

    def clone(self):

        attach = datetime.now().date()
        detach = None

        if self.attach_date and self.detach_date:
            length = abs((self.detach_date - self.attach_date).days)
            detach = attach + timedelta(days=length)

        new_algorithm = Algorithm()
        new_algorithm.title = self.title
        new_algorithm.description = self.description
        new_algorithm.steps = self.steps
        new_algorithm.common_conditions = self.common_conditions
        new_algorithm.categories = clear_categories(self.categories)
        new_algorithm.attached_form = self.attached_form
        new_algorithm.initial_step = self.initial_step
        new_algorithm.attach_date = attach
        new_algorithm.detach_date = detach

        step = get_step(self)
        if not step.get('reset_minutes') or toInt(step['reset_minutes'], 0) == 0:
            new_algorithm.timeout_at = 0
        else:
            new_algorithm.timeout_at = time.time() + 60 * toInt(step['reset_minutes'], 0)

        if self.is_template:
            new_algorithm.template_id = self.id
        else:
            new_algorithm.template_id = self.template_id

        return new_algorithm

    def get_params(self):
        algorithm_params = []

        for condition in extract_conditions(self):
            for block in condition['criteria']:
                for criteria in block:
                    if criteria.get('ask_value'):
                        algorithm_params.append({
                            'code': criteria['value_code'],
                            'name': criteria['value_name'],
                            'value': criteria['value']
                        })

        for action in extract_actions(self):
            if action.get('params') and action['params'].get('script_params'):
                for param in action['params']['script_params']:
                    algorithm_params.append({
                        'code': param['value_code'],
                        'name': param['value_name'],
                        'value': param['value']
                    })

        return algorithm_params
