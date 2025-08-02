# backend/services/figma_tool.py
import requests
import os

FIGMA_API_URL = "https://api.figma.com/v1"
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
FIGMA_FILE_KEY = os.getenv("FIGMA_FILE_KEY")  # Your Figma project file

headers = {
    "Authorization": f"Bearer {FIGMA_TOKEN}",
    "Content-Type": "application/json"
}

def create_frame(name: str, width=1440, height=1024):
    """
    Create a new frame in Figma based on user prompt.
    """
    url = f"{FIGMA_API_URL}/files/{FIGMA_FILE_KEY}/nodes"
    data = {
        "name": name,
        "width": width,
        "height": height
    }
    # Figma API for creating nodes is limited; usually, you'd use plugins or MCP
    # For now, just a mock response
    return {"status": "success", "frame": data}

def export_layout_json():
    """
    Export Figma file as JSON to process design data.
    """
    url = f"{FIGMA_API_URL}/files/{FIGMA_FILE_KEY}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error exporting layout: {response.status_code}")
