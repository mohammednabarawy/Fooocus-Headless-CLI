from gradio_client import Client
client = Client("http://127.0.0.1:7865/")
info = client.view_api(return_format="dict")
max_params = 0
best_index = -1
for endpoint in info['endpoints']:
    num_params = len(endpoint['parameters'])
    if num_params > max_params:
        max_params = num_params
        best_index = endpoint['fn_index']

print(f"Max params: {max_params}, Index: {best_index}")
# Print labels for this endpoint
for endpoint in info['endpoints']:
    if endpoint['fn_index'] == best_index:
        for p in endpoint['parameters']:
             print(f"  - {p['label']}: {p['type']}")
