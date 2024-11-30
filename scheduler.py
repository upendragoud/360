from datetime import datetime, timedelta
from app.authentication.models import User
from app import db


def rotate_api_keys():
    print("Running the API key rotation task...")

    threshold_date = datetime.utcnow() - timedelta(days=180)
    old_keys = User.query.filter(User.api_key_creation_date <= threshold_date).all()

    for user in old_keys:
        user.generate_api_key()
        db.session.commit()
    print("API key rotation task completed.")
