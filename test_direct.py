import os
import sys

# Add Fooocus to path
fooocus_path = os.path.abspath(os.path.join(os.getcwd(), "Fooocus"))
os.chdir(fooocus_path)
sys.path.append(fooocus_path)

print("Importing modules...")
import modules.config
import modules.default_pipeline as pipeline
print("Modules imported.")

print("Calling refresh_everything manually...")
pipeline.refresh_everything(
    refiner_model_name="None",
    base_model_name="juggernautXL_v8Rundiffusion.safetensors",
    loras=[],
    vae_name="Default (none)"
)
print("Refresh done.")
