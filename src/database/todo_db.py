import sqlite3
import json
import os

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect('todo_tasks.db')
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        status TEXT,
        importance TEXT,
        created_datetime TEXT,
        last_modified_datetime TEXT,
        is_posted INTEGER DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()

def import_tasks_from_json():
    """Import tasks from the JSON file to SQLite database"""
    if not os.path.exists('todo_tasks.json'):
        print("No tasks JSON file found")
        return
    
    with open('todo_tasks.json', 'r') as f:
        tasks = json.load(f)
    
    conn = sqlite3.connect('todo_tasks.db')
    cursor = conn.cursor()
    
    for task in tasks:
        cursor.execute('''
        INSERT OR REPLACE INTO tasks 
        (id, title, content, status, importance, created_datetime, last_modified_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task['id'],
            task['title'],
            task.get('body', {}).get('content', ''),
            task['status'],
            task['importance'],
            task['createdDateTime'],
            task['lastModifiedDateTime']
        ))
    
    conn.commit()
    conn.close()
    print(f"Imported {len(tasks)} tasks to database")

def get_unposted_tasks(limit=1):
    """Get tasks that haven't been posted yet"""
    conn = sqlite3.connect('todo_tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, title, content FROM tasks 
    WHERE is_posted = 0 AND status = 'completed'
    LIMIT ?
    ''', (limit,))
    
    tasks = cursor.fetchall()
    conn.close()
    
    return tasks

def mark_task_as_posted(task_id):
    """Mark a task as posted"""
    conn = sqlite3.connect('todo_tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE tasks SET is_posted = 1
    WHERE id = ?
    ''', (task_id,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    import_tasks_from_json()
