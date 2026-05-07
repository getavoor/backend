"""
Avoor - Database Models
(c) 2024-2025 githubcatw & Claude
"""
from flask_login import UserMixin
from datetime import datetime
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy

    # email
    email = db.Column(db.String(100), unique=True)
    # hashed password
    password = db.Column(db.String(250), nullable=False)
    # name
    name = db.Column(db.String(1000), nullable=False)
    # is the user an admin?
    is_admin = db.Column(db.Boolean())
    # has the user confirmed their email?
    is_confirmed = db.Column(db.Boolean(), default=False)
    # is developer mode enabled for this user?
    is_dev = db.Column(db.Boolean())
    # photo
    photo_url = db.Column(db.String(1000))
    # plancoins balance
    plancoins = db.Column(db.Integer, default=0)
    # current streak count
    current_streak = db.Column(db.Integer, default=0)
    # longest streak achieved
    longest_streak = db.Column(db.Integer, default=0)
    # last task completion date (for streak tracking)
    last_task_completion_date = db.Column(db.Date)
    # streak freeze count
    freeze_count = db.Column(db.Integer, default=0)
    # last date a freeze was used
    last_freeze_date = db.Column(db.Date)

    # relationships
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    plancoin_transactions = db.relationship('PlancoinTransaction', backref='user', lazy=True, cascade='all, delete-orphan')

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id

        return False

class Task(db.Model):
    """
    Represents a user task in the time management system.
    Note: Streak functionality is not yet implemented.
    """
    id = db.Column(db.Integer, primary_key=True)

    # user id (foreign key)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # task details
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(5000))

    # status
    is_completed = db.Column(db.Boolean(), default=False)

    # timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)

    # priority level (1=low, 2=medium, 3=high)
    priority = db.Column(db.Integer, default=2)

class PlancoinTransaction(db.Model):
    """
    Represents a plancoin transaction.
    For now, plancoins are received from the client.
    """
    id = db.Column(db.Integer, primary_key=True)

    # user id (foreign key)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # transaction details
    amount = db.Column(db.Integer, nullable=False)  # can be positive or negative
    reason = db.Column(db.String(500))  # why the transaction occurred

    # timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DeleteFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy

    # the reason for deleting the account
    reason_id = db.Column(db.String(50), nullable=False)
    # optional body (in case the user selected "Other")
    body = db.Column(db.String(2000), nullable=True)

class PlancoinReward(db.Model):
    """
    Represents a (primarily user-defined) plancoin reward.
    """
    id = db.Column(db.String, primary_key=True)

    # user id (foreign key)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # name
    name = db.Column(db.String(1000), nullable=False)
    # cost
    cost = db.Column(db.Integer, nullable=False)  # must be positive or negative
    # stock (-1 is unlimited)
    stock = db.Column(db.Integer, nullable=False)  # must be positive or negative

class StreakUpdate(db.Model):
    """
    Represents a streak update.

    A streak update is how a client notifies the backend of the streak being updated.
    """
    update_id = db.Column(db.String, primary_key=True)

    # user id (foreign key) - needed to track per-user updates
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # date of the streak update (date only, no time)
    date = db.Column(db.Date, nullable=False)

    # streak at the time of the update
    current_streak = db.Column(db.Integer, nullable=False)
