import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

DB_PATH = "meeting_tracker.db"

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize SQLite database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create actions table with enhanced fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
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
            start_time REAL,
            end_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            notes TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings (id)
        )
    ''')
    
    # Create meetings table with enhanced metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            title TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration REAL,
            participants TEXT,
            summary TEXT,
            agenda_items TEXT,
            decisions TEXT,
            risks TEXT,
            next_steps TEXT,
            transcript_path TEXT,
            audio_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create participants table for better normalization
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            speaker_name TEXT NOT NULL,
            speaking_time REAL DEFAULT 0.0,
            FOREIGN KEY (meeting_id) REFERENCES meetings (id)
        )
    ''')
    
    # Create action_history table for tracking changes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_id INTEGER,
            old_status TEXT,
            new_status TEXT,
            changed_by TEXT,
            change_reason TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (action_id) REFERENCES actions (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_meeting_file ON actions(meeting_file)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_deadline ON actions(deadline)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date)')
    
    conn.commit()
    conn.close()

def save_meeting_to_db(filename: str, title: str, participants: List[str], 
                      summary: Dict[str, Any], duration: float = 0.0,
                      transcript_path: str = None, audio_path: str = None) -> int:
    """Save meeting metadata to database and return meeting ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert summary components to JSON strings
    agenda_items = json.dumps(summary.get('agenda_items', []))
    decisions = json.dumps(summary.get('decisions', []))
    risks = json.dumps(summary.get('risks', []))
    next_steps = json.dumps(summary.get('next_steps', []))
    executive_summary = summary.get('executive_summary', '')
    
    cursor.execute('''
        INSERT INTO meetings (filename, title, participants, summary, duration,
                            agenda_items, decisions, risks, next_steps,
                            transcript_path, audio_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (filename, title, ','.join(participants), executive_summary, duration,
          agenda_items, decisions, risks, next_steps, transcript_path, audio_path))
    
    meeting_id = cursor.lastrowid
    
    # Save individual participants
    for participant in participants:
        cursor.execute('''
            INSERT INTO participants (meeting_id, speaker_name)
            VALUES (?, ?)
        ''', (meeting_id, participant))
    
    conn.commit()
    conn.close()
    
    return meeting_id

def save_action_to_db(meeting_file: str, action_text: str, assignees: List[str], 
                     deadline: str = None, deadline_urgency: str = 'low',
                     confidence: float = 0.0, speaker: str = None,
                     start_time: float = 0.0, end_time: float = 0.0,
                     meeting_id: int = None) -> int:
    """Save individual action to database and return action ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO actions (meeting_file, meeting_id, action_text, assignees, 
                           deadline, deadline_urgency, confidence, speaker,
                           start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (meeting_file, meeting_id, action_text, ','.join(assignees) if assignees else '', 
          deadline, deadline_urgency, confidence, speaker, start_time, end_time))
    
    action_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return action_id

def get_all_actions(status_filter: str = None, urgency_filter: str = None) -> List[Dict[str, Any]]:
    """Get all actions from database with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT a.*, m.title as meeting_title, m.date as meeting_date
        FROM actions a
        LEFT JOIN meetings m ON a.meeting_id = m.id
        WHERE 1=1
    '''
    params = []
    
    if status_filter:
        query += ' AND a.status = ?'
        params.append(status_filter)
    
    if urgency_filter:
        query += ' AND a.deadline_urgency = ?'
        params.append(urgency_filter)
    
    query += ' ORDER BY a.created_at DESC'
    
    cursor.execute(query, params)
    
    actions = []
    for row in cursor.fetchall():
        actions.append({
            'id': row['id'],
            'meeting_file': row['meeting_file'],
            'meeting_id': row['meeting_id'],
            'meeting_title': row['meeting_title'],
            'meeting_date': row['meeting_date'],
            'action_text': row['action_text'],
            'assignees': row['assignees'].split(',') if row['assignees'] else [],
            'deadline': row['deadline'],
            'deadline_urgency': row['deadline_urgency'],
            'status': row['status'],
            'confidence': row['confidence'],
            'speaker': row['speaker'],
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'created_at': row['created_at'],
            'completed_at': row['completed_at'],
            'notes': row['notes']
        })
    
    conn.close()
    return actions

def mark_action_completed(action_id: int, completed_by: str = None, notes: str = None) -> bool:
    """Mark an action as completed with history tracking"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current status
    cursor.execute('SELECT status FROM actions WHERE id = ?', (action_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    old_status = row['status']
    
    # Update action
    cursor.execute('''
        UPDATE actions 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP, notes = ?
        WHERE id = ?
    ''', (notes, action_id))
    
    # Add to history
    cursor.execute('''
        INSERT INTO action_history (action_id, old_status, new_status, changed_by, change_reason)
        VALUES (?, ?, 'completed', ?, ?)
    ''', (action_id, old_status, completed_by, 'Marked as completed'))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def update_action_status(action_id: int, new_status: str, changed_by: str = None, 
                        reason: str = None) -> bool:
    """Update action status with history tracking"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current status
    cursor.execute('SELECT status FROM actions WHERE id = ?', (action_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    old_status = row['status']
    
    # Update action
    cursor.execute('UPDATE actions SET status = ? WHERE id = ?', (new_status, action_id))
    
    # Add to history
    cursor.execute('''
        INSERT INTO action_history (action_id, old_status, new_status, changed_by, change_reason)
        VALUES (?, ?, ?, ?, ?)
    ''', (action_id, old_status, new_status, changed_by, reason))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_meeting_by_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Get meeting details by filename"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM meetings WHERE filename = ?', (filename,))
    row = cursor.fetchone()
    
    if row:
        meeting = dict(row)
        # Parse JSON fields
        meeting['agenda_items'] = json.loads(meeting['agenda_items']) if meeting['agenda_items'] else []
        meeting['decisions'] = json.loads(meeting['decisions']) if meeting['decisions'] else []
        meeting['risks'] = json.loads(meeting['risks']) if meeting['risks'] else []
        meeting['next_steps'] = json.loads(meeting['next_steps']) if meeting['next_steps'] else []
        meeting['participants'] = meeting['participants'].split(',') if meeting['participants'] else []
        
        conn.close()
        return meeting
    
    conn.close()
    return None

def get_actions_by_meeting(meeting_file: str) -> List[Dict[str, Any]]:
    """Get actions for a specific meeting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM actions 
        WHERE meeting_file = ? 
        ORDER BY start_time ASC
    ''', (meeting_file,))
    
    actions = []
    for row in cursor.fetchall():
        actions.append(dict(row))
    
    conn.close()
    return actions

def get_overdue_actions() -> List[Dict[str, Any]]:
    """Get actions that are past their deadline"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, m.title as meeting_title
        FROM actions a
        LEFT JOIN meetings m ON a.meeting_id = m.id
        WHERE a.status = 'open' 
        AND a.deadline IS NOT NULL 
        AND datetime(a.deadline) < datetime('now')
        ORDER BY a.deadline ASC
    ''', )
    
    actions = []
    for row in cursor.fetchall():
        action = dict(row)
        action['assignees'] = action['assignees'].split(',') if action['assignees'] else []
        actions.append(action)
    
    conn.close()
    return actions

def get_action_statistics() -> Dict[str, Any]:
    """Get statistics about actions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total actions
    cursor.execute('SELECT COUNT(*) as total FROM actions')
    stats['total_actions'] = cursor.fetchone()['total']
    
    # Actions by status
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM actions 
        GROUP BY status
    ''')
    stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # Actions by urgency
    cursor.execute('''
        SELECT deadline_urgency, COUNT(*) as count 
        FROM actions 
        WHERE status = 'open'
        GROUP BY deadline_urgency
    ''')
    stats['by_urgency'] = {row['deadline_urgency']: row['count'] for row in cursor.fetchall()}
    
    # Overdue actions
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM actions 
        WHERE status = 'open' 
        AND deadline IS NOT NULL 
        AND datetime(deadline) < datetime('now')
    ''')
    stats['overdue_count'] = cursor.fetchone()['count']
    
    # Recent meetings
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM meetings 
        WHERE date >= datetime('now', '-7 days')
    ''')
    stats['recent_meetings'] = cursor.fetchone()['count']
    
    conn.close()
    return stats

def cleanup_old_data(days_old: int = 90):
    """Clean up old completed actions and meetings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete old completed actions
    cursor.execute('''
        DELETE FROM actions 
        WHERE status = 'completed' 
        AND completed_at < datetime('now', '-{} days')
    '''.format(days_old))
    
    deleted_actions = cursor.rowcount
    
    # Delete old action history
    cursor.execute('''
        DELETE FROM action_history 
        WHERE changed_at < datetime('now', '-{} days')
    '''.format(days_old))
    
    deleted_history = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {
        'deleted_actions': deleted_actions,
        'deleted_history': deleted_history
    }
