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

    def get_inbox_data(self):
        """
        Fetches all tasks from the inbox (no project assigned).
        In滴答清单, inbox tasks might be under project with id 'inbox' or special endpoint.
        """
        # 尝试不同的收集箱获取方式
        possible_inbox_ids = ['inbox', '0', 'default', '']

        for inbox_id in possible_inbox_ids:
            try:
                # 方法1: 作为特殊项目获取
                url = f"{API_BASE_URL}/project/{inbox_id}/data"
                response = self.client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data and 'tasks' in data:
                        print(f"  ✓ 找到收集箱 (ID: {inbox_id}), 任务数: {len(data['tasks'])}")
                        return data

                # 方法2: 使用collect接口（如果存在）
                url2 = f"{API_BASE_URL}/project/collect/data"
                response2 = self.client.get(url2)
                if response2.status_code == 200:
                    data = response2.json()
                    if data and 'tasks' in data:
                        print(f"  ✓ 找到收集箱 (collect接口), 任务数: {len(data['tasks'])}")
                        return data

            except httpx.HTTPStatusError:
                continue

        # 方法3: 直接获取所有任务并筛选无项目的任务
        try:
            all_tasks = []
            for project in self.get_projects() or []:
                project_data = self.get_project_data(project['id'])
                if project_data and 'tasks' in project_data:
                    all_tasks.extend(project_data['tasks'])

            # 收集箱任务：没有assignee或特定标记的任务
            inbox_tasks = [task for task in all_tasks if task.get('projectId') == 'inbox' or task.get('inbox', False)]

            if inbox_tasks:
                print(f"  ✓ 筛选找到收集箱任务: {len(inbox_tasks)} 条")
                return {'tasks': inbox_tasks}

        except Exception as e:
            print(f"  ✗ 筛选收集箱任务失败: {e}")

        return None
