from app import db


class Consultants(db.Model):
    __tablename__ = 'external_assessor_orders'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessor_uid = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.BIGINT, nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    receipt = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "assessor_uid": self.assessor_uid,
            "order_date": self.order_date,
            "payment_amount": self.payment_amount,
            "receipt": self.receipt
        }

    def __repr__(self):
        return f'<Consultants {self.order_id}>'
