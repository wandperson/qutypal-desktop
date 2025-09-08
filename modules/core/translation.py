# Basic
import sys

# Locallization
import gettext

# Custom modules
from modules.settings import app_settings


LANG_CODE = app_settings.language



try:
    translator = gettext.translation('messages', localedir='locales', languages=[LANG_CODE])
    lang_ = translator.gettext
    #translator.install()
except FileNotFoundError as e:
    print(f"Translation file not found for {LANG_CODE}: {e}")
    sys.exit(1)