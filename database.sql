
-- Job Application Tracker database setup
-- Creates the database and required tables.
-- Does not include passwords or personal application records.

CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

-- Table 1: Job applications
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    job_link VARCHAR(500),
    application_date DATE NOT NULL,
    status ENUM(
        'Applied',
        'Assessment',
        'Interview',
        'Offer',
        'Rejected',
        'Withdrawn'
    ) DEFAULT 'Applied',
    deadline DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- Table 2: Skill matching analysis history
CREATE TABLE IF NOT EXISTS skill_match_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NULL,
    skills_input TEXT NOT NULL,
    job_description TEXT NOT NULL,
    matched_skills TEXT,
    missing_skills TEXT,
    skill_coverage DECIMAL(5,2) NOT NULL,
    text_similarity DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_skill_match_application_id (application_id),

    CONSTRAINT fk_skill_match_application
        FOREIGN KEY (application_id)
        REFERENCES applications(id)
        ON DELETE SET NULL
);
