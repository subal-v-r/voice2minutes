from typing import List, Dict, Any
from app.utils.db import save_action_to_db, get_all_actions as db_get_all_actions

def save_actions_to_db(action_items: List[Dict[str, Any]], meeting_file: str):
    """Save multiple action items to database"""
    for action in action_items:
        save_action_to_db(
            meeting_file=meeting_file,
            action_text=action['text'],
            assignees=action.get('assignees', []),
            deadline=action.get('deadline')
        )

def get_all_actions() -> List[Dict[str, Any]]:
    """Get all actions from database"""
    return db_get_all_actions()

def update_action_status(action_id: int, status: str) -> bool:
    """Update action status"""
    from app.utils.db import mark_action_completed
    if status == 'completed':
        return mark_action_completed(action_id)
    return False

def get_actions_by_meeting(meeting_file: str) -> List[Dict[str, Any]]:
    """Get actions for a specific meeting"""
    all_actions = get_all_actions()
    return [action for action in all_actions if action['meeting_file'] == meeting_file]

def get_overdue_actions() -> List[Dict[str, Any]]:
    """Get actions that are past their deadline"""
    from datetime import datetime
    all_actions = get_all_actions()
    overdue = []
    
    for action in all_actions:
        if action['status'] == 'open' and action['deadline']:
            try:
                deadline = datetime.fromisoformat(action['deadline'])
                if deadline < datetime.now():
                    overdue.append(action)
            except:
                continue
    
    return overdue
