import requests
import json
from auth import get_access_token

def test_graph_api():
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Try to get user profile info (simpler API call)
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers=headers
    )
    
    print(f"Test API call status: {response.status_code}")
    print(f"Response: {response.text}")

# Call this function first
test_graph_api()


# In todo_fetcher.py
def get_todo_lists():
    access_token = get_access_token()
    print(f"Token length: {len(access_token)}")
    print(f"Token starts with: {access_token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = "https://graph.microsoft.com/v1.0/me/todo/lists"
    print(f"Making request to: {url}")
    
    response = requests.get(url, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        return response.json()["value"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def get_tasks_from_list(list_id):
    """Get all tasks from a specific list"""
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()["value"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def save_tasks_to_database(tasks):
    """Save tasks to a local JSON file (placeholder for database)"""
    with open('todo_tasks.json', 'w') as f:
        json.dump(tasks, f, indent=4)
    print(f"Saved {len(tasks)} tasks to todo_tasks.json")

if __name__ == "__main__":
    # Get all To Do lists
    todo_lists = get_todo_lists()
    
    if todo_lists:
        print("Your To Do lists:")
        for i, todo_list in enumerate(todo_lists):
            print(f"{i+1}. {todo_list['displayName']} (ID: {todo_list['id']})")
        
        # Ask user which list to fetch
        list_index = int(input("Enter the number of the list to fetch: ")) - 1
        selected_list = todo_lists[list_index]
        
        print(f"Fetching tasks from '{selected_list['displayName']}'...")
        tasks = get_tasks_from_list(selected_list['id'])
        
        if tasks:
            print(f"Found {len(tasks)} tasks")
            save_tasks_to_database(tasks)
