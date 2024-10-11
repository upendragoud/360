from app import db
import time
from app.organizations.models import Organizations
from app.resources.models import Resources


class Compliance(db.Model):
    __tablename__ = 'Compliance'

    compliance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    compliance_status = db.Column(db.String(150))
    practice_area = db.Column(db.String(250))
    title = db.Column(db.String(250), nullable=False)
    generated_on = db.Column(db.Integer, default=int(time.time()))
    total_checks = db.Column(db.Integer, default=0)
    critical_issues = db.Column(db.Integer, default=0)
    warnings = db.Column(db.Integer, default=0)
    compliant_areas = db.Column(db.Integer, default=0)
    recommendations = db.Column(db.Text)
    detailed_findings = db.Column(db.Text)
    compliance_indicators = db.Column(db.Text)
    key_issues = db.Column(db.Text)
    compliance_score = db.Column(db.Integer, default=0)
    scheduled_run = db.Column(db.Text)
    improvement_areas = db.Column(db.Text)
    org_id = db.Column(db.Integer, db.ForeignKey(Organizations.org_id))
    resource_id = db.Column(db.Integer, db.ForeignKey(Resources.resource_id))
    selected_compliance = db.Column(db.String(250), nullable=False)


    def to_dict(self):
        return {
            "compliance_status":self.compliance_status,
            "practice_area":self.practice_area,
            "title":self.title,
            "generated_on":self.generated_on if self.generated_on else int(time.time()),
            "total_checks":self.total_checks,
            "critical_issues":self.critical_issues,
            "warnings":self.warnings,
            "compliant_areas":self.compliant_areas,
            "recommendations":self.recommendations,
            "detailed_findings":self.detailed_findings,
            "compliance_indicators":self.compliance_indicators,
            "key_issues":self.key_issues,
            "compliance_score":self.compliance_score,
            "scheduled_run":self.scheduled_run,
            "improvement_areas":self.improvement_areas,
            "org_id":self.org_id,
            "resource_id":self.resource_id,
            "selected_compliance":self.selected_compliance
        }
    

