import argparse
import os
import json
import time
from gradio_client import Client

def generate_image(prompt, negative_prompt, output_dir, seed, performance, aspect_ratio, styles):
    try:
        client = Client("http://127.0.0.1:7865/")
    except Exception as e:
        print("Error: Could not connect to Fooocus. Is it running?")
        return

    # Default parameters for Fooocus v2.5.5
    # This list must match the length and order of inputs in webui.py
    # Based on webui.py ctrls list
    args = [
        False, # generate_image_grid
        prompt,
        negative_prompt,
        styles, # style_selections
        performance, # performance_selection
        aspect_ratio, # aspect_ratios_selection
        1, # image_number
        "png", # output_format
        seed, # image_seed
        False, # read_wildcards_in_order
        2.0, # sharpness
        7.0, # guidance_scale
        "juggernautXL_v8Rundiffusion.safetensors", # base_model
        "None", # refiner_model
        0.5, # refiner_switch
        # LoRAs (5 slots: enabled, name, weight)
        True, "sd_xl_offset_example-lora_1.0.safetensors", 0.1,
        False, "None", 1.0,
        False, "None", 1.0,
        False, "None", 1.0,
        False, "None", 1.0,
        False, # input_image_checkbox
        "uov", # current_tab
        "Disabled", # uov_method
        None, # uov_input_image
        [], # outpaint_selections
        None, # inpaint_input_image
        "", # inpaint_additional_prompt
        None, # inpaint_mask_image
        False, # disable_preview
        False, # disable_intermediate_results
        False, # disable_seed_increment
        False, # black_out_nsfw
        1.5, # adm_scaler_positive
        0.8, # adm_scaler_negative
        0.3, # adm_scaler_end
        7.0, # adaptive_cfg
        2, # clip_skip
        "dpmpp_2m_sde_gpu", # sampler_name
        "karras", # scheduler_name
        "Default (none)", # vae_name
        -1, # overwrite_step
        -1, # overwrite_switch
        -1, # overwrite_width
        -1, # overwrite_height
        -1.0, # overwrite_vary_strength
        -1.0, # overwrite_upscale_strength
        False, # mixing_image_prompt_and_vary_upscale
        False, # mixing_image_prompt_and_inpaint
        False, # debugging_cn_preprocessor
        False, # skipping_cn_preprocessor
        64, # canny_low_threshold
        128, # canny_high_threshold
        "joint", # refiner_swap_method
        0.25, # controlnet_softness
        # FreeU
        False, 1.01, 1.02, 0.99, 0.95,
        # Inpaint
        False, False, "v2.6", 1.0, 0.618, False, False, 0,
        # Metadata
        False, # save_final_enhanced_image_only
        True, # save_metadata_to_images
        "fooocus", # metadata_scheme
        # IP CTRLS (7 slots)
        None, 0.5, 0.6, "Image Prompt",
        None, 0.5, 0.6, "Image Prompt",
        None, 0.5, 0.6, "Image Prompt",
        None, 0.5, 0.6, "Image Prompt",
        None, 0.5, 0.6, "Image Prompt",
        None, 0.5, 0.6, "Image Prompt",
        None, 0.5, 0.6, "Image Prompt",
        # Extra
        False, # debugging_dino
        0, # dino_erode_or_dilate
        False, # debugging_enhance_masks_checkbox
        None, # enhance_input_image
        False, # enhance_checkbox
        "Disabled", # enhance_uov_method
        "Before", # enhance_uov_processing_order
        "Original", # enhance_uov_prompt_type
        # Enhance ctrls (lots of them, but we set them to defaults)
    ]
    
    # Add enhance ctrls (16 per tab * 1 tab)
    args += [False, "", "", "", "u2net", "full", "vit_b", 0.25, 0.3, 0, False, "v2.6", 1.0, 0.618, 0, False]

    print(f"Generating image with prompt: {prompt}...")
    
    # fn_index = 32 is common for generate, but we'll try to find it or use api_name
    try:
        # job = client.submit(*args, fn_index=32) # fn_index needs to be correct
        # Using the standard predict which works if indices mismatch but order is okay? 
        # Actually, let's use the explicit indices if possible.
        # For Fooocus v2.5.5, the generate button usually calls fn_index=32
        result = client.predict(*args, fn_index=32)
        
        # result for fn_index=32 is [progress_html, progress_window, progress_gallery, gallery]
        # gallery is a list of [path, caption] or just paths
        gallery = result[-1]
        if gallery and len(gallery) > 0:
            img_info = gallery[0]
            if isinstance(img_info, dict):
                img_path = img_info['name']
            elif isinstance(img_info, list):
                img_path = img_info[0]
            else:
                img_path = img_info
            
            print(f"Success! Image saved at: {img_path}")
            
            # Copy to output_dir if specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                dest = os.path.join(output_dir, os.path.basename(img_path))
                import shutil
                shutil.copy(img_path, dest)
                print(f"Image copied to: {dest}")
        else:
            print("No image was generated. Check Fooocus logs.")
            
    except Exception as e:
        print(f"Error during generation: {e}")
        print("Note: If you get a 'length mismatch', the Fooocus version might have changed its parameters.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fooocus CLI - Generate images from command line")
    parser.add_argument("prompt", type=str, help="Positive prompt")
    parser.add_argument("-n", "--negative", type=str, default="", help="Negative prompt")
    parser.add_argument("-o", "--output", type=str, default="outputs_cli", help="Output directory")
    parser.add_argument("-s", "--seed", type=int, default=-1, help="Seed (-1 for random)")
    parser.add_argument("-p", "--performance", type=str, default="Speed", choices=["Speed", "Quality", "Extreme Speed"], help="Performance mode")
    parser.add_argument("-ar", "--aspect_ratio", type=str, default="1152\u00d7896", help="Aspect ratio (e.g. 1152\u00d7896)")
    parser.add_argument("-st", "--styles", nargs="+", default=["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"], help="Styles to apply")

    args = parser.parse_args()
    
    if args.seed == -1:
        import random
        args.seed = random.randint(0, 2**32 - 1)
        
    generate_image(args.prompt, args.negative, args.output, args.seed, args.performance, args.aspect_ratio, args.styles)
