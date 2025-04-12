-- PackPal Database Schema

-- Drop database if it exists and create a new one
DROP DATABASE IF EXISTS packpal_db;
CREATE DATABASE packpal_db;
USE packpal_db;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Checklists table
CREATE TABLE checklists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    creator_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Checklist items table
CREATE TABLE checklist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text VARCHAR(100) NOT NULL,
    checked BOOLEAN DEFAULT FALSE,
    checklist_id INT NOT NULL,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- Alerts table
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    user_id INT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create a sample admin user with password 'admin123'
-- Password hash is SHA-256 of 'admin123'
INSERT INTO users (username, email, password_hash, role) 
VALUES ('Admin', 'admin@packpal.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin');

-- Insert sample data (only if you want to pre-populate the database)
INSERT INTO checklists (title, creator_id) VALUES ('Travel Essentials', 1);

-- Add items to the sample checklist
INSERT INTO checklist_items (text, checked, checklist_id) VALUES 
('Passport', FALSE, 1),
('Travel Insurance', FALSE, 1),
('Phone Charger', FALSE, 1),
('Toiletries', FALSE, 1),
('Medications', FALSE, 1);

-- Create a welcome alert
INSERT INTO alerts (message, user_id) VALUES ('Welcome to PackPal!', 1); 