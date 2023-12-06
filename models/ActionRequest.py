from infrastructure import db


class ActionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete="CASCADE"), nullable=True)

    action = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    is_done = db.Column(db.Boolean, default=False)

    sent = db.Column(db.DateTime(), default=db.func.current_timestamp())
    done = db.Column(db.DateTime(), nullable=True)
