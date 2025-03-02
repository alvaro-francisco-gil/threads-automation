import msal
import webbrowser
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

load_dotenv()

# Get credentials from .env
client_id = os.getenv("CLIENT_ID")
tenant_id = os.getenv("TENANT_ID")
client_secret = os.getenv("CLIENT_SECRET")


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if 'code=' in self.path:
            query = urlparse(self.path).query
            params = parse_qs(query)
            self.server.auth_code = params['code'][0]
            self.wfile.write(b'Authentication successful! You can close this window.')
        else:
            self.wfile.write(b'Authentication failed!')
    
    def log_message(self, format, *args):
        # Suppress log messages
        return

def get_access_token():
    # Create a serializable token cache
    cache = msal.SerializableTokenCache()
    
    # Check if token cache exists and load it
    if os.path.exists('token_cache.json'):
        with open('token_cache.json', 'r') as f:
            cache_data = f.read()
            if cache_data:
                cache.deserialize(cache_data)
    
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
        token_cache=cache
    )
    
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result:
            # Save updated token cache
            with open('token_cache.json', 'w') as f:
                f.write(cache.serialize())
            return result['access_token']
    
    # If no valid token in cache, get a new one
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
        token_cache=cache
    )

    # Start local server to receive redirect
    server = HTTPServer(('localhost', 8000), AuthHandler)
    server.auth_code = None
    
    # Generate auth URL and open browser
    auth_url = app.get_authorization_request_url(
        scopes,
        redirect_uri="http://localhost:8000/callback"
    )
    webbrowser.open(auth_url)
    
    # Wait for the callback
    while server.auth_code is None:
        server.handle_request()
    
    # Exchange code for token
    result = app.acquire_token_by_authorization_code(
        server.auth_code,
        scopes=scopes,
        redirect_uri="http://localhost:8000/callback"
    )
    
    # Check for errors before trying to access the token
    if "error" in result:
        print(f"Error: {result.get('error')}")
        print(f"Description: {result.get('error_description')}")
        print("Correlation ID: %s" % result.get("correlation_id"))
        return None
    elif "access_token" in result:
        # Save token cache
        with open('token_cache.json', 'w') as f:
            f.write(cache.serialize())
        return result['access_token']
    else:
        print("No error reported but access_token is missing from the response")
        return None

scopes = ["Tasks.Read", "Tasks.ReadWrite"]

if __name__ == "__main__":
    token = get_access_token()
    print(f"Access token: {token}")
