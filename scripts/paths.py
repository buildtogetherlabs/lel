"""Shared project paths — clean production layout."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
TEMPLATE = ROOT / "template"

# Production layers (mint build)
LAYERS = ROOT / "layers"
LAYERS_BASE = LAYERS / "base"
LAYERS_TEMPLATE = LAYERS  # alias used by older script names

# Original trait art for redraw reference only
STYLE_REF = ROOT / "style_ref"
LAYERS_RAW = STYLE_REF  # alias

MANIFESTS = ROOT / "manifests"
OUTPUT = ROOT / "output"
IMAGES = OUTPUT / "images"
METADATA = OUTPUT / "metadata"
PREVIEWS = OUTPUT / "previews"
REPORTS = ROOT / "reports"
