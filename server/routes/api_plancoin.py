"""
Avoor - API plancoin routes
(c) 2024-2026 githubcatw & Claude
"""
from flask import Blueprint, request

from .. import db
from ..models import PlancoinTransaction, PlancoinReward
from ..decorators import api_confirmation_required, api_auth_required

api = Blueprint('api_plancoin', __name__)

@api.route('/api/plancoins/add', methods=['POST'])
@api_confirmation_required
def add_plancoins(current_user):
    """
    Add plancoins to the user's account.
    For now, plancoins are received from the client.
    """
    content = request.json
    if "amount" not in content:
        return {"msg": "Missing amount"}, 400

    amount = content["amount"]
    if not isinstance(amount, int) or amount <= 0:
        return {"msg": "Invalid amount"}, 400

    # Create a transaction record
    transaction = PlancoinReward(
        user_id=current_user.id,
        amount=amount,
        reason=content.get("reason", "Added from client")
    )
    db.session.add(transaction)

    # Update user's plancoin balance
    current_user.plancoins += amount
    db.session.commit()

    return {
        "msg": "Success",
        "plancoins": current_user.plancoins
    }

@api.route('/api/plancoins/history', methods=['GET'])
@api_auth_required
def get_plancoin_history(current_user):
    """Get plancoin transaction history."""
    transactions = PlancoinTransaction.query.filter_by(user_id=current_user.id).order_by(PlancoinTransaction.created_at.desc()).all()

    return {
        "transactions": [{
            "id": t.id,
            "amount": t.amount,
            "reason": t.reason,
            "createdAt": t.created_at.isoformat()
        } for t in transactions]
    }

# -------------- REWARDS ----------------

@api.route('/api/rewards', methods=['POST'])
@api_confirmation_required
def add_reward(current_user):
    """
    Add a plancoin reward to the user's account.
    """
    content = request.json
    if "name" not in content:
        return {"msg": "Missing name"}, 400
    if "cost" not in content:
        return {"msg": "Missing cost"}, 400

    name = content["name"]
    cost = content["cost"]
    if not isinstance(cost, int) or cost <= 0:
        return {"msg": "Invalid cost"}, 400

    # Check if the user has enough plancoins
    if cost > current_user.plancoins:
        return {"msg": "Insufficient funds"}, 400

    # Create a transaction record
    reward = PlancoinReward(
        user_id=current_user.id,
        name=name,
        cost=cost,
        stock=content.get("stock", -1)
    )
    db.session.add(reward)

    # Update user's plancoin balance
    current_user.plancoins -= cost
    db.session.commit()

    return {
        "msg": "Success",
        "plancoins": current_user.plancoins,
        "reward": reward
    }

@api.route('/api/rewards', methods=['GET'])
@api_auth_required
def get_rewards(current_user):
    """
    Get all rewards for the current user.
    """
    rewards = PlancoinReward.query.filter_by(user_id=current_user.id).all()
    return {
        "rewards": [{
            "id": reward.id,
            "name": reward.name,
            "cost": reward.cost,
            "stock": reward.stock
        } for reward in rewards]
    }

@api.route('/api/rewards/<id>', methods=['GET'])
@api_auth_required
def get_reward(current_user):
    """
    Get reward for the current user.
    """
    rewards = PlancoinReward.query.filter_by(user_id=current_user.id).all()
    return {
        "rewards": [{
            "id": reward.id,
            "name": reward.name,
            "cost": reward.cost,
            "stock": reward.stock
        } for reward in rewards]
    }
