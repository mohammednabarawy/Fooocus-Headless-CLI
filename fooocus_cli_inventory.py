"""Local inventory helpers for Fooocus CLI wrappers.

This module intentionally avoids importing Fooocus internals so listing models,
styles, presets, and system fonts stays fast and does not load GPU libraries.
"""

import argparse
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
FOOOCUS_ROOT = PROJECT_ROOT / "Fooocus"
MODELS_ROOT = FOOOCUS_ROOT / "models"

MODEL_EXTENSIONS = {".safetensors", ".ckpt", ".pt", ".pth", ".bin"}
FONT_EXTENSIONS = {".ttf", ".otf", ".ttc"}

MODEL_CATEGORIES = {
    "checkpoints": "checkpoints",
    "loras": "loras",
    "vae": "vae",
    "controlnet": "controlnet",
    "upscale_models": "upscale_models",
    "clip": "clip",
    "clip_vision": "clip_vision",
    "embeddings": "embeddings",
    "inpaint": "inpaint",
}

FONT_STYLE_ALIASES = {
    "default": ["arial", "segoeui", "tahoma"],
    "naskh": ["dtnaskh0", "dtnaskh1", "dtnaskh2", "arabtype", "arial"],
    "arabic": ["arabtype", "arabsq", "dtnaskh0", "arial"],
}

LIKELY_ARABIC_FONT_HINTS = (
    "arab",
    "naskh",
    "kufi",
    "urdu",
    "persian",
    "amiri",
    "scheherazade",
    "tahoma",
    "arial",
    "segoeui",
    "trado",
)


def _file_info(path, root):
    stat = path.stat()
    rel = path.relative_to(root).as_posix()
    return {
        "name": path.name,
        "stem": path.stem,
        "relative_path": rel,
        "path": str(path),
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
    }


def _scan_files(root, extensions):
    if not root.exists():
        return []
    results = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            results.append(_file_info(path, root))
    return sorted(results, key=lambda item: item["relative_path"].lower())


def list_model_inventory():
    categories = {}
    for label, folder in MODEL_CATEGORIES.items():
        categories[label] = _scan_files(MODELS_ROOT / folder, MODEL_EXTENSIONS)

    presets = []
    presets_root = FOOOCUS_ROOT / "presets"
    if presets_root.exists():
        presets = sorted(path.stem for path in presets_root.glob("*.json"))

    styles = []
    styles_root = FOOOCUS_ROOT / "sdxl_styles"
    if styles_root.exists():
        for style_file in sorted(styles_root.glob("*.json")):
            try:
                data = json.loads(style_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("name"):
                        styles.append(item["name"])
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and value.get("name"):
                        styles.append(value["name"])
                    else:
                        styles.append(key)

    return {
        "models_root": str(MODELS_ROOT),
        "categories": categories,
        "presets": presets,
        "styles": sorted(set(styles), key=str.lower),
    }


def list_system_fonts(font_filter=None):
    font_roots = []
    windir = os.environ.get("WINDIR", r"C:\Windows")
    font_roots.append(Path(windir) / "Fonts")
    local_fonts = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts"
    font_roots.append(local_fonts)

    seen = set()
    fonts = []
    for root in font_roots:
        if not root.exists():
            continue
        for path in root.iterdir():
            if not path.is_file() or path.suffix.lower() not in FONT_EXTENSIONS:
                continue
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            alias = path.stem.lower()
            item = {
                "alias": alias,
                "name": path.name,
                "path": str(path),
                "extension": path.suffix.lower(),
                "likely_arabic": any(hint in alias for hint in LIKELY_ARABIC_FONT_HINTS),
            }
            fonts.append(item)

    fonts = sorted(fonts, key=lambda item: (not item["likely_arabic"], item["alias"]))
    if font_filter:
        f = font_filter.lower()
        fonts = [
            item for item in fonts
            if f in item["alias"] or f in item["name"].lower() or f in item["path"].lower()
        ]
    return fonts


def resolve_font_identifier(identifier):
    """Resolve a font path or exposed alias/stem to an installed font path."""
    if not identifier:
        return None
    expanded = os.path.expandvars(os.path.expanduser(identifier))
    if os.path.exists(expanded):
        return expanded

    normalized = identifier.lower().strip()
    normalized_stem = Path(normalized).stem
    for font in list_system_fonts():
        candidates = {
            font["alias"],
            font["name"].lower(),
            Path(font["name"]).stem.lower(),
        }
        if normalized in candidates or normalized_stem in candidates:
            return font["path"]
    return identifier


def resolve_model_name(category, model_name):
    """Resolve a model filename/stem/relative path inside an inventory category."""
    if not model_name:
        return None
    inventory = list_model_inventory()
    models = inventory["categories"].get(category, [])
    normalized = model_name.lower().strip()
    normalized_stem = Path(normalized).stem
    for model in models:
        candidates = {
            model["name"].lower(),
            model["stem"].lower(),
            model["relative_path"].lower(),
        }
        if normalized in candidates or normalized_stem in candidates:
            return model
    return None


def find_font_for_style(style="default", custom_path=None):
    resolved = resolve_font_identifier(custom_path)
    if resolved and os.path.exists(resolved):
        return resolved

    fonts = list_system_fonts()
    by_alias = {font["alias"]: font["path"] for font in fonts}
    for alias in FONT_STYLE_ALIASES.get(style, []):
        if alias in by_alias:
            return by_alias[alias]

    for font in fonts:
        if font["likely_arabic"]:
            return font["path"]
    if fonts:
        return fonts[0]["path"]
    raise FileNotFoundError("No usable system font found.")


def print_model_inventory(as_json=False, limit=None):
    inventory = list_model_inventory()
    if as_json:
        print(json.dumps(inventory, ensure_ascii=False, indent=2))
        return

    print(f"Models root: {inventory['models_root']}")
    for category, items in inventory["categories"].items():
        shown = items[:limit] if limit else items
        print(f"\n[{category}] {len(items)} file(s)")
        for item in shown:
            print(f"  {item['name']}  ({item['size_mb']} MB)")
        if limit and len(items) > limit:
            print(f"  ... {len(items) - limit} more")

    print(f"\n[presets] {len(inventory['presets'])}")
    for item in inventory["presets"]:
        print(f"  {item}")

    print(f"\n[styles] {len(inventory['styles'])}")
    for item in inventory["styles"][:limit or len(inventory["styles"])]:
        print(f"  {item}")
    if limit and len(inventory["styles"]) > limit:
        print(f"  ... {len(inventory['styles']) - limit} more")


def print_font_inventory(as_json=False, font_filter=None, limit=None):
    fonts = list_system_fonts(font_filter=font_filter)
    if as_json:
        print(json.dumps(fonts, ensure_ascii=False, indent=2))
        return

    print(f"System fonts: {len(fonts)}")
    shown = fonts[:limit] if limit else fonts
    for font in shown:
        marker = " Arabic-ready" if font["likely_arabic"] else ""
        print(f"  {font['alias']} -> {font['path']}{marker}")
    if limit and len(fonts) > limit:
        print(f"  ... {len(fonts) - limit} more")


def add_inventory_arguments(parser):
    parser.add_argument("--list-models", action="store_true",
                        help="List local Fooocus checkpoints, LoRAs, VAEs, ControlNets, presets, and styles")
    parser.add_argument("--list-fonts", action="store_true",
                        help="List installed system fonts usable with --font")
    parser.add_argument("--list-inventory", action="store_true",
                        help="List both local models/styles and system fonts")
    parser.add_argument("--font-filter", default=None,
                        help="Filter --list-fonts output by alias, filename, or path")
    parser.add_argument("--inventory-json", action="store_true",
                        help="Print inventory as JSON")
    parser.add_argument("--inventory-limit", type=int, default=None,
                        help="Limit displayed inventory items per section")


def handle_inventory_arguments(args):
    if not (args.list_models or args.list_fonts or args.list_inventory):
        return False

    if args.inventory_json:
        payload = {}
        if args.list_models or args.list_inventory:
            payload["models"] = list_model_inventory()
        if args.list_fonts or args.list_inventory:
            payload["fonts"] = list_system_fonts(font_filter=args.font_filter)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return True

    if args.list_models or args.list_inventory:
        print_model_inventory(as_json=False, limit=args.inventory_limit)
    if args.list_fonts or args.list_inventory:
        if args.list_models or args.list_inventory:
            print()
        print_font_inventory(as_json=False, font_filter=args.font_filter, limit=args.inventory_limit)
    return True
