from flask import Flask, request, jsonify
import pymysql
import hashlib
import json
import secrets
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'packpal_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# User session tokens
active_tokens = {}

def get_db_connection():
    """Establish database connection"""
    try:
        connection = pymysql.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """Execute SQL query with error handling"""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed"}, 500
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = {"affected_rows": cursor.rowcount}
        return result, 200
    except Exception as e:
        print(f"Query execution error: {e}")
        return {"error": str(e)}, 500
    finally:
        connection.close()

def hash_password(password):
    """Create SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Generate a secure random token"""
    return secrets.token_hex(16)

def auth_required(f):
    """Decorator for routes that require authentication"""
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token not in active_tokens:
            return jsonify({"error": "Authentication required"}), 401
        user_id = active_tokens[token]
        return f(user_id, *args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/')
def home():
    """Home route"""
    return jsonify({"message": "Welcome to PackPal API"})

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    data = request.json
    required_fields = ['username', 'email', 'password']
    
    # Validate input
    for field in required_fields:
        if field not in data or not data[field].strip():
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Check if email already exists
    check_query = "SELECT id FROM users WHERE email = %s"
    result, status = execute_query(check_query, (data['email'],))
    
    if status != 200:
        return jsonify(result), status
    
    if result and len(result) > 0:
        return jsonify({"error": "Email already registered"}), 409
    
    # Hash password
    password_hash = hash_password(data['password'])
    
    # Insert new user
    insert_query = """
    INSERT INTO users (username, email, password_hash)
    VALUES (%s, %s, %s)
    """
    result, status = execute_query(
        insert_query, 
        (data['username'], data['email'], password_hash),
        fetch=False
    )
    
    if status != 200:
        return jsonify(result), status
    
    # Get the new user ID
    user_query = "SELECT id FROM users WHERE email = %s"
    user_result, user_status = execute_query(user_query, (data['email'],))
    
    if user_status != 200 or not user_result:
        return jsonify({"error": "User creation failed"}), 500
    
    user_id = user_result[0]['id']
    
    # Create default checklist
    checklist_query = """
    INSERT INTO checklists (title, creator_id)
    VALUES (%s, %s)
    """
    result, status = execute_query(
        checklist_query,
        ("My First Checklist", user_id),
        fetch=False
    )
    
    if status != 200:
        return jsonify(result), status
    
    # Get the new checklist ID
    checklist_query = """
    SELECT id FROM checklists 
    WHERE creator_id = %s 
    ORDER BY created_at DESC 
    LIMIT 1
    """
    checklist_result, checklist_status = execute_query(checklist_query, (user_id,))
    
    if checklist_status != 200 or not checklist_result:
        return jsonify({"error": "Checklist creation failed"}), 500
    
    checklist_id = checklist_result[0]['id']
    
    # Add default items
    default_items = [
        "Passport",
        "Travel Insurance",
        "Phone Charger",
        "Toiletries",
        "Medications"
    ]
    
    for item in default_items:
        item_query = """
        INSERT INTO checklist_items (text, checklist_id)
        VALUES (%s, %s)
        """
        execute_query(item_query, (item, checklist_id), fetch=False)
    
    # Create welcome alert
    alert_query = """
    INSERT INTO alerts (message, user_id)
    VALUES (%s, %s)
    """
    execute_query(
        alert_query,
        ("Welcome to PackPal! Start by customizing your checklist.", user_id),
        fetch=False
    )
    
    # Generate token for auto-login
    token = generate_token()
    active_tokens[token] = user_id
    
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "username": data['username'],
            "email": data['email']
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    required_fields = ['email', 'password']
    
    # Validate input
    for field in required_fields:
        if field not in data or not data[field].strip():
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Hash password
    password_hash = hash_password(data['password'])
    
    # Check credentials
    query = """
    SELECT id, username, email, role 
    FROM users 
    WHERE email = %s AND password_hash = %s
    """
    result, status = execute_query(query, (data['email'], password_hash))
    
    if status != 200:
        return jsonify(result), status
    
    if not result:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate and store token
    user = result[0]
    token = generate_token()
    active_tokens[token] = user['id']
    
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@auth_required
def logout(user_id):
    """User logout endpoint"""
    token = request.headers.get('Authorization')
    if token in active_tokens:
        del active_tokens[token]
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/user', methods=['GET'])
@auth_required
def get_user_info(user_id):
    """Get current user information"""
    query = "SELECT id, username, email, role FROM users WHERE id = %s"
    result, status = execute_query(query, (user_id,))
    
    if status != 200 or not result:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"user": result[0]}), 200

@app.route('/api/checklists', methods=['GET'])
@auth_required
def get_checklists(user_id):
    """Get all checklists for current user"""
    query = """
    SELECT id, title, created_at
    FROM checklists
    WHERE creator_id = %s
    ORDER BY created_at DESC
    """
    result, status = execute_query(query, (user_id,))
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"checklists": result}), 200

@app.route('/api/checklists', methods=['POST'])
@auth_required
def create_checklist(user_id):
    """Create a new checklist"""
    data = request.json
    
    if 'title' not in data or not data['title'].strip():
        return jsonify({"error": "Checklist title is required"}), 400
    
    query = """
    INSERT INTO checklists (title, creator_id)
    VALUES (%s, %s)
    """
    result, status = execute_query(query, (data['title'], user_id), fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    # Get the ID of the newly created checklist
    query = """
    SELECT id FROM checklists 
    WHERE creator_id = %s 
    ORDER BY created_at DESC 
    LIMIT 1
    """
    result, status = execute_query(query, (user_id,))
    
    if status != 200 or not result:
        return jsonify({"error": "Failed to retrieve checklist ID"}), 500
    
    checklist_id = result[0]['id']
    
    # Add items if provided
    if 'items' in data and isinstance(data['items'], list):
        for item in data['items']:
            item_query = """
            INSERT INTO checklist_items (text, checklist_id)
            VALUES (%s, %s)
            """
            execute_query(item_query, (item, checklist_id), fetch=False)
    
    return jsonify({
        "message": "Checklist created successfully",
        "checklist_id": checklist_id
    }), 201

@app.route('/api/checklists/<int:checklist_id>', methods=['GET'])
@auth_required
def get_checklist(user_id, checklist_id):
    """Get a specific checklist with its items"""
    # Verify ownership
    verify_query = """
    SELECT id FROM checklists
    WHERE id = %s AND creator_id = %s
    """
    verify_result, verify_status = execute_query(verify_query, (checklist_id, user_id))
    
    if verify_status != 200:
        return jsonify(verify_result), verify_status
    
    if not verify_result:
        return jsonify({"error": "Checklist not found or access denied"}), 404
    
    # Get checklist details
    checklist_query = "SELECT id, title, created_at FROM checklists WHERE id = %s"
    checklist_result, checklist_status = execute_query(checklist_query, (checklist_id,))
    
    if checklist_status != 200 or not checklist_result:
        return jsonify({"error": "Failed to retrieve checklist"}), 500
    
    checklist = checklist_result[0]
    
    # Get checklist items
    items_query = """
    SELECT id, text, checked, created_at
    FROM checklist_items
    WHERE checklist_id = %s
    ORDER BY id ASC
    """
    items_result, items_status = execute_query(items_query, (checklist_id,))
    
    if items_status != 200:
        return jsonify(items_result), items_status
    
    checklist['items'] = items_result
    
    return jsonify({"checklist": checklist}), 200

@app.route('/api/checklists/<int:checklist_id>', methods=['PUT'])
@auth_required
def update_checklist(user_id, checklist_id):
    """Update a checklist title"""
    data = request.json
    
    if 'title' not in data or not data['title'].strip():
        return jsonify({"error": "Checklist title is required"}), 400
    
    # Verify ownership
    verify_query = """
    SELECT id FROM checklists
    WHERE id = %s AND creator_id = %s
    """
    verify_result, verify_status = execute_query(verify_query, (checklist_id, user_id))
    
    if verify_status != 200:
        return jsonify(verify_result), verify_status
    
    if not verify_result:
        return jsonify({"error": "Checklist not found or access denied"}), 404
    
    # Update title
    update_query = "UPDATE checklists SET title = %s WHERE id = %s"
    result, status = execute_query(update_query, (data['title'], checklist_id), fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"message": "Checklist updated successfully"}), 200

@app.route('/api/checklists/<int:checklist_id>', methods=['DELETE'])
@auth_required
def delete_checklist(user_id, checklist_id):
    """Delete a checklist"""
    # Verify ownership
    verify_query = """
    SELECT id FROM checklists
    WHERE id = %s AND creator_id = %s
    """
    verify_result, verify_status = execute_query(verify_query, (checklist_id, user_id))
    
    if verify_status != 200:
        return jsonify(verify_result), verify_status
    
    if not verify_result:
        return jsonify({"error": "Checklist not found or access denied"}), 404
    
    # Delete the checklist (items will be deleted via CASCADE)
    delete_query = "DELETE FROM checklists WHERE id = %s"
    result, status = execute_query(delete_query, (checklist_id,), fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"message": "Checklist deleted successfully"}), 200

@app.route('/api/checklist-items', methods=['POST'])
@auth_required
def create_checklist_item(user_id):
    """Add an item to a checklist"""
    data = request.json
    required_fields = ['text', 'checklist_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    checklist_id = data['checklist_id']
    
    # Verify checklist ownership
    verify_query = """
    SELECT id FROM checklists
    WHERE id = %s AND creator_id = %s
    """
    verify_result, verify_status = execute_query(verify_query, (checklist_id, user_id))
    
    if verify_status != 200:
        return jsonify(verify_result), verify_status
    
    if not verify_result:
        return jsonify({"error": "Checklist not found or access denied"}), 404
    
    # Add item
    item_query = """
    INSERT INTO checklist_items (text, checklist_id)
    VALUES (%s, %s)
    """
    result, status = execute_query(item_query, (data['text'], checklist_id), fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    # Get the new item ID
    query = """
    SELECT id FROM checklist_items
    WHERE checklist_id = %s
    ORDER BY created_at DESC
    LIMIT 1
    """
    result, status = execute_query(query, (checklist_id,))
    
    if status != 200 or not result:
        return jsonify({"error": "Failed to retrieve item ID"}), 500
    
    item_id = result[0]['id']
    
    return jsonify({
        "message": "Item added successfully",
        "item_id": item_id
    }), 201

@app.route('/api/checklist-items/<int:item_id>', methods=['PUT'])
@auth_required
def update_checklist_item(user_id, item_id):
    """Update a checklist item"""
    data = request.json
    
    # Get item's checklist
    item_query = """
    SELECT ci.id, ci.checklist_id, c.creator_id
    FROM checklist_items ci
    JOIN checklists c ON ci.checklist_id = c.id
    WHERE ci.id = %s
    """
    item_result, item_status = execute_query(item_query, (item_id,))
    
    if item_status != 200:
        return jsonify(item_result), item_status
    
    if not item_result:
        return jsonify({"error": "Item not found"}), 404
    
    # Verify ownership
    if item_result[0]['creator_id'] != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Update fields
    update_fields = []
    params = []
    
    if 'text' in data and data['text'].strip():
        update_fields.append("text = %s")
        params.append(data['text'])
    
    if 'checked' in data:
        update_fields.append("checked = %s")
        params.append(bool(data['checked']))
    
    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400
    
    params.append(item_id)
    
    update_query = f"""
    UPDATE checklist_items
    SET {', '.join(update_fields)}
    WHERE id = %s
    """
    result, status = execute_query(update_query, params, fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"message": "Item updated successfully"}), 200

@app.route('/api/checklist-items/<int:item_id>', methods=['DELETE'])
@auth_required
def delete_checklist_item(user_id, item_id):
    """Delete a checklist item"""
    # Get item's checklist
    item_query = """
    SELECT ci.id, ci.checklist_id, c.creator_id
    FROM checklist_items ci
    JOIN checklists c ON ci.checklist_id = c.id
    WHERE ci.id = %s
    """
    item_result, item_status = execute_query(item_query, (item_id,))
    
    if item_status != 200:
        return jsonify(item_result), item_status
    
    if not item_result:
        return jsonify({"error": "Item not found"}), 404
    
    # Verify ownership
    if item_result[0]['creator_id'] != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Delete item
    delete_query = "DELETE FROM checklist_items WHERE id = %s"
    result, status = execute_query(delete_query, (item_id,), fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"message": "Item deleted successfully"}), 200

@app.route('/api/alerts', methods=['GET'])
@auth_required
def get_alerts(user_id):
    """Get all alerts for current user"""
    query = """
    SELECT id, message, read, created_at
    FROM alerts
    WHERE user_id = %s
    ORDER BY created_at DESC
    """
    result, status = execute_query(query, (user_id,))
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"alerts": result}), 200

@app.route('/api/alerts/<int:alert_id>', methods=['PUT'])
@auth_required
def mark_alert_read(user_id, alert_id):
    """Mark an alert as read"""
    # Verify ownership
    verify_query = """
    SELECT id FROM alerts
    WHERE id = %s AND user_id = %s
    """
    verify_result, verify_status = execute_query(verify_query, (alert_id, user_id))
    
    if verify_status != 200:
        return jsonify(verify_result), verify_status
    
    if not verify_result:
        return jsonify({"error": "Alert not found or access denied"}), 404
    
    # Mark as read
    update_query = "UPDATE alerts SET read = TRUE WHERE id = %s"
    result, status = execute_query(update_query, (alert_id,), fetch=False)
    
    if status != 200:
        return jsonify(result), status
    
    return jsonify({"message": "Alert marked as read"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 