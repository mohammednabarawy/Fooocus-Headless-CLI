"""
Fooocus Headless CLI - Direct image generation without Gradio/Web UI.

This script bypasses Fooocus's web server and calls the internal pipeline
directly to generate images from the command line.

Usage:
    python fooocus_cli_direct.py --prompt "a cat on a mountain"
    python fooocus_cli_direct.py --prompt "landscape" --seed 42 --image-number 2
"""

import os
import sys
import argparse
import random
import traceback
import time

# ============================================================
# PATH BOOTSTRAP - Must happen before any Fooocus imports
# ============================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FOOOCUS_ROOT = os.path.join(PROJECT_ROOT, "Fooocus")

if FOOOCUS_ROOT not in sys.path:
    sys.path.insert(0, FOOOCUS_ROOT)

os.chdir(FOOOCUS_ROOT)

# Suppress Gradio-related env warnings
os.environ.setdefault("GRADIO_SERVER_PORT", "7865")

# ============================================================
# MOCK GRADIO - Fooocus expects shared.gradio_root to exist
# ============================================================
import shared

class MockGradio:
    """Minimal mock to satisfy shared.gradio_root references."""
    def __init__(self):
        self.local_url = "headless"
        self.server_name = "localhost"
        self.server_port = "0"
        self.share = False

shared.gradio_root = MockGradio()

# ============================================================
# PARSE ARGS FIRST (before Fooocus imports and hijacks sys.argv)
# ============================================================
def get_args():
    parser = argparse.ArgumentParser(
        description="Fooocus Headless CLI - Generate images without the web UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --prompt "a beautiful sunset over mountains"
  %(prog)s --prompt "portrait" --base-model realisticVisionV60B1_v51VAE.safetensors
  %(prog)s --prompt "abstract art" --seed 42 --image-number 4 --performance Quality
  %(prog)s --prompt "cat" --aspect-ratio 1024x1024 --styles "Fooocus V2" "Fooocus Enhance"
  %(prog)s --prompt "mech" --lora "add_detail:0.8" --lora "epi_noiseoffset2:0.5"
        """
    )
    parser.add_argument("--prompt", required=True, help="Positive prompt for image generation")
    parser.add_argument("--negative-prompt", default="", help="Negative prompt (things to avoid)")
    parser.add_argument("--output", default="outputs", help="Output directory (relative to project root)")
    parser.add_argument("--seed", type=int, default=-1, help="Random seed (-1 for random)")
    parser.add_argument("--performance", default="Speed",
                        choices=["Speed", "Quality", "Extreme Speed"],
                        help="Performance preset (affects step count)")
    parser.add_argument("--aspect-ratio", default="1152×896",
                        help="Image dimensions as WIDTHxHEIGHT (e.g., 1024x1024, 1152×896)")
    parser.add_argument("--styles", nargs="+", default=["Fooocus V2"],
                        help="Style presets to apply")
    parser.add_argument("--base-model", default=None,
                        help="Base model filename (default: from config)")
    parser.add_argument("--refiner-model", default="None",
                        help="Refiner model filename ('None' to disable)")
    parser.add_argument("--refiner-switch", type=float, default=0.5,
                        help="When to switch to refiner (0.0-1.0)")
    parser.add_argument("--cfg-scale", type=float, default=7.0,
                        help="Classifier-Free Guidance scale")
    parser.add_argument("--sharpness", type=float, default=2.0,
                        help="Output sharpness (Fooocus-specific)")
    parser.add_argument("--image-number", type=int, default=1,
                        help="Number of images to generate")
    parser.add_argument("--sampler", default="dpmpp_2m_sde_gpu",
                        help="Sampler algorithm name")
    parser.add_argument("--scheduler", default="karras",
                        help="Noise scheduler name")
    parser.add_argument("--lora", action="append",
                        help="LoRA in format 'filename:weight' (repeatable)")
    parser.add_argument("--vae", default="Default (model)",
                        help="VAE model name")
    parser.add_argument("--disable-preview", action="store_true", default=True,
                        help="Disable preview generation (default: True for CLI)")
    parser.add_argument("--output-format", default="png", choices=["png", "jpg", "webp"],
                        help="Output image format")
    parser.add_argument("--cn-cpds", default=None,
                        help="Path to reference image for CPDS ControlNet (great for text/structure)")
    parser.add_argument("--cn-cpds-weight", type=float, default=0.7,
                        help="Weight for CPDS ControlNet (default: 0.7)")
    parser.add_argument("--cn-cpds-stop", type=float, default=0.75,
                        help="Stop step (0.0 to 1.0) for CPDS ControlNet (default: 0.75)")
    # img2img / Vary mode - used for text harmonization
    parser.add_argument("--input-image", default=None,
                        help="Input image for img2img mode (e.g., composited text image to harmonize)")
    parser.add_argument("--vary-strength", type=float, default=0.4,
                        help="Denoise strength for img2img (0.0=no change, 1.0=full regenerate. 0.3-0.5 for harmonization)")
    return parser.parse_known_args()

# Parse our custom args and strip them from sys.argv before Fooocus imports
cli_args, remaining_argv = get_args()
sys.argv = [sys.argv[0]] + remaining_argv

# ============================================================
# IMPORT FOOOCUS INTERNALS
# ============================================================
try:
    import modules.config
    import modules.core as core
    import modules.default_pipeline as pipeline
    import modules.flags as flags
    import modules.util as util
    import modules.patch as patch_module
    from modules.patch import PatchSettings, patch_settings, patch_all
    import ldm_patched.modules.model_management as model_management
    from modules.sdxl_styles import apply_style
    
    import cv2
    import extras.preprocessors as preprocessors
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import Fooocus modules: {e}")
    traceback.print_exc()
    sys.exit(1)


def parse_aspect_ratio(ar_string):
    """Parse aspect ratio string like '1152×896' or '1024x1024' into (width, height)."""
    for sep in ["×", "x", "X", "*"]:
        if sep in ar_string:
            try:
                w, h = map(int, ar_string.split(sep))
                return w, h
            except ValueError:
                pass
    print(f"[WARNING] Could not parse aspect ratio '{ar_string}', using 1152x896")
    return 1152, 896


def init_patch_settings(sharpness=2.0, adm_scaler_end=0.3,
                        adm_scaler_positive=1.5, adm_scaler_negative=0.8,
                        controlnet_softness=0.25, adaptive_cfg=7.0):
    """
    Initialize patch_settings for the current PID.
    
    This is CRITICAL - modules/patch.py uses patch_settings[os.getpid()]
    during the entire diffusion process. Without this, every diffusion
    step throws a KeyError(pid) which manifests as 'FATAL ERROR: <pid>'.
    """
    pid = os.getpid()
    patch_settings[pid] = PatchSettings(
        sharpness=sharpness,
        adm_scaler_end=adm_scaler_end,
        positive_adm_scale=adm_scaler_positive,
        negative_adm_scale=adm_scaler_negative,
        controlnet_softness=controlnet_softness,
        adaptive_cfg=adaptive_cfg
    )
    print(f"[CLI] Initialized patch_settings for PID {pid}")
    return pid


def cleanup_patch_settings(pid):
    """Remove patch_settings entry for the current PID."""
    if pid in patch_settings:
        del patch_settings[pid]


def run_cli_generation(args):
    """Execute the full image generation pipeline."""
    pid = None
    try:
        # --- Seed ---
        seed = args.seed if args.seed != -1 else random.randint(0, 2**31 - 1)
        print(f"[CLI] Seed: {seed}")

        # --- Performance ---
        performance_obj = flags.Performance(args.performance)
        steps = performance_obj.steps()
        print(f"[CLI] Performance: {args.performance} ({steps} steps)")

        # --- Aspect Ratio ---
        width, height = parse_aspect_ratio(args.aspect_ratio)
        print(f"[CLI] Resolution: {width}x{height}")

        # --- LoRAs ---
        refresh_loras = []
        if args.lora:
            for l in args.lora:
                parts = l.split(":")
                name = parts[0]
                weight = float(parts[1]) if len(parts) > 1 else 1.0
                refresh_loras.append((name, weight))
                print(f"[CLI] LoRA: {name} @ {weight}")

        # --- Models ---
        base_model = args.base_model or modules.config.default_base_model_name
        refiner_model = args.refiner_model if args.refiner_model not in ["None", "none", ""] else "None"
        vae_name = args.vae
        print(f"[CLI] Base model: {base_model}")
        print(f"[CLI] Refiner: {refiner_model}")
        print(f"[CLI] VAE: {vae_name}")

        # ===========================================================
        # STEP 1: Apply patches (must happen before model loading)
        # ===========================================================
        patch_all()

        # ===========================================================
        # STEP 2: Initialize patch_settings for this PID
        # This prevents the KeyError(pid) crash in modules/patch.py
        # ===========================================================
        pid = init_patch_settings(
            sharpness=args.sharpness,
            adaptive_cfg=args.cfg_scale
        )

        # ===========================================================
        # STEP 3: Clear any stale interrupt flag
        # ===========================================================
        model_management.interrupt_current_processing(False)

        # ===========================================================
        # STEP 4: Load models into GPU memory
        # ===========================================================
        print("[CLI] Loading models...")
        pipeline.refresh_everything(
            refiner_model_name=refiner_model,
            base_model_name=base_model,
            loras=refresh_loras,
            vae_name=vae_name
        )
        print("[CLI] Models loaded successfully")

        # ===========================================================
        # STEP 5: Build prompts with style application
        # ===========================================================
        use_expansion = "Fooocus V2" in args.styles

        positive_basic_workloads = []
        negative_basic_workloads = []
        if args.negative_prompt:
            negative_basic_workloads.append(args.negative_prompt)

        for s in args.styles:
            if s == "Fooocus V2":
                # Fooocus V2 = prompt expansion, not a literal style
                continue
            try:
                p, n, _ = apply_style(s, positive=args.prompt)
                positive_basic_workloads += p
                negative_basic_workloads += n
            except Exception as e:
                print(f"[WARNING] Could not apply style '{s}': {e}")

        # Always include the raw prompt
        if not positive_basic_workloads:
            positive_basic_workloads = [args.prompt]
        else:
            positive_basic_workloads = [args.prompt] + positive_basic_workloads

        if not negative_basic_workloads:
            negative_basic_workloads = [""]

        # ===========================================================
        # STEP 6: Prompt expansion (Fooocus V2 magic)
        # ===========================================================
        if use_expansion:
            print("[CLI] Running Fooocus V2 prompt expansion...")
            expansion = pipeline.final_expansion(args.prompt, seed)
            print(f"[CLI] Expansion: {expansion[:100]}...")
            positive_prompts = positive_basic_workloads + [expansion]
        else:
            positive_prompts = positive_basic_workloads

        # ===========================================================
        # STEP 7: CLIP encode
        # ===========================================================
        print("[CLI] Encoding prompts (CLIP)...")
        c = pipeline.clip_encode(
            texts=positive_prompts,
            pool_top_k=len(positive_basic_workloads)
        )
        uc = pipeline.clip_encode(
            texts=negative_basic_workloads,
            pool_top_k=len(negative_basic_workloads)
        )

        # ===========================================================
        # STEP 7.5: Apply ControlNets (e.g., CPDS for text structure)
        # ===========================================================
        if args.cn_cpds:
            controlnet_cpds_path = modules.config.downloading_controlnet_cpds()

            print(f"[CLI] Loading CPDS ControlNet image from {args.cn_cpds}...")
            cn_img = cv2.imread(args.cn_cpds)
            if cn_img is None:
                print(f"[WARNING] Could not load CPDS image at {args.cn_cpds}. Skipping CPDS.")
            else:
                cn_img = cv2.cvtColor(cn_img, cv2.COLOR_BGR2RGB)
                cn_img = util.resize_image(util.HWC3(cn_img), width=width, height=height)
                cn_img = preprocessors.cpds(cn_img)
                cn_img = util.HWC3(cn_img)
                cn_pytorch = core.numpy_to_pytorch(cn_img)

                print("[CLI] Refreshing ControlNet models...")
                pipeline.refresh_controlnets([controlnet_cpds_path])

                print(f"[CLI] Applying CPDS ControlNet (weight={args.cn_cpds_weight}, stop={args.cn_cpds_stop})")
                c, uc = core.apply_controlnet(
                    c, uc,
                    pipeline.loaded_ControlNets[controlnet_cpds_path],
                    cn_pytorch,
                    args.cn_cpds_weight,
                    0.0,
                    args.cn_cpds_stop
                )

        # ===========================================================
        # STEP 8: Prepare img2img latent (if input-image provided)
        # ===========================================================
        initial_latent = None
        denoise_strength = 1.0

        if args.input_image:
            print(f"[CLI] Loading input image for img2img: {args.input_image}")
            input_img = cv2.imread(args.input_image)
            if input_img is None:
                print(f"[ERROR] Could not load input image: {args.input_image}")
                sys.exit(1)
            input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
            input_img = util.HWC3(input_img)

            # Resize to match target resolution
            from modules.util import set_image_shape_ceil, get_image_shape_ceil, resize_image
            input_img = resize_image(input_img, width=width, height=height)

            # VAE encode to get initial latent
            initial_pixels = core.numpy_to_pytorch(input_img)
            candidate_vae, _ = pipeline.get_candidate_vae(
                steps=steps,
                switch=int(steps * args.refiner_switch),
                denoise=args.vary_strength,
                refiner_swap_method="joint"
            )
            initial_latent = core.encode_vae(vae=candidate_vae, pixels=initial_pixels)
            denoise_strength = args.vary_strength
            B, C, H, W = initial_latent['samples'].shape
            width = W * 8
            height = H * 8
            print(f"[CLI] img2img mode: denoise={denoise_strength}, latent resolution={width}x{height}")

        # ===========================================================
        # STEP 9: Generate images
        # ===========================================================
        switch = int(steps * args.refiner_switch)
        all_images = []

        for i in range(args.image_number):
            current_seed = seed + i
            mode_label = f"img2img (denoise={denoise_strength})" if initial_latent else "txt2img"
            print(f"\n[CLI] === Generating image {i + 1}/{args.image_number} (seed={current_seed}, {mode_label}) ===")

            # Ensure interrupt flag is clear before each image
            model_management.interrupt_current_processing(False)

            def callback(step, x0, x, total_steps, y):
                print(f"  Step {step}/{total_steps}", end="\r", flush=True)

            imgs = pipeline.process_diffusion(
                positive_cond=c,
                negative_cond=uc,
                steps=steps,
                switch=switch,
                width=width,
                height=height,
                image_seed=current_seed,
                callback=callback,
                sampler_name=args.sampler,
                scheduler_name=args.scheduler,
                latent=initial_latent,
                denoise=denoise_strength,
                tiled=False,
                cfg_scale=args.cfg_scale,
                refiner_swap_method="joint",
                disable_preview=args.disable_preview
            )
            all_images.extend(imgs)
            print(f"  Image {i + 1} generated successfully")

        # ===========================================================
        # STEP 10: Save images
        # ===========================================================
        print(f"\n[CLI] Saving {len(all_images)} image(s)...")

        from PIL import Image
        import numpy as np

        out_dir = os.path.abspath(os.path.join(PROJECT_ROOT, args.output))
        os.makedirs(out_dir, exist_ok=True)

        saved_paths = []
        timestamp = int(time.time())
        for i, img in enumerate(all_images):
            filename = f"fooocus_{timestamp}_{seed}_{i}.{args.output_format}"
            filepath = os.path.join(out_dir, filename)

            if isinstance(img, np.ndarray):
                pil_img = Image.fromarray(img)
            else:
                pil_img = img

            if args.output_format == "jpg":
                pil_img.save(filepath, quality=95)
            elif args.output_format == "webp":
                pil_img.save(filepath, quality=95)
            else:
                pil_img.save(filepath)

            print(f"  Saved: {filepath}")
            saved_paths.append(filepath)

        print(f"\n[CLI] Done! {len(saved_paths)} image(s) saved to {out_dir}")
        return saved_paths

    except Exception:
        print("\n[CLI] Error during generation:")
        traceback.print_exc()
        raise
    finally:
        # Always clean up patch_settings
        if pid is not None:
            cleanup_patch_settings(pid)


if __name__ == "__main__":
    try:
        paths = run_cli_generation(cli_args)
        # Print final output as JSON for programmatic consumption
        import json
        print(f"\n__OUTPUT_JSON__={json.dumps(paths)}")
    except SystemExit:
        raise
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)
