from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, Checklist, ChecklistItem, TeamMember, Alert, User
from utils.auth import role_required

checklist_bp = Blueprint('checklist', __name__)

@checklist_bp.route('/', methods=['GET'])
@jwt_required()
def get_checklists():
    """Get all checklists accessible to the current user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # If user is owner or admin, get all checklists created by them
    if user.role in ['owner', 'admin']:
        # Get checklists created by the user
        own_checklists = Checklist.query.filter_by(created_by=user_id).all()
        # Get checklists where the user is a team member
        team_memberships = TeamMember.query.filter_by(user_id=user_id).all()
        team_checklist_ids = [tm.checklist_id for tm in team_memberships]
        team_checklists = Checklist.query.filter(Checklist.id.in_(team_checklist_ids)).all()
        # Combine lists without duplicates
        checklists = list(set(own_checklists + team_checklists))
    else:
        # For regular members and viewers, only get checklists they're part of
        team_memberships = TeamMember.query.filter_by(user_id=user_id).all()
        checklist_ids = [tm.checklist_id for tm in team_memberships]
        checklists = Checklist.query.filter(Checklist.id.in_(checklist_ids)).all()
    
    # Format response
    result = []
    for checklist in checklists:
        # Get creator name
        creator = User.query.get(checklist.created_by)
        creator_name = creator.name if creator else "Unknown"
        
        # Count items by status
        total_items = ChecklistItem.query.filter_by(checklist_id=checklist.id).count()
        packed_count = ChecklistItem.query.filter_by(checklist_id=checklist.id, status='Packed').count()
        delivered_count = ChecklistItem.query.filter_by(checklist_id=checklist.id, status='Delivered').count()
        
        result.append({
            "id": checklist.id,
            "name": checklist.name,
            "created_by": {
                "id": checklist.created_by,
                "name": creator_name
            },
            "created_at": checklist.created_at.isoformat(),
            "stats": {
                "total": total_items,
                "packed": packed_count,
                "delivered": delivered_count
            }
        })
    
    return jsonify(result), 200

@checklist_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['owner', 'admin'])
def create_checklist():
    """Create a new checklist (owner/admin only)"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data.get('name'):
        return jsonify({"error": "Checklist name is required"}), 400
    
    # Create new checklist
    checklist = Checklist(
        name=data['name'],
        created_by=user_id
    )
    
    db.session.add(checklist)
    db.session.commit()
    
    # Automatically add creator as a team member
    team_member = TeamMember(
        checklist_id=checklist.id,
        user_id=user_id
    )
    db.session.add(team_member)
    db.session.commit()
    
    # Get creator name
    creator = User.query.get(user_id)
    
    return jsonify({
        "id": checklist.id,
        "name": checklist.name,
        "created_by": {
            "id": user_id,
            "name": creator.name
        },
        "created_at": checklist.created_at.isoformat()
    }), 201

@checklist_bp.route('/<int:checklist_id>', methods=['GET'])
@jwt_required()
def get_checklist_details(checklist_id):
    """Get details of a specific checklist with items and members"""
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
    
    # Get all items for this checklist
    items = ChecklistItem.query.filter_by(checklist_id=checklist_id).all()
    items_data = []
    
    for item in items:
        assignee = None
        if item.assigned_to:
            user = User.query.get(item.assigned_to)
            if user:
                assignee = {
                    "id": user.id,
                    "name": user.name
                }
        
        items_data.append({
            "id": item.id,
            "title": item.title,
            "status": item.status,
            "assigned_to": assignee,
            "created_at": item.created_at.isoformat()
        })
    
    # Get team members
    team_members = TeamMember.query.filter_by(checklist_id=checklist_id).all()
    members_data = []
    
    for member in team_members:
        user = User.query.get(member.user_id)
        if user:
            members_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            })
    
    # Get creator info
    creator = User.query.get(checklist.created_by)
    creator_name = creator.name if creator else "Unknown"
    
    # Format response
    response = {
        "id": checklist.id,
        "name": checklist.name,
        "created_by": {
            "id": checklist.created_by,
            "name": creator_name
        },
        "created_at": checklist.created_at.isoformat(),
        "items": items_data,
        "members": members_data
    }
    
    return jsonify(response), 200

@checklist_bp.route('/<int:checklist_id>', methods=['PUT'])
@jwt_required()
@role_required(['owner', 'admin'])
def update_checklist(checklist_id):
    """Update a checklist name (owner/admin only)"""
    data = request.get_json()
    
    # Validate input
    if not data.get('name'):
        return jsonify({"error": "Checklist name is required"}), 400
    
    # Check if checklist exists
    checklist = Checklist.query.get(checklist_id)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    
    # Update checklist
    checklist.name = data['name']
    db.session.commit()
    
    return jsonify({
        "id": checklist.id,
        "name": checklist.name,
        "created_by": checklist.created_by,
        "created_at": checklist.created_at.isoformat()
    }), 200

@checklist_bp.route('/<int:checklist_id>', methods=['DELETE'])
@jwt_required()
@role_required(['owner'])
def delete_checklist(checklist_id):
    """Delete a checklist (owner only)"""
    # Check if checklist exists
    checklist = Checklist.query.get(checklist_id)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    
    # Delete checklist (cascade will handle related items, members, and alerts)
    db.session.delete(checklist)
    db.session.commit()
    
    return jsonify({"message": "Checklist deleted successfully"}), 200

@checklist_bp.route('/<int:checklist_id>/items', methods=['POST'])
@jwt_required()
@role_required(['owner', 'admin'])
def add_item(checklist_id):
    """Add an item to a checklist (owner/admin only)"""
    data = request.get_json()
    
    # Validate input
    if not data.get('title'):
        return jsonify({"error": "Item title is required"}), 400
    
    # Check if checklist exists
    checklist = Checklist.query.get(checklist_id)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    
    # Create new item
    item = ChecklistItem(
        title=data['title'],
        checklist_id=checklist_id,
        status='To Pack'
    )
    
    # Handle assignment if provided
    if data.get('assigned_to'):
        # Verify the assigned user exists and is a team member
        user = User.query.get(data['assigned_to'])
        if not user:
            return jsonify({"error": "Assigned user not found"}), 404
        
        is_team_member = TeamMember.query.filter_by(
            checklist_id=checklist_id, 
            user_id=data['assigned_to']
        ).first() is not None
        
        if not is_team_member:
            return jsonify({"error": "User is not a member of this checklist"}), 400
        
        item.assigned_to = data['assigned_to']
    
    db.session.add(item)
    db.session.commit()
    
    # Format assignee data
    assignee = None
    if item.assigned_to:
        user = User.query.get(item.assigned_to)
        if user:
            assignee = {
                "id": user.id,
                "name": user.name
            }
    
    return jsonify({
        "id": item.id,
        "title": item.title,
        "status": item.status,
        "checklist_id": item.checklist_id,
        "assigned_to": assignee,
        "created_at": item.created_at.isoformat()
    }), 201

@checklist_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """Update an item's status or assignment"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    # Check if item exists
    item = ChecklistItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # Check if user has access to this checklist
    is_team_member = TeamMember.query.filter_by(
        checklist_id=item.checklist_id, 
        user_id=user_id
    ).first() is not None
    
    if not is_team_member:
        return jsonify({"error": "You don't have access to this checklist"}), 403
    
    # Get the checklist for alert creation
    checklist = Checklist.query.get(item.checklist_id)
    
    # Handle status updates
    if data.get('status'):
        # Validate status
        valid_statuses = ['To Pack', 'Packed', 'Delivered']
        if data['status'] not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        # Check if user has permission to update status
        if user.role in ['member', 'viewer']:
            if item.assigned_to != user_id:
                # Create an alert for this unauthorized attempt
                alert = Alert(
                    type='conflict',
                    message=f"{user.name} attempted to mark '{item.title}' as {data['status']} but was not assigned to it",
                    checklist_id=item.checklist_id
                )
                db.session.add(alert)
                
                # Only allow if user is assigned to this item
                if user.role == 'viewer':
                    return jsonify({"error": "Viewers cannot update item status"}), 403
                elif user.role == 'member' and item.assigned_to is not None and item.assigned_to != user_id:
                    return jsonify({"error": "You can only update items assigned to you"}), 403
        
        old_status = item.status
        item.status = data['status']
        
        # Create an alert for status change
        alert = Alert(
            type='update',
            message=f"{user.name} changed '{item.title}' status from '{old_status}' to '{data['status']}'",
            checklist_id=item.checklist_id
        )
        db.session.add(alert)
    
    # Handle assignment updates (owner/admin only)
    if data.get('assigned_to') is not None and user.role in ['owner', 'admin']:
        # If assigned_to is null, remove assignment
        if data['assigned_to'] is None:
            item.assigned_to = None
        else:
            # Verify the assigned user exists and is a team member
            assigned_user = User.query.get(data['assigned_to'])
            if not assigned_user:
                return jsonify({"error": "Assigned user not found"}), 404
            
            is_team_member = TeamMember.query.filter_by(
                checklist_id=item.checklist_id, 
                user_id=data['assigned_to']
            ).first() is not None
            
            if not is_team_member:
                return jsonify({"error": "User is not a member of this checklist"}), 400
            
            # Check for conflicting assignment
            existing_items = ChecklistItem.query.filter_by(
                checklist_id=item.checklist_id,
                title=item.title,
                assigned_to=data['assigned_to']
            ).all()
            
            if existing_items and item.id not in [i.id for i in existing_items]:
                # Create conflict alert
                existing_assignee = User.query.get(item.assigned_to) if item.assigned_to else None
                new_assignee = User.query.get(data['assigned_to'])
                
                alert = Alert(
                    type='conflict',
                    message=f"Potential conflict: '{item.title}' assigned to both {existing_assignee.name if existing_assignee else 'nobody'} and {new_assignee.name}",
                    checklist_id=item.checklist_id
                )
                db.session.add(alert)
            
            item.assigned_to = data['assigned_to']
    
    db.session.commit()
    
    # Format assignee data
    assignee = None
    if item.assigned_to:
        assigned_user = User.query.get(item.assigned_to)
        if assigned_user:
            assignee = {
                "id": assigned_user.id,
                "name": assigned_user.name
            }
    
    return jsonify({
        "id": item.id,
        "title": item.title,
        "status": item.status,
        "checklist_id": item.checklist_id,
        "assigned_to": assignee,
        "created_at": item.created_at.isoformat()
    }), 200

@checklist_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
@role_required(['owner', 'admin'])
def delete_item(item_id):
    """Delete an item (owner/admin only)"""
    # Check if item exists
    item = ChecklistItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({"message": "Item deleted successfully"}), 200

@checklist_bp.route('/<int:checklist_id>/progress', methods=['GET'])
@jwt_required()
def get_progress(checklist_id):
    """Get progress statistics for a checklist"""
    # Check if checklist exists
    checklist = Checklist.query.get(checklist_id)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    
    # Check if user has access
    user_id = get_jwt_identity()
    is_team_member = TeamMember.query.filter_by(
        checklist_id=checklist_id, 
        user_id=user_id
    ).first() is not None
    
    is_creator = checklist.created_by == user_id
    
    if not (is_team_member or is_creator):
        return jsonify({"error": "You don't have access to this checklist"}), 403
    
    # Count items by status
    total_items = ChecklistItem.query.filter_by(checklist_id=checklist_id).count()
    
    if total_items == 0:
        return jsonify({
            "checklist_id": checklist_id,
            "total_items": 0,
            "to_pack": {"count": 0, "percent": 0},
            "packed": {"count": 0, "percent": 0},
            "delivered": {"count": 0, "percent": 0}
        }), 200
    
    to_pack_count = ChecklistItem.query.filter_by(checklist_id=checklist_id, status='To Pack').count()
    packed_count = ChecklistItem.query.filter_by(checklist_id=checklist_id, status='Packed').count()
    delivered_count = ChecklistItem.query.filter_by(checklist_id=checklist_id, status='Delivered').count()
    
    # Calculate percentages
    to_pack_percent = round((to_pack_count / total_items) * 100, 1)
    packed_percent = round((packed_count / total_items) * 100, 1)
    delivered_percent = round((delivered_count / total_items) * 100, 1)
    
    return jsonify({
        "checklist_id": checklist_id,
        "total_items": total_items,
        "to_pack": {
            "count": to_pack_count,
            "percent": to_pack_percent
        },
        "packed": {
            "count": packed_count,
            "percent": packed_percent
        },
        "delivered": {
            "count": delivered_count,
            "percent": delivered_percent
        }
    }), 200 