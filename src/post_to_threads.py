from pythreads import Threads, Credentials
from database.todo_db import get_unposted_tasks, mark_task_as_posted
import json
import os
import time
from dotenv import load_dotenv


load_dotenv()

def get_threads_credentials():
    return {
        "username": os.getenv("THREADS_USERNAME"),
        "password": os.getenv("THREADS_PASSWORD")
    }


def load_credentials():
    """Load Threads credentials from file"""
    if not os.path.exists('threads_credentials.json'):
        print("Threads credentials file not found")
        return None
    
    with open('threads_credentials.json', 'r') as f:
        return json.load(f)

def post_task_to_threads(task):
    """Post a task to Threads"""
    task_id, title, content = task
    
    # Format the content for Threads
    post_text = f"{title}\n\n{content}" if content else title
    
    # Load credentials
    creds_data = load_credentials()
    if not creds_data:
        return False
    
    # Create credentials objectº
    credentials = Credentials(
        username=creds_data['username'],
        password=creds_data['password']
    )
    
    # Initialize Threads client
    threads = Threads(credentials)
    
    try:
        # Post to Threads
        response = threads.create_post(text=post_text)
        print(f"Posted task '{title}' to Threads")
        return True
    except Exception as e:
        print(f"Error posting to Threads: {e}")
        return False

def main():
    # Get unposted tasks
    tasks = get_unposted_tasks(limit=1)
    
    if not tasks:
        print("No unposted tasks found")
        return
    
    for task in tasks:
        success = post_task_to_threads(task)
        if success:
            mark_task_as_posted(task[0])
            print(f"Task {task[1]} marked as posted")

if __name__ == "__main__":
    main()
