# PackPal Backend API

Backend for the PackPal Group Logistics Organizer application.

## Features

- User authentication with JWT tokens and role-based access control
- Create and manage packing checklists for events or trips
- Assign items to team members with status tracking
- Add and manage team members for each checklist
- Smart alert system for conflicts and updates
- Progress tracking for checklist completion

## Tech Stack

- Python 3.8+ with Flask framework
- Flask-SQLAlchemy ORM for database interactions
- MySQL database
- JWT-based authentication
- CORS support for frontend integration

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd packpal_backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure the database:
```bash
# Log in to MySQL
mysql -u root -p

# In MySQL prompt, run:
source schema.sql
# Then exit MySQL
exit
```

6. Create a `.env` file in the project root with the following content:
```
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=mysql://username:password@localhost/packpal_db
JWT_SECRET_KEY=your-secret-key-here
```
Replace `username` and `password` with your MySQL credentials.

### Starting the Application

1. Start the Flask server:
```bash
flask run
```

2. The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/login` - Authenticate and get JWT token
- `GET /api/auth/me` - Get current user information

### Checklists
- `GET /api/checklists` - Get all checklists
- `POST /api/checklists` - Create a new checklist
- `GET /api/checklist/<id>` - Get checklist details with items and members
- `PUT /api/checklist/<id>` - Update checklist name
- `DELETE /api/checklist/<id>` - Delete a checklist
- `POST /api/checklist/<id>/items` - Add an item to a checklist
- `PUT /api/checklist/items/<item_id>` - Update item status or assignment
- `DELETE /api/checklist/items/<item_id>` - Delete an item
- `GET /api/checklist/<id>/progress` - Get checklist progress statistics

### Team Members
- `GET /api/members/<checklist_id>` - Get all members of a checklist
- `POST /api/members/<checklist_id>` - Add a member to a checklist
- `DELETE /api/members/<id>` - Remove a member from a checklist
- `GET /api/members/available` - Get all users that can be added to checklists

### Alerts
- `GET /api/alerts` - Get all alerts for the current user's checklists
- `GET /api/alerts/<checklist_id>` - Get alerts for a specific checklist

## Frontend Integration

The backend is designed to work with the PackPal frontend. Make sure your frontend is configured to send requests to the correct API endpoints.

For local development, the frontend should:
1. Make API requests to `http://localhost:5000`
2. Include the JWT token in the Authorization header: `Authorization: Bearer <token>`
3. Send and receive JSON data

## License

This project is licensed under the MIT License. 