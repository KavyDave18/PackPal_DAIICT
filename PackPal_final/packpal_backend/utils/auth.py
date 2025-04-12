from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import User

def role_required(allowed_roles):
    """
    Decorator for role-based access control.
    
    Args:
        allowed_roles (list): List of roles allowed to access the endpoint
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            if user.role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator 