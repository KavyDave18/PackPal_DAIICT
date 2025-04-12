from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulate a database with a dictionary
users = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@packpal.com",
        "role": "admin"
    },
    {
        "id": 2,
        "username": "john",
        "email": "john@example.com",
        "role": "user"
    }
]

checklists = [
    {
        "id": 1,
        "title": "Summer Trip",
        "creator_id": 1,
        "items": [
            {"id": 1, "text": "Clothes", "checked": True},
            {"id": 2, "text": "Toiletries", "checked": False},
            {"id": 3, "text": "Electronics", "checked": False}
        ]
    },
    {
        "id": 2,
        "title": "Camping Trip",
        "creator_id": 2,
        "items": [
            {"id": 1, "text": "Tent", "checked": True},
            {"id": 2, "text": "Sleeping bag", "checked": True},
            {"id": 3, "text": "Food supplies", "checked": False}
        ]
    }
]

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to PackPal API",
        "version": "1.0.0",
        "status": "Running"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    # Simple mock login, doesn't actually check passwords
    return jsonify({
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@packpal.com"
        },
        "token": "mock-jwt-token-for-testing",
        "message": "Login successful"
    })

@app.route('/api/checklists', methods=['GET'])
def get_checklists():
    return jsonify({
        "checklists": checklists,
        "count": len(checklists)
    })

@app.route('/api/checklists/<int:checklist_id>', methods=['GET'])
def get_checklist(checklist_id):
    checklist = next((c for c in checklists if c["id"] == checklist_id), None)
    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404
    return jsonify(checklist)

@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify({
        "members": users,
        "count": len(users)
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = [
        {"id": 1, "message": "New trip created", "user_id": 1, "read": False},
        {"id": 2, "message": "Item checked off", "user_id": 2, "read": True}
    ]
    return jsonify({
        "alerts": alerts,
        "count": len(alerts)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 