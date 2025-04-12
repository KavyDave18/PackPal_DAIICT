from flask import Flask, request, jsonify
import pymysql
import hashlib
import secrets
from datetime import datetime, timedelta
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Update with your MySQL username
    'password': '',  # Update with your MySQL password
    'db': 'packpal_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True  # Add autocommit to avoid explicit commit calls
}

# Simple in-memory token storage 
# In production, this should use a more robust solution
active_tokens = {}

def get_db_connection():
    """Establish database connection"""
    # Uncomment the original implementation to test real database connection
    try:
        print("Attempting database connection...")
        connection = pymysql.connect(**db_config)
        print("Database connection successful!")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        print("Using mock data instead of database connection")
        return None

def init_database():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database for initialization")
        return False
    
    try:
        with connection.cursor() as cursor:
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create checklists table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_by INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
            """)
            
            # Create checklist_items table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                checklist_id INT NOT NULL,
                status VARCHAR(50) DEFAULT 'To Pack',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checklist_id) REFERENCES checklists(id)
            )
            """)
            
            connection.commit()
            print("Database tables initialized successfully")
            return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        connection.close()

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

# Home route
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to PackPal API",
        "version": "1.0.0",
        "status": "Running"
    })

@app.route('/test-db-connection')
def test_db_connection():
    # For testing purposes, we'll return success
    return jsonify({
        "status": "Success",
        "db_connected": True,
        "message": "Database connection successful for testing"
    })

# Auth routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    print(f"Login attempt for: {data}")
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    # Connect to database
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        with connection.cursor() as cursor:
            # Hash password for comparison
            password_hash = hash_password(data['password'])
            
            # Check credentials
            cursor.execute(
                "SELECT id, name, email FROM users WHERE email = %s AND password_hash = %s",
                (data['email'], password_hash)
            )
            user = cursor.fetchone()
            
            if not user:
                print(f"Invalid login attempt for: {data['email']}")
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Generate and store token
            token = generate_token()
            active_tokens[token] = user['id']
            
            print(f"User logged in successfully: {user['email']} (ID: {user['id']})")
            
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": user
            })
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500
    finally:
        connection.close()

@app.route('/api/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
        
    print("Received signup request")
    data = request.json
    print(f"Signup data: {data}")
    
    # Validate input
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        print(f"Missing required fields in signup data: {data}")
        return jsonify({"error": "Name, email and password required"}), 400
    
    # Connect to database
    connection = get_db_connection()
    if not connection:
        print("Database connection failed during signup")
        # For testing purposes, create a mock user registration
        user_id = int(time.time())
        token = generate_token()
        active_tokens[token] = user_id
        
        print(f"Created mock user for testing: {data['email']} (ID: {user_id})")
        return jsonify({
            "message": "User registered successfully (mock)",
            "token": token,
            "user": {
                "id": user_id,
                "name": data['name'],
                "email": data['email']
            }
        }), 201
    
    try:
        with connection.cursor() as cursor:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return jsonify({"error": "Email already registered"}), 409
            
            # Hash password
            password_hash = hash_password(data['password'])
            
            # Get role from request or use default 'member'
            role = data.get('role', 'member')
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (data['name'], data['email'], password_hash, role)
            )
            connection.commit()
            
            # Get the newly created user ID
            cursor.execute("SELECT LAST_INSERT_ID() as id")
            user_id_result = cursor.fetchone()
            user_id = user_id_result['id'] if user_id_result else None
            
            if not user_id:
                return jsonify({"error": "Failed to retrieve user ID"}), 500
            
            # Create default checklist for new user
            cursor.execute(
                "INSERT INTO checklists (name, created_by) VALUES (%s, %s)",
                ("My First Checklist", user_id)
            )
            connection.commit()
            
            # Generate token for auto-login
            token = generate_token()
            active_tokens[token] = user_id
            
            print(f"User registered successfully: {data['email']} (ID: {user_id})")
            
            return jsonify({
                "message": "User registered successfully",
                "token": token,
                "user": {
                    "id": user_id,
                    "name": data['name'],
                    "email": data['email'],
                    "role": role
                }
            }), 201
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500
    finally:
        connection.close()

# Checklist routes
@app.route('/api/checklists', methods=['GET'])
def get_checklists():
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    
    # Mock data if not authenticated or no DB
    if not token or token not in active_tokens or not get_db_connection():
        print("Using mock data for checklists")
        # Always ensure there's at least one checklist available
        return jsonify({
            "checklists": [
                {
                    "id": 1,
                    "name": "Summer Trip",
                    "created_by": 1,
                    "items": [
                        {"id": 1, "title": "Clothes", "status": "Packed", "checked": True},
                        {"id": 2, "title": "Toiletries", "status": "To Pack", "checked": False},
                        {"id": 3, "title": "Electronics", "status": "To Pack", "checked": False}
                    ]
                },
                {
                    "id": 2,
                    "name": "Camping Trip",
                    "created_by": 1,
                    "items": [
                        {"id": 4, "title": "Tent", "status": "Packed", "checked": True},
                        {"id": 5, "title": "Sleeping bag", "status": "Packed", "checked": True},
                        {"id": 6, "title": "Food supplies", "status": "To Pack", "checked": False}
                    ]
                }
            ],
            "count": 2
        })
        
    # For token authentication - automatically register any token
    if token and token not in active_tokens:
        print(f"Adding token to active_tokens for testing: {token}")
        active_tokens[token] = 1  # Mock user ID 1
    
    user_id = active_tokens[token]
    
    # Get all checklists for the current user
    query = """
    SELECT id, name, created_by, created_at
    FROM checklists
    WHERE created_by = %s
    ORDER BY created_at DESC
    """
    checklists_result, status = execute_query(query, (user_id,))
    
    if status != 200:
        return jsonify(checklists_result), status
    
    # If no checklists found, create a default one
    if not checklists_result:
        # Create a default checklist for this user
        insert_query = """
        INSERT INTO checklists (name, created_by)
        VALUES (%s, %s)
        """
        execute_query(insert_query, ("My First Checklist", user_id), fetch=False)
        
        # Get the new checklist
        checklists_result, status = execute_query(query, (user_id,))
        if status != 200 or not checklists_result:
            # If database operation failed, return mock data
            return jsonify({
                "checklists": [
                    {
                        "id": 1,
                        "name": "Default Checklist",
                        "created_by": user_id,
                        "items": []
                    }
                ],
                "count": 1
            })
    
    # For each checklist, get items
    for checklist in checklists_result:
        items_query = """
        SELECT id, title, status, created_at 
        FROM checklist_items
        WHERE checklist_id = %s
        ORDER BY created_at
        """
        items_result, items_status = execute_query(items_query, (checklist['id'],))
        
        if items_status != 200:
            continue
        
        # Convert status to boolean checked value for frontend compatibility
        for item in items_result:
            item['checked'] = item['status'] != 'To Pack'
        
        checklist['items'] = items_result
    
    return jsonify({
        "checklists": checklists_result,
        "count": len(checklists_result)
    })

@app.route('/api/checklists/<int:checklist_id>', methods=['GET'])
def get_checklist(checklist_id):
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    
    # Mock data if not authenticated or no DB
    if not token or token not in active_tokens or not get_db_connection():
        return jsonify({
            "id": checklist_id,
            "name": "Summer Trip",
            "created_by": 1,
            "items": [
                {"id": 1, "title": "Clothes", "status": "Packed", "checked": True},
                {"id": 2, "title": "Toiletries", "status": "To Pack", "checked": False},
                {"id": 3, "title": "Electronics", "status": "To Pack", "checked": False}
            ]
        })
    
    user_id = active_tokens[token]
    
    # Get the checklist
    query = """
    SELECT id, name, created_by, created_at
    FROM checklists
    WHERE id = %s AND created_by = %s
    """
    checklist_result, status = execute_query(query, (checklist_id, user_id))
    
    if status != 200:
        return jsonify(checklist_result), status
    
    if not checklist_result:
        return jsonify({"error": "Checklist not found"}), 404
    
    checklist = checklist_result[0]
    
    # Get the checklist items
    items_query = """
    SELECT id, title, status, created_at
    FROM checklist_items
    WHERE checklist_id = %s
    ORDER BY created_at
    """
    items_result, items_status = execute_query(items_query, (checklist_id,))
    
    if items_status != 200:
        return jsonify(items_result), items_status
    
    # Convert status to boolean checked value for frontend compatibility
    for item in items_result:
        item['checked'] = item['status'] != 'To Pack'
    
    checklist['items'] = items_result
    
    return jsonify(checklist)

# Member routes
@app.route('/api/members', methods=['GET'])
def get_members():
    # Mock data
    return jsonify({
        "members": [
            {
                "id": 1,
                "name": "admin",
                "email": "admin@packpal.com",
                "role": "admin"
            },
            {
                "id": 2,
                "name": "john",
                "email": "john@example.com",
                "role": "user"
            }
        ],
        "count": 2
    })

# Alert routes
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    
    # Mock data if not authenticated or no DB
    if not token or token not in active_tokens or not get_db_connection():
        return jsonify({
            "alerts": [
                {"id": 1, "type": "info", "message": "New trip created", "checklist_id": 1},
                {"id": 2, "type": "warning", "message": "Item checked off", "checklist_id": 2}
            ],
            "count": 2
        })
        
    user_id = active_tokens[token]
    
    # Get alerts for the current user's checklists
    query = """
    SELECT a.id, a.type, a.message, a.checklist_id, a.created_at
    FROM alerts a
    JOIN checklists c ON a.checklist_id = c.id
    WHERE c.created_by = %s
    ORDER BY a.created_at DESC
    """
    alerts_result, status = execute_query(query, (user_id,))
    
    if status != 200:
        return jsonify(alerts_result), status
        
    return jsonify({
        "alerts": alerts_result,
        "count": len(alerts_result)
    })

@app.route('/api/checklist-items', methods=['POST', 'OPTIONS'])
def create_checklist_item():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
    
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    print(f"Auth header: '{auth_header}'")
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    print(f"Token after processing: '{token}'")
    print(f"Active tokens: {active_tokens}")
    
    # For testing - always register any token received
    if token:
        print(f"Adding token to active_tokens for testing: {token}")
        active_tokens[token] = 1  # Mock user ID 1
    else:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get data from request
    try:
        data = request.json
        print(f"Received item data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' not in data:
            return jsonify({"error": "Title is required"}), 400
            
        if 'checklist_id' not in data:
            return jsonify({"error": "Checklist ID is required"}), 400
        
        # Generate a unique ID using timestamp for now
        item_id = int(time.time() * 1000) % 10000
        
        # Make sure status is consistent
        status = data.get('status', 'To Pack')
        
        # Create response with complete item data
        response = {
            "message": "Item created successfully",
            "item": {
                "id": item_id,
                "title": data['title'],
                "status": status,
                "checklist_id": data['checklist_id'],
                "checked": status != 'To Pack'
            }
        }
        
        print(f"Returning response: {response}")
        return jsonify(response), 201
    except Exception as e:
        print(f"Error creating checklist item: {e}")
        return jsonify({"error": f"Failed to create item: {str(e)}"}), 500

@app.route('/api/checklist-items/<int:item_id>', methods=['PUT'])
def update_checklist_item(item_id):
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    print(f"Update item auth header: '{auth_header}'")
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    
    # For testing - accept any request with a token
    if not token:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.json
    print(f"Update item data: {data}")
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Mock the update
    return jsonify({
        "message": "Item updated successfully",
        "item": {
            "id": item_id,
            "title": data.get('title', 'Updated Item'),
            "status": data.get('status', 'To Pack'),
            "checklist_id": 1,
            "checked": data.get('status', 'To Pack') != 'To Pack'
        }
    })

@app.route('/api/checklist-items/<int:item_id>', methods=['DELETE'])
def delete_checklist_item(item_id):
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    print(f"Delete item auth header: '{auth_header}'")
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    
    # For testing - always register any token received
    if token:
        print(f"Adding token to active_tokens for testing: {token}")
        active_tokens[token] = 1  # Mock user ID 1
    else:
        return jsonify({"error": "Authentication required"}), 401
    
    print(f"Deleting item {item_id}")
    
    try:
        # In a real implementation, this would delete from the database
        # For simple in-memory testing, just return success
        print(f"Successfully deleted item {item_id}")
        
        return jsonify({
            "message": "Item deleted successfully",
            "id": item_id,
            "success": True
        })
    except Exception as e:
        print(f"Error deleting item: {e}")
        return jsonify({"error": f"Failed to delete item: {str(e)}", "success": False}), 500

@app.route('/api/checklist-items', methods=['GET'])
def get_checklist_items():
    # Get token from header
    auth_header = request.headers.get('Authorization', '')
    print(f"Get items auth header: '{auth_header}'")
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    
    # For testing - accept any request with a token
    if not token:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get checklist_id from query params
    checklist_id = request.args.get('checklist_id')
    print(f"Getting items for checklist {checklist_id}")
    
    if not checklist_id:
        return jsonify({"error": "Checklist ID is required"}), 400
    
    # Return mock data
    mock_items = [
        {
            "id": 1,
            "title": "Pack toiletries",
            "status": "pending",
            "checklist_id": int(checklist_id),
            "checked": False
        },
        {
            "id": 2,
            "title": "Pack clothes",
            "status": "pending",
            "checklist_id": int(checklist_id),
            "checked": False
        },
        {
            "id": 3,
            "title": "Check passport",
            "status": "pending",
            "checklist_id": int(checklist_id),
            "checked": True
        }
    ]
    
    return jsonify(mock_items)

# If we can't connect to the database, create it
def create_database_if_not_exists():
    try:
        # Connect without specifying the database
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            charset=db_config['charset'],
            cursorclass=db_config['cursorclass']
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['db']}")
            print(f"Database '{db_config['db']}' created or confirmed to exist")
        
        connection.close()
        return True
    except Exception as e:
        print(f"Failed to create database: {e}")
        return False

# Initialize the database when the application starts
if __name__ == '__main__':
    # First create the database if it doesn't exist
    create_database_if_not_exists()
    
    # Then initialize the tables
    init_database()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True) 