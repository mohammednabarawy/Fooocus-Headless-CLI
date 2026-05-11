from gradio_client import Client
client = Client("http://127.0.0.1:7865/")
info = client.view_api(return_format="dict")
for endpoint in info['unnamed_endpoints']:
    for param in endpoint['parameters']:
        if param.get('label') == 'Prompt':
            print(f"Found Prompt in endpoint {endpoint['fn_index']}")
            print(f"Number of parameters: {len(endpoint['parameters'])}")
            if len(endpoint['parameters']) > 30:
                print("THIS IS LIKELY THE ONE!")
                # Save to file
                import json
                with open("endpoint_params.json", "w") as f:
                    json.dump(endpoint, f, indent=4)
