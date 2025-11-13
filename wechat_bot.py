import httpx
from config import WECHAT_BOT_KEY

class WechatBot:
    def __init__(self):
        if not WECHAT_BOT_KEY:
            raise ValueError("WECHAT_BOT_KEY is not set in the environment variables.")
        self.webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECHAT_BOT_KEY}"
        self.client = httpx.Client()

    def send_markdown(self, content: str):
        """
        Sends a markdown message to the bot.
        """
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        try:
            response = self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print("Message sent successfully to WeChat Bot.")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error sending message to WeChat Bot: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
    def send_text(self, content: str):
        """
        Sends a text message to the bot.
        """
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        try:
            response = self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print("Message sent successfully to WeChat Bot.")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error sending message to WeChat Bot: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            return None
            return None
