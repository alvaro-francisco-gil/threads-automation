import requests

def get_todo_lists(access_token):
    url = "https://graph.microsoft.com/v1.0/me/todo/lists"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def get_tasks_from_list(access_token, list_id):
    url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()
