"""
Avoor - API misc routes
(c) 2024-2025 githubcatw & Claude
"""
from flask import Blueprint, request

from .. import db
from ..models import DeleteFeedback
from ..decorators import api_confirmation_required
from ..bouncer import is_version_allowed

api = Blueprint('api_misc', __name__)

@api.route('/api/sendFeedback', methods=['POST'])
@api_confirmation_required
def send_feedback(current_user):
    if "id" not in request.json:
        return {"msg":"Missing feedback"}, 400
    feedback_type = request.json["id"]

    reason = None
    if "reason" in request.json:
        feedback_type = request.json["reason"]

    # save this feedback
    fb = DeleteFeedback(reason_id = feedback_type, body = reason)
    # add the new feedback to the database
    db.session.add(fb)
    db.session.commit()

    # return it
    return {"msg":"Success"}

@api.route('/api/bouncer', methods=['GET'])
def bouncer():
    """Check if the user is using a supported version of Planbot."""
    # read the user agent
    ua = request.headers.get('User-Agent')
    # in case of a failure, reject the version
    if not ua:
        return {
            "allowed": False
        }

    # check the version and return the verdict
    return {
        "allowed": is_version_allowed(ua)
    }
