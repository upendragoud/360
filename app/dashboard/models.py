from app import db


'''
class TaskStatus(db.Model):
    __tablename__ = 'task_status'
    task_status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_status_name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "task_status_id": self.task_status_id,
            "task_status_name": self.task_status_name
        }

    def __repr__(self):
        return f'<TaskStatus {self.task_status_id}>'
'''