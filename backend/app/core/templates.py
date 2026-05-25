import os
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class FieldConfig(BaseModel):
    label: Optional[str] = None
    regex: Optional[str] = None
    required: bool = False
    options: Optional[list] = None

class TemplateConfig(BaseModel):
    template_name: str
    version: str
    region: str
    fields: Dict[str, FieldConfig]
    layout: Dict[str, Any]

class TemplateEngine:
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        self.templates: Dict[str, TemplateConfig] = {}
        self._load_templates()

    def _load_templates(self):
        if not os.path.exists(self.templates_dir):
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(self.templates_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = yaml.safe_load(f)
                        config = TemplateConfig(**data)
                        self.templates[config.template_name] = config
                    except Exception as e:
                        print(f"Error loading template {filename}: {e}")

    def get_template(self, name: str) -> Optional[TemplateConfig]:
        return self.templates.get(name)

    def list_templates(self):
        return list(self.templates.keys())

# Global instance
templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
engine = TemplateEngine(templates_path)
