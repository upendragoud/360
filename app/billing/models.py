from app import db


class Billing(db.Model):
    __tablename__ = 'billing'
    billing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('billing_plans.plan_id'), nullable=False)
    start_date = db.Column(db.BIGINT, nullable=False)
    end_date = db.Column(db.BIGINT, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    billing_date = db.Column(db.BIGINT, nullable=False)
    is_deleted = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "billing_id": self.billing_id,
            "org_id": self.org_id,
            "plan_id": self.plan_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "amount": self.amount,
            "billing_date": self.billing_date,
            "is_deleted": self.is_deleted
        }

    def __repr__(self):
        return f'<Billing {self.billing_id}>'

