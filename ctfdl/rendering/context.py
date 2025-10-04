from pathlib import Path

from ctfdl.rendering.engine import TemplateEngine


class TemplateEngineContext:
    _instance: TemplateEngine | None = None

    @classmethod
    def initialize(cls, user_template_dir: Path | None, builtin_template_dir: Path):
        if cls._instance is None:
            cls._instance = TemplateEngine(user_template_dir, builtin_template_dir)

    @classmethod
    def get(cls) -> TemplateEngine:
        if cls._instance is None:
            raise RuntimeError("TemplateEngineContext not initialized.")
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
