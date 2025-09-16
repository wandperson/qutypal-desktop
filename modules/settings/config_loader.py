from pathlib import Path
from dataclasses import dataclass, fields
import tomllib



def load_config(cls: dataclass, path: Path) -> dataclass:
    if not path.exists():
        print(f"Config file {path} not found, using defaults.")
        return cls()

    with path.open("rb") as f:
        data = tomllib.load(f)

    defaults = cls()

    kwargs = {}
    for field in fields(cls):
        key = field.name
        kwargs[key] = data.get(key, getattr(defaults, key))

    return cls(**kwargs)