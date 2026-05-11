from gradio_client import Client
import json
import sys

try:
    client = Client("http://127.0.0.1:7865/")
    info = client.view_api(return_format="json")
    with open("api_info.json", "w") as f:
        json.dump(info, f, indent=4)
    print("API info saved to api_info.json")
except Exception as e:
    print(f"Error: {e}")
    print("Is Fooocus running?")
