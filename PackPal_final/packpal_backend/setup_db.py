import pymysql
import os
import time

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Update with your MySQL username
    'password': '',  # Update with your MySQL password
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def setup_database():
    """Set up the database and tables if they don't exist"""
    
    # Connect to MySQL server (without specifying a database)
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        charset=db_config['charset'],
        cursorclass=db_config['cursorclass']
    )
    
    try:
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS packpal_db")
            cursor.execute("USE packpal_db")
            
            # Create users table - use 'name' instead of 'username' to match existing schema
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create checklists table - match existing schema with 'name' and 'created_by'
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_by INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # Create checklist items table - match the existing schema
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'To Pack',
                checklist_id INT NOT NULL,
                assigned_to INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
            )
            """)
            
            # Create alerts table - match existing schema
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type VARCHAR(20) NOT NULL,
                message VARCHAR(255) NOT NULL,
                checklist_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
            )
            """)
            
            # Check if admin user exists
            cursor.execute("SELECT id FROM users WHERE email = 'admin@packpal.com'")
            admin = cursor.fetchone()
            
            # Create admin user if not exists
            if not admin:
                # Password 'admin123' - SHA-256 hash
                password_hash = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
                cursor.execute("""
                INSERT INTO users (name, email, password_hash, role) 
                VALUES ('Admin', 'admin@packpal.com', %s, 'admin')
                """, (password_hash,))
                
                # Get admin user ID
                cursor.execute("SELECT id FROM users WHERE email = 'admin@packpal.com'")
                admin_id = cursor.fetchone()['id']
                
                # Create sample checklist for admin
                cursor.execute("""
                INSERT INTO checklists (name, created_by) 
                VALUES ('Travel Essentials', %s)
                """, (admin_id,))
                
                # Get checklist ID
                cursor.execute("""
                SELECT id FROM checklists 
                WHERE created_by = %s 
                ORDER BY created_at DESC 
                LIMIT 1
                """, (admin_id,))
                checklist_id = cursor.fetchone()['id']
                
                # Add items to checklist
                sample_items = [
                    ('Passport', 'To Pack'),
                    ('Travel Insurance', 'To Pack'),
                    ('Phone Charger', 'To Pack'),
                    ('Toiletries', 'To Pack'),
                    ('Medications', 'To Pack')
                ]
                
                for item, status in sample_items:
                    cursor.execute("""
                    INSERT INTO checklist_items (title, status, checklist_id) 
                    VALUES (%s, %s, %s)
                    """, (item, status, checklist_id))
                
                # Create welcome alert
                cursor.execute("""
                INSERT INTO alerts (type, message, checklist_id) 
                VALUES ('info', 'Welcome to PackPal!', %s)
                """, (checklist_id,))
            
            # Commit changes
            connection.commit()
            
            print("Database setup completed successfully.")
    except Exception as e:
        print(f"Error setting up database: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    # Wait a bit for MySQL to be fully running
    time.sleep(1)
    setup_database() 