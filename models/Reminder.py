from infrastructure import db

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    attach_date = db.Column(db.Date, nullable=True)
    detach_date = db.Column(db.Date, nullable=True)
    timetable = db.Column(db.JSON, nullable=True)

    last_sent = db.Column(db.DateTime(), nullable=True)
    send_next = db.Column(db.DateTime(), nullable=True)

    title = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(7), nullable=False)
    state = db.Column(db.Text, nullable=True)
    text = db.Column(db.Text, nullable=True)

    is_template = db.Column(db.Boolean, default=False)
    template_id = db.Column(db.Integer, db.ForeignKey('reminder.id', ondelete="set null"), nullable=True)

    canceled_at = db.Column(db.DateTime, nullable=True)
    hide_actions = db.Column(db.Boolean, default=False)

    has_order = db.Column(db.Boolean, default=False)
    order = db.Column(db.String(255), nullable=True)
    order_params = db.Column(db.JSON, nullable=True)
    order_agent_id = db.Column(db.Integer, nullable=True)

    has_action = db.Column(db.Boolean, default=False)
    action = db.Column(db.String(255), nullable=True)
    action_description = db.Column(db.String(255), nullable=True)

    has_record_params = db.Column(db.Boolean, default=False)
    record_params = db.Column(db.JSON, nullable=True)

    def timetable_description(self):
        if self.timetable['mode'] == 'dates':
            description = 'Отправляется в конкретные даты.'
        elif self.timetable['mode'] == 'daily':
            description = '{} раз(а) в день'.format(len(self.timetable['points']))
        elif self.timetable['mode'] == 'weekly':
            description = '{} раз(а) в неделю'.format(len(self.timetable['points']))
        else:
            description = '{} раз(а) в месяц'.format(len(self.timetable['points']))
        if self.timetable['mode'] not in ['dates', 'manual']:
            delta = self.detach_date - self.attach_date
            description += ' в течение {} дней'.format(abs(delta.days))
        return description

    def as_dict(self):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "patient_id": self.patient_id,
            "type": self.type,
            "title": self.title,
            "state": self.state,
            "text": self.text,
            "attach_date": self.attach_date.strftime('%Y-%m-%d') if self.attach_date else None,
            "detach_date": self.detach_date.strftime('%Y-%m-%d') if self.detach_date else None,
            "timetable": self.timetable,
            "canceled_at": self.canceled_at.strftime("%d.%m.%Y") if self.canceled_at else None,
            "is_template": self.is_template,
            "template_id": self.template_id,
            "hide_actions": self.hide_actions,
            "has_order": self.has_order,
            "order": self.order,
            "order_params": self.order_params,
            "order_agent_id": self.order_agent_id,
            "has_action": self.has_action,
            "action": self.action,
            "action_description": self.action_description,
            "has_record_params": self.has_record_params,
            "record_params": self.record_params
        }

    def clone(self):
        new_reminder = Reminder()
        new_reminder.type = self.type
        new_reminder.title = self.title
        new_reminder.state = 'active'

        new_reminder.text = self.text

        new_reminder.attach_date = self.attach_date
        new_reminder.detach_date = self.detach_date
        new_reminder.timetable = self.timetable
        new_reminder.hide_actions = self.hide_actions

        new_reminder.has_order = self.has_order
        new_reminder.order = self.order
        new_reminder.order_params = self.order_params
        new_reminder.order_agent_id = self.order_agent_id

        new_reminder.has_action = self.has_action
        new_reminder.action = self.action
        new_reminder.action_description = self.action_description

        new_reminder.has_record_params = self.has_record_params
        new_reminder.record_params = self.record_params

        if self.is_template:
            new_reminder.template_id = self.id
        else:
            new_reminder.template_id = self.template_id

        return new_reminder
