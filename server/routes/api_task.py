"""
Avoor - API task management routes
(c) 2024-2026 githubcatw & Claude
"""
from flask import Blueprint, request

from .. import db
from ..models import Task
from ..decorators import api_confirmation_required, api_auth_required

from datetime import datetime

api = Blueprint('api_task', __name__)

@api.route('/api/tasks', methods=['GET'])
@api_auth_required
def get_tasks(current_user):
    """Get all tasks for the current user."""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return {
        "tasks": [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "isCompleted": task.is_completed,
            "createdAt": task.created_at.isoformat() if task.created_at else None,
            "completedAt": task.completed_at.isoformat() if task.completed_at else None,
            "dueDate": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority
        } for task in tasks]
    }

@api.route('/api/tasks', methods=['POST'])
@api_confirmation_required
def create_task(current_user):
    """Create a new task."""
    content = request.json
    if "title" not in content:
        return {"msg": "Missing title"}, 400

    task = Task(
        user_id=current_user.id,
        title=content["title"],
        description=content.get("description"),
        priority=content.get("priority", 2),
        due_date=datetime.fromisoformat(content["dueDate"]) if "dueDate" in content else None
    )
    db.session.add(task)
    db.session.commit()

    return {
        "msg": "Success",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "isCompleted": task.is_completed,
            "createdAt": task.created_at.isoformat(),
            "priority": task.priority
        }
    }

@api.route('/api/tasks/<int:task_id>', methods=['PUT'])
@api_confirmation_required
def update_task(current_user, task_id):
    """Update a task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return {"msg": "Task not found"}, 404

    content = request.json
    if "title" in content:
        task.title = content["title"]
    if "description" in content:
        task.description = content["description"]
    if "priority" in content:
        task.priority = content["priority"]
    if "isCompleted" in content:
        task.is_completed = content["isCompleted"]
        if task.is_completed and not task.completed_at:
            task.completed_at = datetime.utcnow()
            # Note: Streak functionality is not yet implemented
        elif not task.is_completed:
            task.completed_at = None
    if "dueDate" in content:
        task.due_date = datetime.fromisoformat(content["dueDate"]) if content["dueDate"] else None

    db.session.commit()

    return {"msg": "Success"}

@api.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@api_confirmation_required
def delete_task(current_user, task_id):
    """Delete a task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return {"msg": "Task not found"}, 404

    db.session.delete(task)
    db.session.commit()

    return {"msg": "Success"}
