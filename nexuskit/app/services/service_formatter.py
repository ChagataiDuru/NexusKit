import json
import yaml

def format_text(text: str, format_type: str) -> str:
    if format_type == "json":
        try:
            data = json.loads(text)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    elif format_type == "yaml":
        try:
            data = yaml.safe_load(text)
            return yaml.dump(data, indent=2, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
    else:
        raise ValueError("Unsupported format type")
