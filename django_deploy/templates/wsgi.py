# wsgi.py is configured to live in %(project_name)s/deploy.

from os.path import abspath, dirname, join
import os
import sys

# Avoid having stray print statements cause 500 errors
sys.stdout = sys.stderr

sys.path.insert(0, abspath(join(dirname(__file__), "..", "..")))
sys.path.insert(0, abspath(join(dirname(__file__), "..")))
sys.path.insert(0, abspath(join(dirname(__file__), "..", "apps")))

os.environ["DJANGO_SETTINGS_MODULE"] = "%(project_name)s.settings"

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
