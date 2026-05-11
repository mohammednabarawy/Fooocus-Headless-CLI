import sys
import os
root = os.path.join(os.getcwd(), 'Fooocus')
sys.path.append(root)
os.chdir(root)
print(f"CWD: {os.getcwd()}")
try:
    import modules.cli_worker
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
