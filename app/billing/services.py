from datetime import datetime, timezone
from app import db
from .models import Billing
from app.log_handler import get_logger
from app.organizations.models import Organizations
from app.authentication.models import User, Profile
from app.pricing.models import Pricing


current_datetime_utc = datetime.now(timezone.utc)

# Convert datetime to Unix timestamp
timestamp = int(current_datetime_utc.timestamp())


logger = get_logger()


def get_billings_service():
    try:
        query = db.session.query(Billing.billing_id, Billing.billing_date, Billing.start_date, Billing.end_date,
                                 Billing.org_id, Billing.plan_id, Billing.is_deleted).filter(Billing.is_deleted == 0)
        billings = query.all()
        item = {}
        output = []
        column_names = query.statement.columns.keys()
        for i in range(len(billings)):
            for j in range(len(billings[i])):
                item[column_names[j]] = billings[i][j]
            output.append(item)
            item = {}
        return output
    except Exception as e:
        logger.error(f"Error fetching billings: {e}")
        return None


def get_billing_service(bid):
    try:
        query = db.session.query(Billing.billing_id, Billing.billing_date, Billing.start_date, Billing.end_date,
                                 Billing.org_id, Billing.plan_id, Billing.is_deleted).filter(
            Billing.billing_id == bid).filter(Billing.is_deleted == 0)
        billing = query.first()
        if billing is not None:
            column_names = query.statement.columns.keys()
            output = {}
            for i in range(len(column_names)):
                output[column_names[i]] = billing[i]
            return output
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching billing details for " + str(bid) + ": {e}")
        return None


def get_org_billings_service(oid):
    try:
        query = db.session.query(Billing.billing_id, Billing.billing_date, Billing.start_date, Billing.end_date,
                                 Billing.org_id, Billing.plan_id, Billing.is_deleted).filter(
            Billing.org_id == oid).filter(Billing.is_deleted == 0)
        billings = query.all()
        item = {}
        output = []
        column_names = query.statement.columns.keys()
        for i in range(len(billings)):
            for j in range(len(billings[i])):
                item[column_names[j]] = billings[i][j]
            output.append(item)
            item = {}
        return output
    except Exception as e:
        logger.error(f"Error fetching billing details for org" + str(oid) + ": {e}")
        return None


def create_billing_service(data):
    try:
        new_billing = Billing(**data)
        db.session.add(new_billing)
        db.session.commit()
        bid = new_billing.billing_id
        billing = get_billing_service(bid)
        return billing
    except Exception as e:
        logger.error(f"Error creating billing entry: {e}")
        db.session.rollback()
        return None


def get_billing_by_user_id_services(user_id):
    try:
        query = db.session.query(Billing.billing_id,Billing.org_id, Billing.amount, Billing.billing_date, Billing.end_date, Billing.is_deleted,
                                Billing.plan_id, Billing.start_date, User.user_email,User.user_id,Organizations.org_name,
                                Profile.f_name, Profile.l_name, Pricing.description, Pricing.name, Pricing.price) \
                .join(Pricing, Billing.plan_id == Pricing.plan_id) \
                .join(Organizations, Organizations.org_id == Billing.org_id) \
                .join(User, Organizations.org_id == User.org_id) \
                .join(Profile, Profile.user_id == User.user_id) \
                .filter(User.user_id == user_id) \
                .filter(Billing.is_deleted==0) 
        result = query.all()        
        item = {}
        output = []
        column_names = query.statement.columns.keys()
        for i in range(len(result)):
            for j in range(len(result[i])):
                item[column_names[j]] = result[i][j]
            output.append(item)
            item = {}
        return output
    except Exception as e:
        logger.error(f"Error retriveing Account: {e}")
        db.session.rollback()
        return None
