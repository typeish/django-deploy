# django.wsgi is configured to live in %(project_name)s/deploy.

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

# Avoid having stray print statements cause 500 errors
sys.stdout = sys.stderr

sys.path.insert(0, abspath(join(dirname(__file__), "..", "..")))
sys.path.insert(0, abspath(join(dirname(__file__), "..")))
sys.path.insert(0, abspath(join(dirname(__file__), "..", "apps")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "%(project_name)s.settings"

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
