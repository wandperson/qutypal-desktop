# Basic
from typing import Optional
from dataclasses import dataclass, field



@dataclass
class AppSettings:
    companion_run_on_launch: bool = True
    language: str = 'en'

app_settings = AppSettings()