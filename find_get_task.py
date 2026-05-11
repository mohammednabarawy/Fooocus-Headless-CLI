from gradio_client import Client
client = Client("http://127.0.0.1:7865/")
info = client.view_api(return_format="dict")
for endpoint in info['unnamed_endpoints']:
    # Inspecting indices based on observation
    params = endpoint.get('parameters', [])
    returns = endpoint.get('returns', [])
    if len(params) > 100 and len(returns) == 1:
        print(f"Candidate for get_task found! Index: {endpoint['fn_index']}")
        print(f"Parameters: {len(params)}, Returns: {len(returns)}")
        # Verify first few params
        print(f"  Param 0: {params[0].get('label')}")
        print(f"  Param 1: {params[1].get('label')}")
        print(f"  Param 2: {params[2].get('label')}")
