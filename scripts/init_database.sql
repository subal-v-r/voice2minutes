-- Initialize Meeting Tracker Database
-- This script creates all necessary tables and indexes

-- Drop existing tables if they exist (for fresh start)
DROP TABLE IF EXISTS action_history;
DROP TABLE IF EXISTS participants;
DROP TABLE IF EXISTS actions;
DROP TABLE IF EXISTS meetings;

-- Create meetings table
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    title TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration REAL DEFAULT 0.0,
    participants TEXT,
    summary TEXT,
    agenda_items TEXT,
    decisions TEXT,
    risks TEXT,
    next_steps TEXT,
    transcript_path TEXT,
    audio_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create actions table
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_file TEXT NOT NULL,
    meeting_id INTEGER,
    action_text TEXT NOT NULL,
    assignees TEXT,
    deadline TEXT,
    deadline_urgency TEXT DEFAULT 'low',
    status TEXT DEFAULT 'open',
    confidence REAL DEFAULT 0.0,
    speaker TEXT,
    start_time REAL DEFAULT 0.0,
    end_time REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (meeting_id) REFERENCES meetings (id) ON DELETE CASCADE
);

-- Create participants table
CREATE TABLE participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    speaker_name TEXT NOT NULL,
    speaking_time REAL DEFAULT 0.0,
    FOREIGN KEY (meeting_id) REFERENCES meetings (id) ON DELETE CASCADE
);

-- Create action history table
CREATE TABLE action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT,
    changed_by TEXT,
    change_reason TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (action_id) REFERENCES actions (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_actions_meeting_file ON actions(meeting_file);
CREATE INDEX idx_actions_status ON actions(status);
CREATE INDEX idx_actions_deadline ON actions(deadline);
CREATE INDEX idx_actions_urgency ON actions(deadline_urgency);
CREATE INDEX idx_meetings_date ON meetings(date);
CREATE INDEX idx_meetings_filename ON meetings(filename);
CREATE INDEX idx_participants_meeting ON participants(meeting_id);
CREATE INDEX idx_history_action ON action_history(action_id);

-- Insert sample data for testing
INSERT INTO meetings (filename, title, participants, summary, duration) VALUES
('sample_meeting_1.mp3', 'Weekly Team Standup', 'John Doe,Jane Smith,Bob Johnson', 'Discussed project progress and upcoming deadlines', 1800),
('sample_meeting_2.mp3', 'Product Planning Session', 'Alice Brown,Charlie Wilson,David Lee', 'Planned features for next quarter release', 3600);

-- Insert sample actions
INSERT INTO actions (meeting_file, meeting_id, action_text, assignees, deadline, deadline_urgency, status, confidence, speaker) VALUES
('sample_meeting_1.mp3', 1, 'John will send the updated project timeline by Friday', 'John Doe', '2024-01-19T17:00:00', 'medium', 'open', 0.85, 'Jane Smith'),
('sample_meeting_1.mp3', 1, 'Jane needs to review the code changes before deployment', 'Jane Smith', '2024-01-18T12:00:00', 'high', 'open', 0.92, 'John Doe'),
('sample_meeting_2.mp3', 2, 'Alice will prepare the feature specifications document', 'Alice Brown', '2024-01-25T17:00:00', 'low', 'open', 0.78, 'Charlie Wilson');
