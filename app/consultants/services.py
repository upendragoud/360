from app import db
from .models import Consultants
from app.assessments.models import Assessments
from app.log_handler import get_logger
from sqlalchemy import and_

logger = get_logger()


def get_consultant_orders_service():
    try:
        query = db.session.query(Consultants.order_id, Consultants.assessor_uid, Consultants.order_date, Consultants.payment_amount, Consultants.receipt).join(Assessments, and_(Assessments.assessor_user_id == Consultants.assessor_uid, Assessments.assessment_type == 3)).filter(Assessments.resource_id == 1)
        consultants = query.all()
        item = {}
        output = []
        column_names = query.statement.columns.keys()
        for i in range(len(consultants)):
            for j in range(len(consultants[i])):
                item[column_names[j]] = consultants[i][j]
            output.append(item)
            item = {}
        return output
    except Exception as e:
        logger.error(f"Error fetching consultants: {e}")
        return None
