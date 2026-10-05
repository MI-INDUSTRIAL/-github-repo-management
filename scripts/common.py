import re 
from pathlib import Path 
import yaml 
 
ALLOWED_VISIBILITY = {"private", "internal", "public"} 
REQUIRED_FIELDS = {"product", "purpose", "service", "description", "visibility"} 
 
def normalize(value: str) -> str: 
    value = value.strip().lower() 
    value = re.sub(r"[^a-z0-9-]", "-", value) 
    value = re.sub(r"-+", "-", value).strip("-") 
    return value 
 
def load_request(path: str) -> dict: 
    file_path = Path(path) 
    if file_path.suffix not in {".yml", ".yaml"}: 
        raise ValueError("Request must be a .yml or .yaml file") 
    data = yaml.safe_load(file_path.read_text(encoding="utf-8")) 
    if not isinstance(data, dict): 
        raise ValueError("Request YAML must contain a mapping") 
    missing = REQUIRED_FIELDS - set(data) 
    if missing: 
        raise ValueError(f"Missing fields: {', '.join(sorted(missing))}") 
    for key in REQUIRED_FIELDS: 
        if not isinstance(data[key], str) or not data[key].strip(): 
            raise ValueError(f"{key} must be a non-empty string") 
    data["visibility"] = data["visibility"].strip().lower() 
    if data["visibility"] not in ALLOWED_VISIBILITY: 
        raise ValueError("visibility must be private, internal, or public") 
    return data 
 
def repo_name(data: dict) -> str: 
    parts = [normalize(data[k]) for k in ("product", "purpose", "service")] 
    if any(not p for p in parts): 
        raise ValueError("product, purpose and service must contain valid characters") 
    return "-".join(parts)
