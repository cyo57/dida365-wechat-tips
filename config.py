import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WECHAT_BOT_KEY = os.getenv("WECHAT_BOT_KEY")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# API URLs
AUTHORIZATION_URL = "https://dida365.com/oauth/authorize"
TOKEN_URL = "https://dida365.com/oauth/token"
API_BASE_URL = "https://api.dida365.com/open/v1"