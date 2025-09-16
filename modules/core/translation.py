# Basic
import sys

# Locallization
import gettext

# Custom modules
from modules.core import PathManager
from modules.settings import app_settings



try:
    translator = gettext.translation(
        domain='messages',
        localedir=PathManager.get_locales_dir(),
        languages=[app_settings.language]
    )
    lang_ = translator.gettext
    # translator.install()
except FileNotFoundError as e:
    print(f"Translation file not found for {app_settings.language}: {e}")
    sys.exit(1)