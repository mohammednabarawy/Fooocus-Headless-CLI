from gradio_client import Client
import sys

client = Client("http://127.0.0.1:7865/")
for i, endpoint in enumerate(client.endpoints):
    # Search for the one that takes the most parameters or has a specific signature
    if len(endpoint.parameters) > 20:
        print(f"Endpoint {i}: {len(endpoint.parameters)} parameters")
        for p in endpoint.parameters:
             print(f"  - {p['label']}: {p['type']}")
