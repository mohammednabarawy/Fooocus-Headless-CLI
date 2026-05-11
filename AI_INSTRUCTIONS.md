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
| `--list-models` | flag | false | Print installed checkpoints, LoRAs, VAEs, ControlNets, presets, and styles |
| `--list-fonts` | flag | false | Print installed system fonts usable with `--font` |
| `--list-inventory` | flag | false | Print both model and font inventory |
| `--inventory-json` | flag | false | Machine-readable inventory output |
| `--dry-run` | flag | false | Print resolved model/prompt settings without loading diffusion models |

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

Models are located in `Fooocus/models/checkpoints/`. Always inspect the live
inventory before choosing a model:

```bash
.\fooocus-cli.bat --list-models
.\arabic-poster-cli.bat --list-models
.\arabic-poster-cli.bat --list-inventory --inventory-json
```

Common useful local checkpoints in this install include:

- `juggernautXL_v8Rundiffusion.safetensors` for general SDXL work
- `RealVisXL_V5.0_fp16.safetensors` or `realvisxlV50_v50Bakedvae.safetensors` for realistic ad/product scenes
- `epicrealismXL_vxiAbeast.safetensors` for cinematic realism
- `realisticStockPhoto_v20.safetensors` for commercial stock-photo style
- `dreamshaper_8.safetensors` and `majicmixRealistic_v7_sd1.5.safetensors` are SD1.5-era files and may not fit every SDXL workflow

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

For best CLI results, prefer the batch wrapper and a preset:

```bash
.\arabic-poster-cli.bat \
    --preset pro_text \
    --arabic-text "مستقبل الذكاء الاصطناعي" \
    --scene-prompt "premium technology poster" \
    --subject "glass AI assistant device on a desk" \
    --composition "centered product with clean negative space for headline" \
    --lighting "soft studio lighting with realistic reflections" \
    --output "outputs/arabic_ai_poster.png"
```

`--preset pro_text` enables the high-fidelity text workflow: Quality mode,
low-denoise harmonization, CPDS text-structure guidance, and one final crisp
Arabic repaint after export so glyphs stay readable without duplicate text
layers. It exports at 2x size by default.

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
| `--preset` | `balanced` | `balanced`, `pro_text`, `clean_graphic`, or `neon_sign` |
| `--prompt-profile` | `none` | `nano_banana_pro`, `image2`, `product_ad`, `infographic`, `cinematic`, or `signage` |
| `--subject`, `--composition`, `--lighting`, etc. | none | Optional creative-brief fields compiled into a clearer generation prompt |
| `--final-text-pass` | preset-based | Re-overlay exact shaped text after harmonization (`0` disables) |
| `--text-guide` | `none` | CPDS text reference for `scene`, `harmonize`, or `both` |
| `--max-lines` | none | Wrap and shrink text to fit a target line count |
| `--no-wrap` | false | Disable automatic Arabic word wrapping |
| `--export-scale`, `--export-width`, `--export-height` | `1.0` | Final high-resolution export controls, capped by `--export-max-side` |
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

You can now list and use installed system fonts by alias:

```bash
.\arabic-poster-cli.bat --list-fonts
.\arabic-poster-cli.bat --list-fonts --font-filter arab

.\arabic-poster-cli.bat \
    --preset clean_graphic \
    --arabic-text "القهوة سر الصباح" \
    --scene-prompt "premium coffee product advertisement" \
    --font "tahoma" \
    --output "outputs/coffee_arabic.png"
```

`--font` accepts a full font path or any alias printed by `--list-fonts`.

## Local Smoke Tests

Use these before reporting changes to the user:

```bash
.\python_embeded\python.exe -s -m py_compile arabic_poster_pipeline.py arabic_text_renderer.py fooocus_cli_direct.py fooocus_cli_inventory.py test_cli_inventory.py
.\python_embeded\python.exe -s test_cli_inventory.py
```

Use dry-run for fast model/preset/font checks:

```bash
.\arabic-poster-cli.bat --dry-run --preset pro_text --base-model "RealVisXL_V5.0_fp16" --font "decotype naskh" --arabic-text "تصميم فاخر" --scene-prompt "luxury perfume campaign"
.\fooocus-cli.bat --dry-run --prompt "premium product advertisement, no text" --base-model "juggernautXL_v8Rundiffusion"
```

## Professional Agent Playbook

When an AI agent is asked to generate professional images with this app:

1. Start in `D:\Fooocus_win64_2-5-0`.
2. Inspect the real install before choosing assets:

```bash
.\arabic-poster-cli.bat --list-models --inventory-limit 10
.\arabic-poster-cli.bat --list-fonts --font-filter arab --inventory-limit 20
```

3. Use `--dry-run` to resolve the model, font, preset, prompt profile, and export plan.
4. Generate one image first. Do not batch until the first image completes and the file is readable.
5. For images that need exact Arabic or any non-Latin text, always use `arabic-poster-cli.bat`, not raw text prompting.
6. For images with no required exact text, use `fooocus-cli.bat` and explicitly include `no text, no letters, no watermark` when text is unwanted.
7. Inspect generated backgrounds for accidental fake text/logos. If it appears, strengthen the scene prompt with `blank label surfaces` and the negative prompt with `logo, label text, gibberish text, pseudo text, latin letters`.
8. Inspect Arabic/text outputs for duplicate text layers. Professional defaults should use only one final repair layer: leave `pro_text` on its default final crisp export repaint, and do not add `--final-text-pass` unless `--no-crisp-export-text` is also used.
9. Verify outputs by opening/inspecting the produced files, checking dimensions, and confirming the image is nonblank.

Recommended model/preset pairings:

| Goal | CLI | Model | Preset/Profile |
|---|---|---|---|
| Arabic product poster | `arabic-poster-cli.bat` | `RealVisXL_V5.0_fp16.safetensors` | `--preset pro_text --prompt-profile nano_banana_pro` |
| Arabic signage/neon | `arabic-poster-cli.bat` | `juggernautXL_v8Rundiffusion.safetensors` | `--preset neon_sign --prompt-profile signage` |
| Clean brand/ad graphic | `arabic-poster-cli.bat` | `realisticStockPhoto_v20.safetensors` or `RealVisXL_V5.0_fp16.safetensors` | `--preset clean_graphic --prompt-profile image2` |
| Cinematic product render without text | `fooocus-cli.bat` | `epicrealismXL_vxiAbeast.safetensors` | `--styles "Fooocus V2" "Fooocus Enhance"` |

Use creative-brief fields instead of one vague prompt:

```bash
--subject "crystal perfume bottle on black marble"
--composition "centered product with clean headline space above"
--lighting "soft studio lighting, gold rim light, realistic reflections"
--brand-colors "black, champagne gold, ivory"
--camera "85mm lens, shallow depth of field"
--materials "glass, polished marble, brushed metal"
```

## Validated Advanced Runs

These commands completed successfully on this machine.

### Arabic product poster

```bash
.\arabic-poster-cli.bat --preset pro_text --base-model RealVisXL_V5.0_fp16.safetensors --font "decotype naskh" --arabic-text "تصميم فاخر" --scene-prompt "luxury perfume campaign with an unlabeled blank perfume bottle, blank front surface" --subject "unlabeled crystal perfume bottle on black marble" --composition "centered product with clean headline space above" --lighting "soft studio lighting, gold rim light, realistic reflections" --brand-colors "black, champagne gold, ivory" --negative-prompt "logo, label, label text, bottle text, brand name, fake letters, gibberish" --text-position top --text-effect all --width 896 --height 640 --output outputs\advanced_realvis_perfume_clean.png --seed 1204 --steps 24 --harmonize 0.28 --export-scale 1.5
```

Result: `outputs\advanced_realvis_perfume_clean.png`, `1344x960`. Completed scene generation, text reference, compositing, harmonization, one final crisp text pass, and resize export. This cleaned version uses stronger blank-label and fake-text negatives after visual inspection found that the first product render had hallucinated small label text on the bottle.

### Arabic neon signage

```bash
.\arabic-poster-cli.bat --preset neon_sign --base-model juggernautXL_v8Rundiffusion.safetensors --font "ae_arab" --arabic-text "ليلة القهوة" --scene-prompt "premium Arabic cafe neon sign at night" --subject "cozy modern cafe storefront after rain" --composition "wide cinematic storefront with Arabic sign area above entrance" --lighting "neon reflections on wet street, warm interior glow" --prompt-profile signage --text-position top --text-color 255,210,120 --width 896 --height 640 --output outputs\advanced_juggernaut_neon_cafe.png --seed 1202 --steps 20 --harmonize 0.34 --export-scale 1.5
```

Result: `outputs\advanced_juggernaut_neon_cafe.png`, `1344x960`. Completed scene generation, text reference, compositing, harmonization, one final exact-text pass, and resize export.

### Duplicate text-layer regression test

```bash
.\arabic-poster-cli.bat --preset pro_text --base-model RealVisXL_V5.0_fp16.safetensors --font "decotype naskh" --arabic-text "اختبار النص" --scene-prompt "minimal luxury product background with blank label surfaces" --subject "simple unlabeled glass bottle" --composition "centered product with top headline space" --negative-prompt "logo, label text, fake text, duplicate text" --text-position top --width 640 --height 448 --output outputs\duplicate_text_fix_test.png --seed 1210 --steps 12 --harmonize 0.24 --export-scale 1
```

Result: `outputs\duplicate_text_fix_test.png`, `1280x896`. Runtime log confirmed `pro_text` now skips the separate pre-export `Final exact-text pass` and applies only one `Final crisp text pass`.

### Direct product ad

```bash
.\fooocus-cli.bat --prompt "premium cinematic product advertisement, sculptural wireless headphones on brushed titanium pedestal, soft studio lighting, realistic reflections, shallow depth of field, editorial luxury campaign, no text, no letters, no watermark" --negative-prompt "text, letters, watermark, logo, blurry, low quality" --base-model epicrealismXL_vxiAbeast.safetensors --styles "Fooocus V2" "Fooocus Enhance" --aspect-ratio 896x640 --output outputs\advanced_direct_product --seed 1203 --steps 18 --performance Speed
```

Result: `outputs\advanced_direct_product\fooocus_1778542656_1203_0.png`, `896x640`. Completed raw headless Fooocus generation and JSON output reporting.

File readability/nonblank check used:

```bash
.\python_embeded\python.exe -s -c "import sys; sys.path.insert(0, r'D:\Fooocus_win64_2-5-0'); from PIL import Image, ImageStat; paths=[r'outputs\advanced_realvis_perfume_clean.png', r'outputs\advanced_juggernaut_neon_cafe.png', r'outputs\advanced_direct_product\fooocus_1778542656_1203_0.png']; [print(p, Image.open(p).size, ImageStat.Stat(Image.open(p).convert('L')).extrema[0]) for p in paths]"
```
