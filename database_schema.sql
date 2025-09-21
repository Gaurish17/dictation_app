-- Database Schema for Dictation & Typing Practice Application
-- This shows the complete database structure

-- Users table - stores all user accounts (admin, superuser, students)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,  -- SHA256 hashed
    role VARCHAR(20) NOT NULL,       -- 'admin', 'superuser', 'student'
    subscription_start DATE,
    subscription_end DATE,
    device_id VARCHAR(200),          -- For device restriction
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dictation content table - stores audio files and their text
CREATE TABLE dictation_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    audio_file VARCHAR(200) NOT NULL,    -- Path to audio file
    content_text TEXT NOT NULL,          -- Expected text for dictation
    difficulty_level VARCHAR(50),       -- 'beginner', 'intermediate', 'advanced'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Typing passages table - stores text passages for typing practice
CREATE TABLE typing_passages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    passage TEXT NOT NULL,              -- The text to be typed
    difficulty_level VARCHAR(50),       -- 'beginner', 'intermediate', 'advanced'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dictation attempts table - tracks student dictation practice attempts
CREATE TABLE dictation_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    dictation_content_id INTEGER NOT NULL,
    typed_text TEXT,                     -- What the student typed
    accuracy REAL,                       -- Accuracy percentage (0-100)
    time_taken INTEGER,                  -- Time in seconds
    wpm REAL,                           -- Words per minute
    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (dictation_content_id) REFERENCES dictation_content (id)
);

-- Typing attempts table - tracks student typing practice attempts
CREATE TABLE typing_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    typing_passage_id INTEGER NOT NULL,
    typed_text TEXT,                     -- What the student typed
    accuracy REAL,                       -- Accuracy percentage (0-100)
    time_taken INTEGER,                  -- Time in seconds
    wpm REAL,                           -- Words per minute
    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (typing_passage_id) REFERENCES typing_passages (id)
);

-- Indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_dictation_attempts_user_id ON dictation_attempts(user_id);
CREATE INDEX idx_dictation_attempts_date ON dictation_attempts(attempt_date);
CREATE INDEX idx_typing_attempts_user_id ON typing_attempts(user_id);
CREATE INDEX idx_typing_attempts_date ON typing_attempts(attempt_date);

-- Initial admin users (these are created when the app first runs)
INSERT OR IGNORE INTO users (username, password, role, subscription_start, subscription_end) VALUES
('admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'admin', '2024-01-01', '2030-12-31'),
('superuser', 'ac7e72c8e6b6e7b4ed1c2b9d8c4b8c7a6d5c4e3b2a9f8e7d6c5b4a3f2e1d0c9b8', 'superuser', '2024-01-01', '2030-12-31'),
('student1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'student', '2024-01-01', '2025-12-31'),
('student2', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'student', '2024-01-01', '2025-12-31'),
('student3', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'student', '2024-01-01', '2025-12-31');

-- Sample dictation content (optional)
INSERT OR IGNORE INTO dictation_content (title, audio_file, content_text, difficulty_level) VALUES
('Sample Dictation 1', 'sample1.mp3', 'The quick brown fox jumps over the lazy dog.', 'beginner'),
('Sample Dictation 2', 'sample2.mp3', 'Technology has revolutionized the way we communicate and learn.', 'intermediate');

-- Sample typing passages (optional)
INSERT OR IGNORE INTO typing_passages (title, passage, difficulty_level) VALUES
('Basic Typing 1', 'The quick brown fox jumps over the lazy dog. This sentence contains all letters of the alphabet.', 'beginner'),
('Intermediate Text', 'In today''s digital world, typing skills are essential for productivity and communication. Practice makes perfect.', 'intermediate'),
('Advanced Passage', 'The technological advancement in artificial intelligence has transformed various industries, creating new opportunities while challenging traditional methodologies.', 'advanced');
