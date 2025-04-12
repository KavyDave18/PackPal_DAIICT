from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, TeamMember, User, Checklist, Alert
from utils.auth import role_required

members_bp = Blueprint('members', __name__)

@members_bp.route('/<int:checklist_id>', methods=['GET'])
@jwt_required()
def get_members(checklist_id):
    """Get all members of a checklist"""
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
    
    # Get team members and their details
    team_members = TeamMember.query.filter_by(checklist_id=checklist_id).all()
    
    members_data = []
    for member in team_members:
        user = User.query.get(member.user_id)
        if user:
            members_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "membership_id": member.id  # Include the TeamMember.id for removal
            })
    
    return jsonify(members_data), 200

@members_bp.route('/<int:checklist_id>', methods=['POST'])
@jwt_required()
@role_required(['owner', 'admin'])
def add_member(checklist_id):
    """Add a member to a checklist (owner/admin only)"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    data = request.get_json()
    
    # Validate required fields
    if not data.get('user_id'):
        return jsonify({"error": "User ID is required"}), 400
    
    # Check if checklist exists
    checklist = Checklist.query.get(checklist_id)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    
    # Check if user exists
    member_user = User.query.get(data['user_id'])
    if not member_user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is already a member
    existing_member = TeamMember.query.filter_by(
        checklist_id=checklist_id,
        user_id=data['user_id']
    ).first()
    
    if existing_member:
        return jsonify({"error": "User is already a member of this checklist"}), 400
    
    # Add user as a team member
    team_member = TeamMember(
        checklist_id=checklist_id,
        user_id=data['user_id']
    )
    
    db.session.add(team_member)
    
    # Create an alert for the new member
    alert = Alert(
        type='update',
        message=f"{current_user.name} added {member_user.name} to the checklist",
        checklist_id=checklist_id
    )
    db.session.add(alert)
    
    db.session.commit()
    
    return jsonify({
        "id": team_member.id,
        "checklist_id": team_member.checklist_id,
        "user": {
            "id": member_user.id,
            "name": member_user.name,
            "email": member_user.email,
            "role": member_user.role
        },
        "created_at": team_member.created_at.isoformat()
    }), 201

@members_bp.route('/<int:membership_id>', methods=['DELETE'])
@jwt_required()
@role_required(['owner', 'admin'])
def remove_member(membership_id):
    """Remove a member from a checklist (owner/admin only)"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Check if membership exists
    membership = TeamMember.query.get(membership_id)
    if not membership:
        return jsonify({"error": "Membership not found"}), 404
    
    # Get user and checklist details for the alert
    member_user = User.query.get(membership.user_id)
    checklist = Checklist.query.get(membership.checklist_id)
    
    if not member_user or not checklist:
        return jsonify({"error": "Associated user or checklist not found"}), 404
    
    # Don't allow removing the checklist owner if they're the only owner
    if membership.user_id == checklist.created_by:
        # Check if this is the only owner
        owner_count = 0
        members = TeamMember.query.filter_by(checklist_id=membership.checklist_id).all()
        for member in members:
            user = User.query.get(member.user_id)
            if user and user.role == 'owner':
                owner_count += 1
        
        if owner_count <= 1:
            return jsonify({"error": "Cannot remove the only owner of the checklist"}), 400
    
    # Remove the member
    db.session.delete(membership)
    
    # Create an alert
    alert = Alert(
        type='update',
        message=f"{current_user.name} removed {member_user.name} from the checklist",
        checklist_id=membership.checklist_id
    )
    db.session.add(alert)
    
    db.session.commit()
    
    return jsonify({"message": "Member removed successfully"}), 200

@members_bp.route('/available', methods=['GET'])
@jwt_required()
@role_required(['owner', 'admin'])
def get_available_users():
    """Get all users that can be added to checklists (for admin selection)"""
    # Get all users
    users = User.query.all()
    
    # Format the response
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        })
    
    return jsonify(result), 200 