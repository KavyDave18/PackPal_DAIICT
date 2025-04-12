from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, Alert, Checklist, TeamMember
from utils.auth import role_required

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/<int:checklist_id>', methods=['GET'])
@jwt_required()
def get_checklist_alerts(checklist_id):
    """Get all alerts for a specific checklist"""
    user_id = get_jwt_identity()
    
    # Check if checklist exists
    checklist = Checklist.query.get(checklist_id)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    
    # Check if user has access to this checklist
    is_team_member = TeamMember.query.filter_by(
        checklist_id=checklist_id, 
        user_id=user_id
    ).first() is not None
    
    is_creator = checklist.created_by == user_id
    
    if not (is_team_member or is_creator):
        return jsonify({"error": "You don't have access to this checklist"}), 403
    
    # Get alerts, ordered by most recent first
    alerts = Alert.query.filter_by(checklist_id=checklist_id) \
                       .order_by(Alert.created_at.desc()) \
                       .all()
    
    # Format response
    result = []
    for alert in alerts:
        result.append({
            "id": alert.id,
            "type": alert.type,
            "message": alert.message,
            "created_at": alert.created_at.isoformat()
        })
    
    return jsonify(result), 200

@alerts_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_alerts():
    """Get all alerts for the checklists accessible to the user"""
    user_id = get_jwt_identity()
    
    # Get all checklists the user has access to
    owned_checklists = Checklist.query.filter_by(created_by=user_id).all()
    team_memberships = TeamMember.query.filter_by(user_id=user_id).all()
    
    checklist_ids = [c.id for c in owned_checklists]
    for membership in team_memberships:
        if membership.checklist_id not in checklist_ids:
            checklist_ids.append(membership.checklist_id)
    
    # If user has no checklists, return empty list
    if not checklist_ids:
        return jsonify([]), 200
    
    # Get alerts for these checklists, ordered by most recent first
    alerts = Alert.query.filter(Alert.checklist_id.in_(checklist_ids)) \
                       .order_by(Alert.created_at.desc()) \
                       .limit(50) \
                       .all()
    
    # Format response
    result = []
    for alert in alerts:
        # Get checklist name
        checklist = Checklist.query.get(alert.checklist_id)
        checklist_name = checklist.name if checklist else "Unknown Checklist"
        
        result.append({
            "id": alert.id,
            "type": alert.type,
            "message": alert.message,
            "checklist": {
                "id": alert.checklist_id,
                "name": checklist_name
            },
            "created_at": alert.created_at.isoformat()
        })
    
    return jsonify(result), 200

# Note: We don't need a POST endpoint for alerts since they are created
# internally in the application based on user actions 