# Fooocus CLI (Command Line Interface)

This is a custom Command Line Interface for Fooocus, allowing you to generate images programmatically without launching the web browser. It supports advanced features like model selection, custom styles, LoRAs, and batch generation.

## 🚀 Quick Start

A batch file has been created in the root directory for easy access:

```powershell
.\fooocus-cli.bat --prompt "a beautiful landscape" --output "landscape.png"
```

## 🛠️ Usage & Arguments

### Basic Usage

```powershell
.\fooocus-cli.bat --prompt "your prompt" --aspect-ratio "1024x1024"
```

### Advanced Usage

```powershell
.\fooocus-cli.bat ^
  --prompt "cyberpunk detective, neon rain" ^
  --negative-prompt "bright, sunny" ^
  --steps 30 ^
  --cfg-scale 7.0 ^
  --style "Fooocus V2" --style "Fooocus Cyberpunk" ^
  --base-model "juggernautXL_v8Rundiffusion.safetensors" ^
  --lora "sd_xl_offset_example-lora_1.0.safetensors:0.5" ^
  --image-number 2 ^
  --output "detective.png"
```

### Argument Reference

| Category | Argument | Description | Default |
| :--- | :--- | :--- | :--- |
| **Core** | `--prompt` | **(Required)** The positive prompt text. | N/A |
| | `--negative-prompt` | valid negative prompt text. | "" |
| | `--output` | Output filename. Relative command run location. | N/A |
| | `--seed` | Seed number for reproducibility. `-1` is random. | -1 |
| | `--image-number` | Number of images to generate in a row. | 1 |
| **Performance** | `--performance` | Preset: `Speed`, `Quality`, `Extreme Speed`. | Speed |
| | `--steps` | Exact number of sampling steps (overrides performance). | N/A |
| | `--aspect-ratio` | Dimensions (e.g., `1152x896`, `1024x1024`). | 1152x896 |
| | `--cfg-scale` | Guidance scale (how strictly to follow prompt). | 7.0 |
| | `--sharpness` | Image sharpness filter strength. | 2.0 |
| | `--sampler` | Sampler method name. | dpmpp_2m_sde_gpu |
| | `--scheduler` | Scheduler name. | karras |
| **Models** | `--base-model` | Filename of the base checkpoint. | (Config Default) |
| | `--refiner-model` | Filename of the refiner checkpoint. | (Config Default) |
| | `--refiner-switch` | Step ratio to switch to refiner (0.0-1.0). | 0.5 |
| | `--lora` | Load LoRA: `filename:weight`. Use flag multiple times. | N/A |
| **Styles** | `--style` | Style name. Use flag multiple times. | (Fooocus Defaults) |

## 🤖 AI Agent Integration

If you want to teach an AI agent to use this tool, provide it with the following specification:

### Tool: `generate_image_fooocus`

**Description:** Generates images locally using Fooocus via CLI.
**Execution:** `d:\Fooocus_win64_2-5-0\fooocus-cli.bat`

**Parameters:**
*   `prompt`: String (Required)
*   `negative_prompt`: String
*   `output`: String (Filename)
*   `aspect_ratio`: String (e.g., "1024x1024")
*   `base_model`: String (Checkpoint filename)
*   `style`: List[String] (Style names)
*   `lora`: List[String] (Format "name:weight")
*   `steps`: Integer
*   `cfg_scale`: Float

**Notes:**
*   Output is saved relative to `d:\Fooocus_win64_2-5-0\Fooocus\` if a relative path is given in python, but the batch wrapper usually handles CWD. Absolute paths are recommended for the `--output` argument to ensure files are saved exactly where intended.

## Arabic/Text Image CLI

For posters, signs, ads, and Arabic text, use the dedicated text pipeline instead of asking SDXL to spell the text directly:

```powershell
.\arabic-poster-cli.bat ^
  --preset pro_text ^
  --arabic-text "مستقبل الذكاء الاصطناعي" ^
  --scene-prompt "premium technology poster" ^
  --subject "glass AI assistant device on a desk" ^
  --composition "centered product with clean negative space for headline" ^
  --lighting "soft studio lighting with realistic reflections" ^
  --brand-colors "deep blue, white, subtle cyan accents" ^
  --output "outputs\arabic_ai_poster.png"
```

Useful presets:

| Preset | Best for |
| :--- | :--- |
| `pro_text` | Nano Banana / Image-style blended poster text. Uses Quality, harmonization, CPDS text guide, export scaling, and one final crisp repaint to avoid duplicate text layers. |
| `clean_graphic` | Sharp brand graphics where exact text matters more than painted-in texture. |
| `neon_sign` | Glowing sign text integrated into a scene. |
| `balanced` | Manual control with conservative defaults. |

Extra controls:

| Argument | Description |
| :--- | :--- |
| `--prompt-profile nano_banana_pro` | Adds a structured, studio-quality prompt profile with stronger layout and text-zone wording. |
| `--subject`, `--composition`, `--location`, `--visual-style`, `--lighting`, `--camera` | Optional creative-brief fields that compile into a clearer scene prompt. |
| `--harmonize 0.25-0.45` | Low-denoise img2img blend; higher values integrate more but can deform letters. |
| `--final-text-pass 0.25-1.0` | Optional pre-export exact text repair. Do not combine it with the default `pro_text` crisp export repaint unless you intentionally want multiple text layers. |
| `--text-guide harmonize` | Uses a rendered text reference with CPDS ControlNet to preserve text structure during harmonization. |
| `--max-lines N` | Auto-wraps and shrinks Arabic text to fit within N lines. |
| `--no-wrap` | Disables automatic wrapping. |
| `--export-scale 2` or `--export-width 4096` | Exports a larger final image after generation; `pro_text` defaults to 2x with a crisp text repaint. |
| `--no-crisp-export-text` | Disables preset-enabled final crisp repaint if you want to use only `--final-text-pass`. |

The important limitation is still real: local SDXL/Fooocus cannot spell Arabic reliably inside the diffusion model itself. This CLI gets close to modern text-image systems by combining exact RTL rendering with controlled image harmonization.

If text appears doubled, use only one repair method. The default `pro_text` path now uses harmonization plus one final crisp repaint; avoid adding `--final-text-pass` unless you also pass `--no-crisp-export-text`.

## Discover Local Models, Styles, Presets, and Fonts

The CLIs can now expose the real assets installed on this machine.

```powershell
# List checkpoints, LoRAs, VAEs, ControlNets, presets, and styles
.\fooocus-cli.bat --list-models

# Same inventory from the Arabic poster CLI
.\arabic-poster-cli.bat --list-models

# List installed system fonts that can be passed to --font
.\arabic-poster-cli.bat --list-fonts

# Filter fonts
.\arabic-poster-cli.bat --list-fonts --font-filter arab

# Machine-readable output for agents/scripts
.\arabic-poster-cli.bat --list-inventory --inventory-json
```

Font usage:

```powershell
.\arabic-poster-cli.bat ^
  --preset clean_graphic ^
  --arabic-text "القهوة سر الصباح" ^
  --scene-prompt "premium coffee product advertisement" ^
  --font "arial" ^
  --output "outputs\coffee_arabic.png"
```

`--font` accepts a full `.ttf/.otf/.ttc` path or an exposed font alias such as `arial`, `tahoma`, `segoeui`, `arabtype`, or any alias shown by `--list-fonts`.

Model usage:

```powershell
.\arabic-poster-cli.bat ^
  --preset pro_text ^
  --base-model "juggernautXL_v8Rundiffusion.safetensors" ^
  --arabic-text "عرض خاص" ^
  --scene-prompt "premium product advertisement" ^
  --subject "luxury perfume bottle" ^
  --composition "centered product, empty space for headline" ^
  --font "tahoma" ^
  --output "outputs\perfume_offer.png"
```

Good starting model choices visible in this install include:

| Goal | Try |
| :--- | :--- |
| General SDXL quality | `juggernautXL_v8Rundiffusion.safetensors` |
| Realistic products/people | `RealVisXL_V5.0_fp16.safetensors`, `realvisxlV50_v50Bakedvae.safetensors`, `epicrealismXL_vxiAbeast.safetensors` |
| Stock/ad style | `realisticStockPhoto_v20.safetensors` |
| Inpaint workflows | `juggernautxl_inpaint.safetensors`, `dreamshaperXL_lightningInpaint.safetensors` |

Fast local smoke tests:

```powershell
.\python_embeded\python.exe -s -m py_compile arabic_poster_pipeline.py arabic_text_renderer.py fooocus_cli_direct.py fooocus_cli_inventory.py test_cli_inventory.py
.\python_embeded\python.exe -s test_cli_inventory.py
```

Dry-run combinations before spending GPU time:

```powershell
.\arabic-poster-cli.bat ^
  --dry-run ^
  --preset pro_text ^
  --base-model "RealVisXL_V5.0_fp16" ^
  --font "decotype naskh" ^
  --arabic-text "تصميم فاخر" ^
  --scene-prompt "luxury perfume campaign" ^
  --subject "crystal perfume bottle" ^
  --composition "centered product with headline space"

.\fooocus-cli.bat ^
  --dry-run ^
  --prompt "premium product advertisement, no text" ^
  --base-model "juggernautXL_v8Rundiffusion" ^
  --styles "Fooocus V2" "Fooocus Enhance"
```
