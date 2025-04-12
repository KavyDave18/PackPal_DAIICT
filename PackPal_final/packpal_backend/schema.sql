-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS packpal_db;
USE packpal_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Checklists table
CREATE TABLE IF NOT EXISTS checklists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Checklist items table
CREATE TABLE IF NOT EXISTS checklist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'To Pack',
    checklist_id INT NOT NULL,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- Team members table
CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    checklist_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_team_member (checklist_id, user_id)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    message VARCHAR(255) NOT NULL,
    checklist_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
);

-- Sample data for testing
-- Uncomment the following lines to add sample data

-- -- Sample users with different roles
-- INSERT INTO users (name, email, password_hash, role) VALUES 
-- ('John Owner', 'owner@example.com', '$2b$12$QyLK9d8XDaP2e8Tr7NuFxezirRF5XbZMCEzG3Bwx0KR9XAZe1m.bW', 'owner'),  -- password: 'password123'
-- ('Jane Admin', 'admin@example.com', '$2b$12$QyLK9d8XDaP2e8Tr7NuFxezirRF5XbZMCEzG3Bwx0KR9XAZe1m.bW', 'admin'),   -- password: 'password123'
-- ('Bob Member', 'member@example.com', '$2b$12$QyLK9d8XDaP2e8Tr7NuFxezirRF5XbZMCEzG3Bwx0KR9XAZe1m.bW', 'member'),  -- password: 'password123'
-- ('Alice Viewer', 'viewer@example.com', '$2b$12$QyLK9d8XDaP2e8Tr7NuFxezirRF5XbZMCEzG3Bwx0KR9XAZe1m.bW', 'viewer'); -- password: 'password123'

-- -- Sample checklist
-- INSERT INTO checklists (name, created_by) VALUES ('Trip to Paris', 1);

-- -- Sample team members
-- INSERT INTO team_members (checklist_id, user_id) VALUES 
-- (1, 1),  -- Owner is a member
-- (1, 2),  -- Admin is a member
-- (1, 3),  -- Member is a member
-- (1, 4);  -- Viewer is a member

-- -- Sample checklist items
-- INSERT INTO checklist_items (title, checklist_id, status, assigned_to) VALUES 
-- ('Passport', 1, 'Packed', 1),
-- ('Travel Insurance', 1, 'To Pack', 2),
-- ('Camera', 1, 'To Pack', 3),
-- ('Toiletries', 1, 'To Pack', NULL);

-- -- Sample alerts
-- INSERT INTO alerts (type, message, checklist_id) VALUES 
-- ('update', 'John Owner changed Passport status from To Pack to Packed', 1),
-- ('conflict', 'Both John Owner and Jane Admin attempted to mark Travel Insurance as Packed', 1); 