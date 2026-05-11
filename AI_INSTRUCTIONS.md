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

## Best Practices for Arabic & Non-Latin Text Rendering

Fooocus (SDXL) naturally struggles with complex Arabic ligatures and right-to-left scripts compared to closed-source alternatives. When tasked with generating Arabic text, employ the following strategies:

### 1. Advanced Prompting (Supported in CLI)
*   **Clear Syntax:** Provide the exact text and specify the language/script. Example: *"A professional poster with bold Arabic text 'مرحبا بالعالم' in elegant Naskh calligraphy, high contrast, clear legible letters, right-to-left script"*
*   **Weights & Descriptors:** Use weighting to enforce the text constraint: *(Arabic text:1.3), perfect spelling, sharp typography, legible letters, no distortion*.
*   **Negative Prompting:** Always use strong negative prompts: *blurry text, deformed letters, disconnected Arabic script, wrong spelling, Latin gibberish, low quality text*.
*   **Styles & Settings:** Use the `Fooocus V2` style preset. Higher `--cfg-scale` (4–8) and higher `--steps` (30–60 via Quality mode) improve structural coherence.

### 2. Custom Models & LoRAs (Supported in CLI)
*   Use typography-specific SDXL LoRAs (e.g., search for `text`, `typography`, `logo`, or `font` LoRAs on Civitai).
*   Look for Middle Eastern/Arabic fine-tuned base models or calligraphy LoRAs.
*   Apply them using `--lora "filename:weight"` or `--base-model "filename"`.

### 3. Image Prompting / ControlNet (Requires Script Extension or UI)
*   **Highly Recommended:** The most effective way to render precise Arabic text is to use **Image Prompts** combined with **CPDS** (Contrast Preserving Decolorization Structure) or **PyraCanny** ControlNets.
*   Generate a clean reference image containing the exact Arabic text (e.g., via a Python script using Pillow and a TTF font).
*   *Note: This feature is not currently exposed in the basic CLI arguments. To implement this autonomously, you must either modify `fooocus_cli_direct.py` to accept Image Prompts, or utilize the Fooocus WebUI.*

### 4. Hybrid Post-Processing (Agentic Workflow)
*   Generate a base image with the desired aesthetic but generic text.
*   Use a separate Python script with an imaging library (like PIL/Pillow or OpenCV) to overlay perfectly rendered TTF Arabic text onto the generated image.
*   *(Optional)* Run the composite image through Fooocus Inpainting (requires extending the CLI) to blend the text naturally into the environment.
