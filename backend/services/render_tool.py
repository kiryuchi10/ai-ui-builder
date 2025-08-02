# backend/services/render_tool.py
import requests
import os

RENDER_API_KEY = os.getenv("RENDER_API_KEY")
RENDER_SERVICE_ID = os.getenv("RENDER_SERVICE_ID")
RENDER_API_URL = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json"
}

def trigger_deployment():
    """
    Trigger a new deployment on Render.
    """
    payload = {"clearCache": True}
    response = requests.post(RENDER_API_URL, headers=headers, json=payload)
    if response.status_code == 201:
        return {"status": "success", "deployment": response.json()}
    else:
        return {"status": "error", "details": response.text}
