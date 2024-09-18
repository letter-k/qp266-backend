import os

from config.logging.logging_settings import LOGGING_SETTINGS
from config.settings.base import *  # noqa: F403

# logging settings
LOGGING = LOGGING_SETTINGS

# Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405
# Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
# and renames the files with unique names for each version to support long-term caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
