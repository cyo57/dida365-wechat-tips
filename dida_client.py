import httpx
import json
import os
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHORIZATION_URL, TOKEN_URL, API_BASE_URL

class DidaClient:
    def __init__(self, access_token=None):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI
        self.token_cache_file = "data/token_cache"
        
        if access_token:
            self.access_token = access_token
        else:
            self.access_token = self._load_token_from_cache()
            
        self.client = httpx.Client(headers={"Authorization": f"Bearer {self.access_token}"})

    def _save_token_to_cache(self, token_data):
        with open(self.token_cache_file, "w") as f:
            json.dump(token_data, f)
        self.access_token = token_data.get("access_token")
        self.client.headers["Authorization"] = f"Bearer {self.access_token}"

    def _load_token_from_cache(self):
        if os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, "r") as f:
                token_data = json.load(f)
                return token_data.get("access_token")
        return None

    def get_authorization_url(self, state="xyz"):
        """
        Generates the authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "scope": "tasks:read",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        req = httpx.Request("GET", AUTHORIZATION_URL, params=params)
        return str(req.url)

    def get_access_token(self, code: str):
        """
        Exchanges authorization code for an access token.
        """
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "scope": "tasks:read",
            "redirect_uri": self.redirect_uri,
        }
        import base64
        
        # Manually construct Basic Auth header
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            # Use httpx.Client to send the request
            with httpx.Client() as client:
                response = client.post(TOKEN_URL, data=data, headers=headers)
            
            response.raise_for_status()
            token_data = response.json()
            self._save_token_to_cache(token_data)
            print("Access token obtained and cached successfully.")
            return token_data.get("access_token")
        except httpx.HTTPStatusError as e:
            print(f"Error getting access token: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            return None

    def get_projects(self):
        """
        Fetches all projects.
        """
        url = f"{API_BASE_URL}/project"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error getting projects: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            return None

    def get_project_data(self, project_id: str):
        """
        Fetches all data, including undone tasks, for a specific project.
        """
        url = f"{API_BASE_URL}/project/{project_id}/data"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error getting project data for project {project_id}: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            return None
