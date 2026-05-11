from gradio_client import Client
client = Client("http://127.0.0.1:7865/")
info = client.view_api(return_format="dict")
print(info.keys())
if 'named_endpoints' in info:
    print("Named endpoints:", info['named_endpoints'].keys())
