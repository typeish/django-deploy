from __future__ import with_statement
from django_deploy.system import *
from django_deploy.utils import manage, template
from fabric.api import cd, env, local, run
from fabric.contrib.files import append, sed, upload_template
from fabric.operations import put


def build_static_media():
    "Build the static media for the project."
    # Purge the old before building the new
    run("rm -rf /srv/www/%(project_name)s/site_media/static/*" % env)
    manage("build_static --noinput")

def createsuperuser():
    username = raw_input("Enter name for new super user: ")
    manage("createsuperuser %s" % username)

def deploy_project():
    "Deploy the project. Requires that the project has been set up first."
    upload_project()
    install_project_requirements()
    build_static_media()
    manage("syncdb --noinput")
    enable_project()

def disable_project():
    "Disable the site in Apache."
    run("a2dissite %(project_name)s" % env)
    reload_webserver()

def enable_project():
    "Enable the site in Apache."
    run("a2dissite %(project_name)s" % env)
    reload_webserver()

def install_project_requirements():
    "Install everything in requirements.txt to the project's virtualenv."
    with cd("/srv/www/%(project_name)s/%(project_name)s" % env):
        run("workon %(project_name)s && pip install -U -r requirements.txt" % env)

def redeploy_project():
    "Delete project code directory and redeploy. Data and logs remain intact."
    disable_project()
    run("rm -rf /srv/www/%(project_name)s/%(project_name)s/*" % env)
    deploy_project()

def remove_project():
    "Totally remove a deployed project from the server."
    disable_project()
    # Remove Apache config, project directory, and virtualenv
    run("rm /etc/apache2/sites-available/%(project_name)s" % env)
    run("rm -rf /srv/www/%(project_name)s" % env)
    run("rmvirtualenv %(project_name)s" % env)

def setup_project():
    "Deploy a project for the first time."
    # TODO: Check that it is safe to run the setup
    run("mkvirtualenv --no-site-packages %(project_name)s" % env)
    # Create project's directory structure
    run("mkdir -p /srv/www/%(project_name)s/%(project_name)s" % env)
    with cd("/srv/www/%(project_name)s" % env):
        run("mkdir -p conf db logs site_media/static site_media/media")
    # Set Apache permissions
    run("chown www-data /srv/www/%(project_name)s/db" % env)
    run("chown -R www-data /srv/www/%(project_name)s/site_media" % env)
    upload_apache_config()

def upload_apache_config():
    "Upload a customized apache configuration to the server."
    env.project_site_packages = run('workon %(project_name)s && python -c "from distutils.sysconfig import get_python_lib; print get_python_lib();"' % env)
    upload_template(template("apache.conf"), "/etc/apache2/sites-available/%(project_name)s" % env, context=env)

def upload_project():
    "Uploads the entire project to the server."
    # Make sure the project directory exists
    run("mkdir -p /srv/www/%(project_name)s/%(project_name)s" % env)
    # Package the appropriate branch, move it to the server, then clean up
    local("git archive --format=tar %(project_branch)s | gzip > project.tar.gz" % env)
    put("project.tar.gz", "/srv/www/%(project_name)s/%(project_name)s/project.tar.gz" % env)
    local("rm project.tar.gz")
    # Unpackage the code, then clean up
    with cd("/srv/www/%(project_name)s/%(project_name)s" % env):
        run("tar zxf project.tar.gz")
        run("rm project.tar.gz")
        # Turn debugging off
        #sed("setting.py", "DEBUG\w*=\w", "")
