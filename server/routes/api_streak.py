"""
Avoor - API streak routes
(c) 2024-2026 githubcatw & Claude
"""
from datetime import date
from flask import Blueprint, request

from .. import db
from ..decorators import api_auth_required
from ..models import StreakUpdate

api = Blueprint('api_streak', __name__)

@api.route('/api/streak', methods=['GET'])
@api_auth_required
def get_streak(current_user):
    """Get the user's current streak information."""
    return {
        "currentStreak": current_user.current_streak,
        "longestStreak": current_user.longest_streak,
        "lastCompletionDate": current_user.last_task_completion_date.isoformat() if current_user.last_task_completion_date else None
    }


@api.route('/api/streaks', methods=['GET'])
@api_auth_required
def get_streaks(current_user):
    """Get the user's streak information including freeze data."""
    today = date.today()

    # Calculate freeze_used_today from last_freeze_date
    freeze_used_today = (
        current_user.last_freeze_date is not None and
        current_user.last_freeze_date == today
    )

    return {
        "current_streak": current_user.current_streak,
        "freeze_count": current_user.freeze_count or 0,
        "longest_streak": current_user.longest_streak,
        "last_update_date": current_user.last_task_completion_date.isoformat() if current_user.last_task_completion_date else None,
        "freeze_used_today": freeze_used_today
    }


@api.route('/api/streaks', methods=['POST'])
@api_auth_required
def post_streak(current_user):
    """Update the user's streak."""
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    update_id = data.get('update_id')
    date_str = data.get('date')

    if not update_id:
        return {"error": "update_id is required"}, 400
    if not date_str:
        return {"error": "date is required"}, 400

    # Parse the date (expecting ISO 8601 format, date only)
    try:
        update_date = date.fromisoformat(date_str)
    except ValueError:
        return {"error": "Invalid date format. Expected ISO 8601 date (YYYY-MM-DD)"}, 400

    streak_extended = True

    # Check if update_id already exists
    existing_by_id = StreakUpdate.query.filter_by(update_id=update_id).first()
    if existing_by_id:
        streak_extended = False

    # Check if user already has an update for this date
    existing_by_date = StreakUpdate.query.filter_by(
        user_id=current_user.id,
        date=update_date
    ).first()
    if existing_by_date:
        streak_extended = False

    # If this is a new update, save it and update user streak
    if streak_extended:
        # Update the user's streak
        current_user.current_streak += 1
        if current_user.current_streak > current_user.longest_streak:
            current_user.longest_streak = current_user.current_streak
        current_user.last_task_completion_date = update_date

        # Create the streak update record
        streak_update = StreakUpdate(
            update_id=update_id,
            user_id=current_user.id,
            date=update_date,
            current_streak=current_user.current_streak
        )
        db.session.add(streak_update)
        db.session.commit()

    return {
        "current_streak": current_user.current_streak,
        "freeze_count": current_user.freeze_count or 0,
        "longest_streak": current_user.longest_streak,
        "streak_extended": streak_extended
    }


@api.route('/api/streaks/freeze', methods=['GET'])
@api_auth_required
def get_streaks_freeze(current_user):
    """Get the user's streak freeze information."""
    today = date.today()

    # Check if freeze was used today
    freeze_used = (
        current_user.last_freeze_date is not None and
        current_user.last_freeze_date == today
    )

    return {
        "freeze_count": current_user.freeze_count or 0,
        "freeze_used": freeze_used,
        "current_streak": current_user.current_streak
    }
