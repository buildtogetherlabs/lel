"""Shared project paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
LAYERS_RAW = ROOT / "layers_raw" / "wojak_pfp_project"
LAYERS_NORM = ROOT / "layers_normalized"
MANIFESTS = ROOT / "manifests"
OUTPUT = ROOT / "output"
IMAGES = OUTPUT / "images"
METADATA = OUTPUT / "metadata"
PREVIEWS = OUTPUT / "previews"
REPORTS = ROOT / "reports"
