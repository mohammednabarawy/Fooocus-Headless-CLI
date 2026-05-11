"""
Arabic Poster Pipeline - End-to-end orchestrator for generating images with
correct Arabic text using Fooocus.

THE FUNDAMENTAL TRUTH: SDXL cannot natively generate correct Arabic text.
The model lacks Arabic glyph understanding in its weights. This pipeline
solves the problem by splitting the work:

  1. GENERATE: Fooocus creates the artistic scene/background (no text)
  2. RENDER:   PIL renders pixel-perfect Arabic text with proper shaping
  3. COMPOSITE: Text is overlaid onto the scene with professional effects
  4. (OPTIONAL) HARMONIZE: Fooocus inpainting blends text edges naturally

Usage:
    python arabic_poster_pipeline.py \\
        --arabic-text "مرحبا بالعالم" \\
        --scene-prompt "A beautiful luxury hotel lobby, marble floors, golden lighting" \\
        --output final_poster.png

    python arabic_poster_pipeline.py \\
        --arabic-text "بسم الله الرحمن الرحيم" \\
        --scene-prompt "elegant Islamic geometric pattern background, dark blue and gold" \\
        --text-position bottom --text-effect shadow --darken 0.4 \\
        --output islamic_art.png
"""

import os
import sys
import argparse
import subprocess
import time
import json
import glob

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


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
    steps=None,
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
    print(f"  Running: {' '.join(cmd[:6])}...")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print(f"[PIPELINE] Fooocus generation FAILED!")
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

    print(f"  Final: {output_path}")
    return output_path


def run_full_pipeline(args):
    """
    Execute the complete Arabic poster generation pipeline.

    Workflow:
      1. Generate scene with Fooocus (prompt describes scene WITHOUT text)
      2. Composite Arabic text onto the generated scene
      3. Save final result
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

    # Step 2: Composite text onto each generated scene
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

        result = run_text_compositing(
            arabic_text=args.arabic_text,
            background_path=scene_path,
            output_path=out_path,
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
        final_paths.append(result)

    print(f"\n{'='*60}")
    print(f"[PIPELINE] COMPLETE! {len(final_paths)} image(s) with correct Arabic text")
    print(f"{'='*60}")
    for p in final_paths:
        print(f"  -> {p}")

    return final_paths


def main():
    parser = argparse.ArgumentParser(
        description="Arabic Poster Pipeline - Generate images with correct Arabic text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The pipeline works in two phases:
  1. Fooocus generates the artistic scene (WITHOUT text in the image)
  2. Perfect Arabic text is composited on top with professional effects

This guarantees 100%% correct Arabic text because the text is rendered
programmatically using proper RTL shaping, not generated by the AI model.

Examples:
  # Basic usage
  python arabic_poster_pipeline.py \\
      --arabic-text "مرحبا بالعالم" \\
      --scene-prompt "luxury restaurant interior, warm lighting, elegant"

  # Islamic art with Naskh calligraphy
  python arabic_poster_pipeline.py \\
      --arabic-text "بسم الله الرحمن الرحيم" \\
      --scene-prompt "intricate Islamic geometric pattern, dark blue and gold, arabesque" \\
      --font-style naskh --text-effect all --darken 0.3

  # Business poster with text at bottom
  python arabic_poster_pipeline.py \\
      --arabic-text "شركة التقنية المتقدمة\\nحلول مبتكرة للمستقبل" \\
      --scene-prompt "modern tech office, glass building, blue sky, professional" \\
      --text-position bottom --text-effect shadow --darken 0.5

  # Multiple variations
  python arabic_poster_pipeline.py \\
      --arabic-text "مرحبا" \\
      --scene-prompt "mountain sunset landscape" \\
      --image-number 4 --seed 42
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
