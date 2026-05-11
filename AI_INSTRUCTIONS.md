# Fooocus Headless CLI — AI Agent Instructions

> **For any AI agent**: This document tells you exactly how to generate images
> using the Fooocus installation at this directory, without opening a browser.

## Quick Start

```bash
# From this directory (d:\Fooocus_win64_2-5-0):
.\fooocus-cli.bat --prompt "your prompt here"

# Or directly:
.\python_embeded\python.exe -s fooocus_cli_direct.py --prompt "your prompt here"
```

## Full Argument Reference

| Argument | Type | Default | Description |
|---|---|---|---|
| `--prompt` | string | **required** | The image description |
| `--negative-prompt` | string | `""` | Things to avoid in the image |
| `--output` | path | `outputs` | Output directory (relative to project root) |
| `--seed` | int | `-1` | Random seed (`-1` = random) |
| `--performance` | choice | `Speed` | `Speed` / `Quality` / `Extreme Speed` |
| `--aspect-ratio` | string | `1152×896` | `WIDTHxHEIGHT` (e.g., `1024x1024`) |
| `--styles` | list | `Fooocus V2` | Style presets (space-separated) |
| `--base-model` | string | config default | Model `.safetensors` filename |
| `--refiner-model` | string | `None` | Refiner model (`None` to disable) |
| `--refiner-switch` | float | `0.5` | When to switch to refiner (0.0–1.0) |
| `--cfg-scale` | float | `7.0` | Classifier-Free Guidance scale |
| `--sharpness` | float | `2.0` | Fooocus sharpness enhancement |
| `--image-number` | int | `1` | Number of images to generate |
| `--sampler` | string | `dpmpp_2m_sde_gpu` | Sampler algorithm |
| `--scheduler` | string | `karras` | Noise scheduler |
| `--lora` | string | none | LoRA as `filename:weight` (repeatable) |
| `--steps` | int | none | Override performance steps |

## Examples

```bash
# Simple generation
.\fooocus-cli.bat --prompt "a cyberpunk cityscape at night, neon lights"

# High quality with specific seed
.\fooocus-cli.bat --prompt "portrait of a warrior" --performance Quality --seed 12345

# Multiple images, square aspect ratio
.\fooocus-cli.bat --prompt "abstract fractal art" --image-number 4 --aspect-ratio 1024x1024

# With LoRA weights
.\fooocus-cli.bat --prompt "detailed mech robot" --lora "add_detail:0.8"

# With specific steps
.\fooocus-cli.bat --prompt "abstract art" --aspect-ratio 1024x1024 --steps 40
```

## Output

- Images are saved to the `--output` directory (default: `outputs/`)
- Filenames follow pattern: `fooocus_{timestamp}_{seed}_{index}.{format}`
- The script prints `__OUTPUT_JSON__=["path1", "path2", ...]` on the last line for programmatic parsing

## Available Models

Models are located in `Fooocus/models/checkpoints/`. The default base model
is configured in `Fooocus/modules/config.py`. Common models:

- `juggernautXL_v8Rundiffusion.safetensors` (default)
- Check `Fooocus/models/checkpoints/` for all available models

LoRA files are in `Fooocus/models/loras/`.

## Available Styles

Style presets are loaded from `Fooocus/sdxl_styles/*.json`. The special style
`Fooocus V2` enables the built-in prompt expansion engine (recommended).

## Architecture Notes

- **Entry point**: `fooocus_cli_direct.py` — bypasses Gradio/web server entirely
- **Python**: Uses the embedded Python at `python_embeded/python.exe`
- **GPU**: Requires CUDA-capable GPU (PyTorch 2.7.1 + CUDA 12.8)
- **Models directory**: `Fooocus/models/` (symlinked to shared model store)

## Error Handling

- Exit code `0` = success
- Exit code `1` = error (details printed to stderr)
- The `__OUTPUT_JSON__` line is only printed on success

## Performance

- **Speed mode**: ~30 steps, ~15 seconds per image on modern GPU
- **Quality mode**: ~60 steps, ~30 seconds per image
- **Extreme Speed**: ~8 steps, ~5 seconds (lower quality)

Model loading adds ~2-5 seconds on first run; subsequent runs reuse loaded models.

## Arabic & Non-Latin Text Generation (CRITICAL)

> **SDXL cannot natively generate correct Arabic text.** The model lacks Arabic
> glyph understanding in its weights. No amount of prompt engineering or ControlNet
> will reliably produce correct Arabic script. The solution below is the **only
> reliable method**.

### The Hybrid Pipeline (PRIMARY METHOD)

Use `arabic_poster_pipeline.py` — a one-command orchestrator that:
1. **Generates** the artistic scene with Fooocus (prompt describes scene, NOT text)
2. **Composites** pixel-perfect Arabic text using PIL with proper RTL shaping
3. **Harmonizes** the text by piping the composite back into Fooocus using `img2img` at a low denoise strength, allowing the model to blend the text into the scene's lighting, textures, and style.

```bash
# Basic usage
.\python_embeded\python.exe arabic_poster_pipeline.py \
    --arabic-text "مرحبا بالعالم" \
    --scene-prompt "luxury hotel lobby, marble floors, golden lighting"

# Islamic art with Naskh calligraphy, bottom text, darkened backdrop
.\python_embeded\python.exe arabic_poster_pipeline.py \
    --arabic-text "بسم الله الرحمن الرحيم" \
    --scene-prompt "intricate Islamic geometric pattern, dark blue and gold" \
    --font-style naskh --text-effect all --text-position bottom --darken 0.4

# High-fidelity blended text using Harmonization (img2img at 0.35 denoise)
.\python_embeded\python.exe arabic_poster_pipeline.py \
    --arabic-text "بسم الله الرحمن الرحيم" \
    --scene-prompt "intricate Islamic geometric pattern, dark blue and gold" \
    --font-style naskh --harmonize 0.35

# Multi-line business poster
.\python_embeded\python.exe arabic_poster_pipeline.py \
    --arabic-text "شركة التقنية المتقدمة\nحلول مبتكرة للمستقبل" \
    --scene-prompt "modern tech office, glass building, blue sky" \
    --text-position bottom --text-effect shadow --darken 0.5

# Multiple variations
.\python_embeded\python.exe arabic_poster_pipeline.py \
    --arabic-text "مرحبا" \
    --scene-prompt "mountain sunset landscape" \
    --image-number 4 --seed 42
```

### Pipeline Arguments

| Argument | Default | Description |
|---|---|---|
| `--arabic-text` | **required** | Arabic text to render (`\n` for newlines) |
| `--scene-prompt` | **required** | Scene description (NO text in prompt) |
| `--output` | `arabic_poster.png` | Output file path |
| `--font-style` | `default` | `default` (Arial), `naskh`, or `arabic` |
| `--font` | auto | Custom `.ttf` font path |
| `--text-effect` | `shadow` | `none`, `outline`, `shadow`, `glow`, `all` |
| `--text-position` | `center` | `center`, `top`, `bottom` |
| `--font-size` | auto-fit | Fixed font size in px |
| `--opacity` | `1.0` | Text opacity (0.0–1.0) |
| `--darken` | `0.0` | Darken backdrop behind text (0.0–1.0) |
| `--text-color` | `255,255,255` | RGB text color |
| `--padding` | `60` | Edge padding in px |
| Plus all Fooocus args: `--seed`, `--performance`, `--base-model`, `--lora`, etc. |

### Standalone Text Renderer

`arabic_text_renderer.py` can be used independently for three modes:

```bash
# Mode 1: ControlNet reference (white-on-black)
.\python_embeded\python.exe arabic_text_renderer.py \
    --text "مرحبا بالعالم" --mode reference --output ref.png --style naskh

# Mode 2: Composite text onto existing image
.\python_embeded\python.exe arabic_text_renderer.py \
    --text "مرحبا" --mode composite --background scene.png --output final.png --effect shadow

# Mode 3: Create inpaint mask for text area
.\python_embeded\python.exe arabic_text_renderer.py \
    --text "النص" --mode mask --output mask.png --dilate 15
```

### ControlNet CPDS (Supplementary — NOT Sufficient Alone)

The CLI also supports CPDS ControlNet for structural guidance. This can improve
text-like shapes but **will NOT produce correct Arabic glyphs**. Use only as a
supplement to the hybrid pipeline, never as the sole method:

```bash
.\python_embeded\python.exe fooocus_cli_direct.py \
    --prompt "poster with Arabic calligraphy" \
    --cn-cpds ref.png --cn-cpds-weight 0.8 --cn-cpds-stop 0.8
```

### Why Other Methods Fail

| Method | Result |
|---|---|
| Prompt engineering | Garbled/hallucinated glyphs ~95% of the time |
| ControlNet (CPDS) | Approximate shapes, but incorrect ligatures & diacritics |
| LoRA fine-tuning | Improves aesthetics, but cannot guarantee spelling accuracy |
| **Hybrid compositing** | **100% correct text, every time** ✓ |

### Font Availability

The renderer auto-discovers fonts. Available styles on this system:
- **default**: Arial (best Unicode coverage, recommended for most text)
- **naskh**: DTNaskh family (beautiful calligraphic style, some glyphs may be missing)
- **arabic**: ArabType, ArabSQ

For custom fonts, use `--font "C:\path\to\font.ttf"`.

