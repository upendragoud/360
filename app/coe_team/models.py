from app import db


class COETeam(db.Model):
    __tablename__ = 'coe_team'
    team_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    coe_area = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    coe_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_deleted = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "org_id": self.org_id,
            "coe_area": self.coe_area,
            "name": self.name,
            "description": self.description,
            "coe_admin_id": self.coe_admin_id,
            "is_deleted": self.is_deleted
        }

    def __repr__(self):
        return f'<COETeam {self.team_id}>'
