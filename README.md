# Threads Automation

A simple Python script to post content to Threads using the pythreads package.

## Setup

1. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

2. Configure your Threads credentials in the `.env` file:
   ```
   THREADS_USERNAME=your_threads_username
   THREADS_PASSWORD=your_threads_password
   ```

## Usage

Run the script:
```
python src/post_to_threads.py
```

The script will prompt you to enter a title and optional content for your post.

## Programmatic Usage

You can also import the `post_to_threads` function in your own scripts:

```python
from src.post_to_threads import post_to_threads

# Post to Threads
post_to_threads("Title", "Content")
```
