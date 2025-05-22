from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class VariantLoader:
    def __init__(self, user_template_dir: Optional[Path], builtin_template_dir: Path):
        self.user_dir = user_template_dir
        self.builtin_dir = builtin_template_dir

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def resolve_variant(self, name: str) -> Dict[str, Any]:
        variant_path = self._variant_path(name)
        if not variant_path.exists():
            raise FileNotFoundError(f"Variant '{name}' not found at {variant_path}")

        variant = self._load_yaml(variant_path)

        if "extends" in variant:
            base = self.resolve_variant(variant["extends"])
            merged = {
                "name": variant.get("name", base.get("name", name)),
                "components": variant.get("components", base.get("components", [])),
            }
            return merged

        return variant

    def _variant_path(self, name: str) -> Path:
        root = (
            self.user_dir
            if self.user_dir and (self.user_dir / "challenge/variants").exists()
            else self.builtin_dir
        )
        return root / "challenge/variants" / f"{name}.yaml"
