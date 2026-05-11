"""
Arabic Poster Pipeline - End-to-end orchestrator for generating images with
correct Arabic text using Fooocus.

THE FUNDAMENTAL TRUTH: SDXL cannot natively generate correct Arabic text.
The model lacks Arabic glyph understanding in its weights. This pipeline
solves the problem with a 3-step process:

  1. GENERATE: Fooocus creates the artistic scene/background (no text)
  2. COMPOSITE: PIL renders pixel-perfect Arabic text onto the scene
  3. HARMONIZE: Fooocus img2img at low denoise blends the text into
     the scene's style/lighting/texture — making it look PAINTED IN,
     not pasted on top.

Usage:
    python arabic_poster_pipeline.py \\
        --arabic-text "مرحبا بالعالم" \\
        --scene-prompt "A beautiful luxury hotel lobby, marble floors, golden lighting" \\
        --output final_poster.png

    python arabic_poster_pipeline.py \\
        --arabic-text "بسم الله الرحمن الرحيم" \\
        --scene-prompt "elegant Islamic geometric pattern background, dark blue and gold" \\
        --text-position bottom --text-effect shadow --darken 0.4 \\
        --harmonize 0.35 --output islamic_art.png
"""

import os
import sys
import argparse
import subprocess
import time
import json
import glob

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _run_fooocus_cmd(cmd, label="Fooocus"):
    """Run a Fooocus CLI command and parse output paths."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print(f"[PIPELINE] {label} FAILED!")
        print(f"  STDERR: {result.stderr[-500:]}")
        print(f"  STDOUT: {result.stdout[-500:]}")
        return []

    # Parse output paths from JSON marker
    paths = []
    for line in result.stdout.splitlines():
        if "__OUTPUT_JSON__=" in line:
            json_str = line.split("__OUTPUT_JSON__=", 1)[1]
            paths = json.loads(json_str)
            break

    return paths


def run_fooocus_generation(
    prompt,
    output_dir,
    width=1152,
    height=896,
    negative_prompt="",
    seed=-1,
    performance="Speed",
    styles=None,
    base_model=None,
    cfg_scale=7.0,
    sampler="dpmpp_2m_sde_gpu",
    scheduler="karras",
    image_number=1,
    loras=None,
    cn_cpds=None,
    cn_cpds_weight=0.7,
    cn_cpds_stop=0.75,
):
    """
    Run Fooocus image generation via the CLI.
    Returns list of generated image paths.
    """
    python_exe = os.path.join(PROJECT_ROOT, "python_embeded", "python.exe")
    cli_script = os.path.join(PROJECT_ROOT, "fooocus_cli_direct.py")

    if not os.path.exists(python_exe):
        python_exe = sys.executable

    cmd = [
        python_exe, cli_script,
        "--prompt", prompt,
        "--output", output_dir,
        "--aspect-ratio", f"{width}x{height}",
        "--cfg-scale", str(cfg_scale),
        "--sampler", sampler,
        "--scheduler", scheduler,
        "--image-number", str(image_number),
        "--performance", performance,
    ]

    if negative_prompt:
        cmd.extend(["--negative-prompt", negative_prompt])
    if seed != -1:
        cmd.extend(["--seed", str(seed)])
    if styles:
        cmd.extend(["--styles"] + styles)
    if base_model:
        cmd.extend(["--base-model", base_model])
    if loras:
        for lora in loras:
            cmd.extend(["--lora", lora])
    if cn_cpds:
        cmd.extend([
            "--cn-cpds", cn_cpds,
            "--cn-cpds-weight", str(cn_cpds_weight),
            "--cn-cpds-stop", str(cn_cpds_stop),
        ])

    print(f"\n{'='*60}")
    print(f"[PIPELINE] Step 1: Generating scene with Fooocus")
    print(f"{'='*60}")
    print(f"  Prompt: {prompt[:100]}...")
    print(f"  Resolution: {width}x{height}")

    paths = _run_fooocus_cmd(cmd, "Scene generation")

    if not paths:
        # Fallback: find most recent files in output dir
        full_output = os.path.join(PROJECT_ROOT, output_dir)
        candidates = sorted(
            glob.glob(os.path.join(full_output, "fooocus_*")),
            key=os.path.getmtime,
            reverse=True
        )
        paths = candidates[:image_number]

    print(f"  Generated {len(paths)} image(s)")
    for p in paths:
        print(f"    -> {p}")
    return paths


def run_harmonization(
    composited_image_path,
    output_path,
    prompt,
    negative_prompt="",
    width=1152,
    height=896,
    denoise_strength=0.35,
    seed=-1,
    performance="Speed",
    styles=None,
    base_model=None,
    cfg_scale=7.0,
    loras=None,
):
    """
    Run Fooocus img2img at LOW denoise to harmonize composited text.

    This is THE KEY STEP that makes the text look painted into the scene
    rather than pasted on top. At 0.25-0.45 denoise:
    - The diffusion model re-renders the image lightly
    - Text inherits scene lighting, texture, color palette
    - Edges blend naturally
    - Overall structure (text shape) is preserved

    Args:
        composited_image_path: The composited image (scene + text overlay)
        output_path: Where to save the harmonized result
        prompt: Should describe the desired look ("elegant Arabic calligraphy...")
        denoise_strength: 0.25-0.45 for best results (too low = no effect, too high = destroys text)
    """
    python_exe = os.path.join(PROJECT_ROOT, "python_embeded", "python.exe")
    cli_script = os.path.join(PROJECT_ROOT, "fooocus_cli_direct.py")

    if not os.path.exists(python_exe):
        python_exe = sys.executable

    cmd = [
        python_exe, cli_script,
        "--prompt", prompt,
        "--input-image", composited_image_path,
        "--vary-strength", str(denoise_strength),
        "--output", os.path.dirname(output_path) or "outputs",
        "--aspect-ratio", f"{width}x{height}",
        "--cfg-scale", str(cfg_scale),
        "--image-number", "1",
        "--performance", performance,
    ]

    if negative_prompt:
        cmd.extend(["--negative-prompt", negative_prompt])
    if seed != -1:
        cmd.extend(["--seed", str(seed)])
    if styles:
        cmd.extend(["--styles"] + styles)
    if base_model:
        cmd.extend(["--base-model", base_model])
    if loras:
        for lora in loras:
            cmd.extend(["--lora", lora])

    print(f"\n{'='*60}")
    print(f"[PIPELINE] Step 3: Harmonizing text with scene (denoise={denoise_strength})")
    print(f"{'='*60}")
    print(f"  Input: {composited_image_path}")
    print(f"  Denoise: {denoise_strength}")

    paths = _run_fooocus_cmd(cmd, "Harmonization")

    if paths:
        # Copy the harmonized result to the desired output path
        import shutil
        shutil.copy2(paths[0], output_path)
        print(f"  Harmonized: {output_path}")
        return output_path
    else:
        print(f"  [WARNING] Harmonization failed, using composited image as final output")
        import shutil
        shutil.copy2(composited_image_path, output_path)
        return output_path


def run_text_compositing(
    arabic_text,
    background_path,
    output_path,
    font_style="default",
    font_path=None,
    effect="shadow",
    position="center",
    font_size=None,
    opacity=1.0,
    darken=0.0,
    padding=60,
    text_color="255,255,255",
):
    """
    Composite Arabic text onto a background image.
    Uses the ArabicTextRenderer module.
    """
    print(f"\n{'='*60}")
    print(f"[PIPELINE] Step 2: Compositing Arabic text")
    print(f"{'='*60}")
    print(f"  Text: {arabic_text}")
    print(f"  Background: {background_path}")
    print(f"  Effect: {effect}, Position: {position}")

    # Import renderer
    sys.path.insert(0, PROJECT_ROOT)
    from arabic_text_renderer import ArabicTextRenderer

    renderer = ArabicTextRenderer(font_style=font_style, font_path=font_path)

    tc = tuple(int(c) for c in text_color.split(","))

    renderer.composite_text_on_image(
        text=arabic_text,
        background_path=background_path,
        output_path=output_path,
        padding=padding,
        text_color=tc,
        effect=effect,
        position=position,
        font_size=font_size,
        opacity=opacity,
        text_area_darken=darken,
    )

    print(f"  Composited: {output_path}")
    return output_path


def run_full_pipeline(args):
    """
    Execute the complete Arabic poster generation pipeline.

    Workflow:
      1. Generate scene with Fooocus (prompt describes scene WITHOUT text)
      2. Composite Arabic text onto the generated scene
      3. (Optional) Harmonize with img2img to blend text into scene
    """
    timestamp = int(time.time())
    temp_dir = os.path.join(PROJECT_ROOT, "outputs", "pipeline_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Auto-enhance prompt to exclude text generation attempts
    scene_prompt = args.scene_prompt
    if not any(kw in scene_prompt.lower() for kw in ["no text", "without text", "text-free", "blank"]):
        scene_prompt += ", no text, no letters, no words, clean background"

    negative = args.negative_prompt or ""
    if negative:
        negative += ", "
    negative += "text, letters, words, typography, writing, watermark, signature"

    # Step 1: Generate the scene
    scene_paths = run_fooocus_generation(
        prompt=scene_prompt,
        output_dir="outputs",
        width=args.width,
        height=args.height,
        negative_prompt=negative,
        seed=args.seed,
        performance=args.performance,
        styles=args.styles,
        base_model=args.base_model,
        cfg_scale=args.cfg_scale,
        image_number=args.image_number,
        loras=args.lora,
    )

    if not scene_paths:
        print("\n[PIPELINE] FAILED: No scene images were generated.")
        return []

    # Step 2 & 3: Composite text + optional harmonization
    final_paths = []
    for i, scene_path in enumerate(scene_paths):
        if args.image_number > 1:
            base, ext = os.path.splitext(args.output)
            out_path = f"{base}_{i}{ext}"
        else:
            out_path = args.output

        # Make output path absolute
        if not os.path.isabs(out_path):
            out_path = os.path.join(PROJECT_ROOT, out_path)

        # Step 2: Composite text
        if args.harmonize > 0:
            # Save intermediate composite to temp
            composite_path = os.path.join(temp_dir, f"composite_{timestamp}_{i}.png")
        else:
            composite_path = out_path

        run_text_compositing(
            arabic_text=args.arabic_text,
            background_path=scene_path,
            output_path=composite_path,
            font_style=args.font_style,
            font_path=args.font,
            effect=args.text_effect,
            position=args.text_position,
            font_size=args.font_size,
            opacity=args.opacity,
            darken=args.darken,
            padding=args.padding,
            text_color=args.text_color,
        )

        # Step 3: Harmonize (if enabled)
        if args.harmonize > 0:
            harmonize_prompt = f"{args.scene_prompt}, beautiful Arabic calligraphy text, elegant typography, integrated text design"
            harmonize_negative = "blurry text, distorted letters, illegible, low quality"

            run_harmonization(
                composited_image_path=composite_path,
                output_path=out_path,
                prompt=harmonize_prompt,
                negative_prompt=harmonize_negative,
                width=args.width,
                height=args.height,
                denoise_strength=args.harmonize,
                seed=args.seed + i if args.seed != -1 else -1,
                performance=args.performance,
                styles=args.styles,
                base_model=args.base_model,
                cfg_scale=args.cfg_scale,
                loras=args.lora,
            )

        final_paths.append(out_path)

    mode = "harmonized" if args.harmonize > 0 else "composited"
    print(f"\n{'='*60}")
    print(f"[PIPELINE] COMPLETE! {len(final_paths)} {mode} image(s) with Arabic text")
    print(f"{'='*60}")
    for p in final_paths:
        print(f"  -> {p}")

    return final_paths


def main():
    parser = argparse.ArgumentParser(
        description="Arabic Poster Pipeline - Generate images with correct Arabic text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The pipeline works in three phases:
  1. Fooocus generates the artistic scene (WITHOUT text in the image)
  2. Perfect Arabic text is composited on top with professional effects
  3. (Optional) Fooocus img2img re-renders at low denoise to HARMONIZE
     the text into the scene's style, lighting, and texture

The harmonization step is what makes text look PAINTED INTO the scene
rather than pasted on top. Use --harmonize 0.3 to 0.45 for best results.

Examples:
  # Basic (composite only, fast)
  python arabic_poster_pipeline.py \\
      --arabic-text "مرحبا بالعالم" \\
      --scene-prompt "luxury restaurant interior, warm lighting, elegant"

  # With harmonization (text looks integrated into scene)
  python arabic_poster_pipeline.py \\
      --arabic-text "مرحبا بالعالم" \\
      --scene-prompt "luxury restaurant interior, warm lighting, elegant" \\
      --harmonize 0.35

  # Islamic art with Naskh calligraphy, harmonized
  python arabic_poster_pipeline.py \\
      --arabic-text "بسم الله الرحمن الرحيم" \\
      --scene-prompt "intricate Islamic geometric pattern, dark blue and gold" \\
      --font-style naskh --text-effect all --darken 0.3 --harmonize 0.3

  # Business poster (no harmonization needed for clean backgrounds)
  python arabic_poster_pipeline.py \\
      --arabic-text "شركة التقنية المتقدمة\\nحلول مبتكرة للمستقبل" \\
      --scene-prompt "modern tech office, glass building, blue sky" \\
      --text-position bottom --text-effect shadow --darken 0.5

  # Multiple variations
  python arabic_poster_pipeline.py \\
      --arabic-text "مرحبا" \\
      --scene-prompt "mountain sunset landscape" \\
      --image-number 4 --seed 42 --harmonize 0.35
        """
    )

    # Required
    parser.add_argument("--arabic-text", required=True,
                        help="Arabic text to render (use \\\\n for newlines)")
    parser.add_argument("--scene-prompt", required=True,
                        help="Prompt describing the SCENE/BACKGROUND (do NOT include text descriptions)")

    # Output
    parser.add_argument("--output", default="arabic_poster.png",
                        help="Output file path")
    parser.add_argument("--width", type=int, default=1152, help="Image width")
    parser.add_argument("--height", type=int, default=896, help="Image height")

    # Harmonization
    parser.add_argument("--harmonize", type=float, default=0.0,
                        help="Harmonization strength (0=disabled, 0.25-0.45=recommended). "
                             "Makes text look PAINTED INTO the scene via low-denoise img2img.")

    # Text styling
    parser.add_argument("--font-style", default="default",
                        choices=["default", "naskh", "arabic"],
                        help="Font style for Arabic text")
    parser.add_argument("--font", default=None, help="Custom font file path")
    parser.add_argument("--text-effect", default="shadow",
                        choices=["none", "outline", "shadow", "glow", "all"],
                        help="Text visual effect")
    parser.add_argument("--text-position", default="center",
                        choices=["center", "top", "bottom"],
                        help="Text placement on the image")
    parser.add_argument("--font-size", type=int, default=None,
                        help="Fixed font size (auto-fit if not set)")
    parser.add_argument("--opacity", type=float, default=1.0,
                        help="Text opacity (0.0-1.0)")
    parser.add_argument("--darken", type=float, default=0.0,
                        help="Darken area behind text for readability (0.0-1.0)")
    parser.add_argument("--padding", type=int, default=60,
                        help="Padding from image edges in pixels")
    parser.add_argument("--text-color", default="255,255,255",
                        help="Text color as R,G,B")

    # Fooocus generation settings
    parser.add_argument("--negative-prompt", default="",
                        help="Negative prompt for scene generation")
    parser.add_argument("--seed", type=int, default=-1, help="Random seed")
    parser.add_argument("--performance", default="Speed",
                        choices=["Speed", "Quality", "Extreme Speed"])
    parser.add_argument("--styles", nargs="+", default=["Fooocus V2"],
                        help="Fooocus style presets")
    parser.add_argument("--base-model", default=None, help="Base model name")
    parser.add_argument("--cfg-scale", type=float, default=7.0)
    parser.add_argument("--image-number", type=int, default=1,
                        help="Number of scene variations to generate")
    parser.add_argument("--lora", action="append",
                        help="LoRA in format 'name:weight' (repeatable)")

    args = parser.parse_args()
    run_full_pipeline(args)


if __name__ == "__main__":
    main()
