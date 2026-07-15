-- Medical RAG System - MySQL Database Initialization Script
-- This script is executed automatically when the MySQL container starts

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS medical_rag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE medical_rag;

-- ============================================
-- Patients Table
-- ============================================
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    age INT,
    birth_date DATE,
    phone VARCHAR(20),
    address TEXT,
    id_card VARCHAR(18),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Medical Records Table
-- ============================================
CREATE TABLE IF NOT EXISTS medical_records (
    record_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    record_type VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    doctor VARCHAR(100),
    visit_time DATETIME NOT NULL,
    admission_time DATETIME,
    discharge_time DATETIME,
    content TEXT,
    diagnosis TEXT,
    medications JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_visit_time (visit_time),
    INDEX idx_department (department),
    FULLTEXT INDEX ft_content (content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Summaries Table
-- ============================================
CREATE TABLE IF NOT EXISTS summaries (
    summary_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    summary_type ENUM('transfer', 'discharge', 'admission', 'progress') NOT NULL,
    sections JSON NOT NULL,
    entities JSON,
    generated_by VARCHAR(100),
    model_used VARCHAR(100),
    processing_time_ms INT,
    status ENUM('draft', 'completed', 'reviewed') DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_summary_type (summary_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Query Logs Table
-- ============================================
CREATE TABLE IF NOT EXISTS query_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    query TEXT NOT NULL,
    query_type VARCHAR(50),
    patient_id VARCHAR(50),
    result_count INT,
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Users Table (for authentication)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor', 'nurse', 'researcher') DEFAULT 'doctor',
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Insert Default Data
-- ============================================

-- Insert default admin user (password: admin123)
INSERT INTO users (user_id, username, password_hash, role) VALUES
    ('U00001', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND0.RfpOxGi', 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- Insert sample patients
INSERT INTO patients (patient_id, name, gender, age, phone) VALUES
    ('P00001', '张三', 'Male', 45, '13800138001'),
    ('P00002', '李四', 'Female', 52, '13800138002'),
    ('P00003', '王五', 'Male', 38, '13800138003')
ON DUPLICATE KEY UPDATE patient_id=patient_id;

-- Grant permissions to rag_user
GRANT ALL PRIVILEGES ON medical_rag.* TO 'rag_user'@'%';
FLUSH PRIVILEGES;

-- Create view for patient summary
CREATE OR REPLACE VIEW v_patient_summary AS
SELECT 
    p.patient_id,
    p.name,
    p.gender,
    p.age,
    COUNT(DISTINCT mr.record_id) as total_records,
    MAX(mr.visit_time) as last_visit
FROM patients p
LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
GROUP BY p.patient_id, p.name, p.gender, p.age;

COMMIT;
