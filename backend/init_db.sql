-- PostgreSQL Database Schema for UNIMAK Problem Tracking System

-- Enable UUID extension if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table with role column
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language TEXT DEFAULT 'en',
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

-- Managers table
CREATE TABLE IF NOT EXISTS managers (
    id SERIAL PRIMARY KEY,
    manager_name TEXT NOT NULL UNIQUE,
    manager_mail TEXT
);

-- Engineers table
CREATE TABLE IF NOT EXISTS engineers (
    id SERIAL PRIMARY KEY,
    engineer_name TEXT NOT NULL UNIQUE,
    engineer_mail TEXT
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL UNIQUE,
    customer_country TEXT NOT NULL
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_number TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL UNIQUE,
    manager_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (manager_id) REFERENCES managers(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Groups table
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    engineer_id INTEGER NOT NULL,
    group_name TEXT NOT NULL,
    group_number TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (engineer_id) REFERENCES engineers(id)
);

-- Components table
CREATE TABLE IF NOT EXISTS components (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    position_no TEXT,
    component_no TEXT,
    component_name TEXT,
    unit_quantity INTEGER,
    total_quantity INTEGER,
    weight FLOAT,
    description TEXT,
    size TEXT,
    materials TEXT,
    machine_type TEXT,
    notes TEXT,
    working_area TEXT,
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

-- Problems table
CREATE TABLE IF NOT EXISTS problems (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    planned_closing_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

-- Problem components table
CREATE TABLE IF NOT EXISTS problem_components (
    id SERIAL PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    component_id INTEGER NOT NULL,
    reason TEXT,
    department TEXT,
    action TEXT,
    priority TEXT,
    description TEXT,
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    FOREIGN KEY (component_id) REFERENCES components(id)
);

-- Problem steps table
CREATE TABLE IF NOT EXISTS problem_steps (
    id SERIAL PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    component_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    df_filename TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    planned_closing_date DATE NOT NULL,
    action_after_report TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    FOREIGN KEY (component_id) REFERENCES components(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_problems_user_id ON problems(user_id);
CREATE INDEX IF NOT EXISTS idx_problems_project_id ON problems(project_id);
CREATE INDEX IF NOT EXISTS idx_problems_group_id ON problems(group_id);
CREATE INDEX IF NOT EXISTS idx_problem_components_problem_id ON problem_components(problem_id);
CREATE INDEX IF NOT EXISTS idx_problem_components_component_id ON problem_components(component_id);
CREATE INDEX IF NOT EXISTS idx_problem_steps_problem_id ON problem_steps(problem_id);
CREATE INDEX IF NOT EXISTS idx_problem_steps_component_id ON problem_steps(component_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION!)
-- Password hash for 'admin123' using werkzeug
INSERT INTO users (username, password_hash, role) 
VALUES ('admin', 'pbkdf2:sha256:600000$XxXxXxXxXxXxXxXx$...', 'admin')
ON CONFLICT (username) DO NOTHING;

