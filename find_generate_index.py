from gradio_client import Client
import json

client = Client("http://127.0.0.1:7865/")
info = client.view_api(return_format="dict")
# Look for predictable labels
for endpoint in info['endpoints']:
    for param in endpoint['parameters']:
        if param['label'] == 'Prompt':
            print(f"Generate Endpoint found! Index: {endpoint['fn_index']}")
            print(f"Parameters: {len(endpoint['parameters'])}")
            # Save the parameters schema
            with open("generate_params.json", "w") as f:
                json.dump(endpoint['parameters'], f, indent=4)
            break
