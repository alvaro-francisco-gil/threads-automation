from pythreads import Threads, Credentials
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

def get_threads_credentials():
    """Get Threads credentials from environment variables"""
    return {
        "username": os.getenv("THREADS_USERNAME"),
        "password": os.getenv("THREADS_PASSWORD")
    }

def post_to_threads(title, content=None):
    """Post content to Threads"""
    # Format the content for Threads
    post_text = f"{title}\n\n{content}" if content else title
    
    # Get credentials from env
    creds = get_threads_credentials()
    if not creds["username"] or not creds["password"]:
        print("Threads credentials not found in .env file")
        return False
    
    # Create credentials object
    credentials = Credentials(
        username=creds["username"],
        password=creds["password"]
    )
    
    # Initialize Threads client
    threads = Threads(credentials)
    
    try:
        # Post to Threads
        response = threads.create_post(text=post_text)
        print(f"Posted to Threads: '{title}'")
        return True
    except Exception as e:
        print(f"Error posting to Threads: {e}")
        return False

def main():
    """Main function to demonstrate how to use the script"""
    print("Threads Posting Script")
    print("-" * 30)
    
    # Example usage
    title = input("Enter your post title: ")
    content = input("Enter your post content (optional): ")
    
    post_to_threads(title, content)

if __name__ == "__main__":
    main()
