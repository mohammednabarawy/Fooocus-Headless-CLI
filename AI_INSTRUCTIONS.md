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
| `--vae` | string | `Default (model)` | VAE model name |
| `--output-format` | choice | `png` | `png` / `jpg` / `webp` |

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

# Custom model
.\fooocus-cli.bat --prompt "landscape" --base-model realisticVisionV60B1_v51VAE.safetensors
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
