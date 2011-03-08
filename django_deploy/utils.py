from django.conf import settings
from django.core.management.base import CommandError
from fabric import state
from fabric.api import cd, env, run
from fabric.network import denormalize
import os.path, time


DJANGO_DEPLOY_ROOT = os.path.abspath(os.path.dirname(__file__))

PROJECTS_PATH = "/srv/www/"
VIRTUALENVS_PATH = "/srv/virtualenvs/"

def close_connections():
    for key in state.connections.keys():
        if state.output.status:
            print "Disconnecting from %s..." % denormalize(key),
        state.connections[key].close()
        del state.connections[key]
        if state.output.status:
            print "done."

def fab_task(func):
    def new_func(*args, **kwargs):
        setup_env()
        val = func(*args, **kwargs)
        close_connections()
        return val
    return new_func

def get_required_val(dictionary, key, err_msg):
    value = dictionary.get(key, None)
    if value:
        return value
    raise CommandError(err_msg)

def manage(command):
    with cd(env.project_root):
        run("workon %s && python manage.py %s" % (env.project_name, command))

def setup_env():
    deploys = getattr(settings, "DEPLOYS", None)
    if not deploys:
        raise CommandError("DEPLOYS has not been defined in your project's settings.py file.")

    default = get_required_val(deploys, "default", "A default deployment has not been defined in your project's settings file.")

    domain = get_required_val(default, "DOMAIN", "DOMAIN must be defined for your default deployment.")
    host = get_required_val(default, "HOST", "HOST must be defined for your default deployment.")
    name = get_required_val(default, "NAME", "NAME must be defined for your default deployment.")
    user = get_required_val(default, "USER", "USER must be defined for your default deployment.")

    password = default.get("PASSWORD", None)
    branch = default.get("BRANCH", None) or "master"

    # Essentials
    env.project_domain = domain
    env.hosts = [ host ]
    env.host_string = host
    env.project_name = name
    env.user = user
    env.password = password
    env.project_branch = branch
    env.deploy_time = run("python -c 'import time; print time.strftime(\"%Y-%m-%d-%H-%M\");'")
    # Helpers
    env.deploy_root = os.path.join(PROJECTS_PATH, env.project_name)
    env.project_root = os.path.join(PROJECTS_PATH, env.project_name, env.project_name)
    env.virtualenv_dir = os.path.join(VIRTUALENVS_PATH, env.project_name)

def script(file_path):
    return os.path.join(DJANGO_DEPLOY_ROOT,  "scripts", file_path)

def template(file_path):
    return os.path.join(DJANGO_DEPLOY_ROOT,  "templates", file_path)
