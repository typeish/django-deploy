from __future__ import with_statement
from django_deploy.system import reload_webserver
from django_deploy.utils import manage, template
from fabric.api import cd, env, local, run, sudo
from fabric.contrib.files import append, upload_template
from fabric.operations import put


def build_static_media():
    "Build the static media for the project."
    # Purge the old before building the new
    sudo("rm -rf /srv/www/%(project_name)s/site_media/static/*" % env)
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
    sudo("a2dissite %(project_name)s" % env)
    reload_webserver()

def enable_project():
    "Enable the site in Apache."
    sudo("a2ensite %(project_name)s" % env)
    reload_webserver()

def install_project_requirements():
    "Install everything in requirements.txt to the project's virtualenv."
    with cd("/srv/www/%(project_name)s/%(project_name)s" % env):
        sudo("workon %(project_name)s && pip install -I -r requirements.txt" % env)

def redeploy_project():
    "Delete project code directory and redeploy. Data and logs remain intact."
    disable_project()
    sudo("rm -rf /srv/www/%(project_name)s/%(project_name)s/*" % env)
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
    sudo("mkvirtualenv --no-site-packages %(project_name)s" % env)
    # Create project's directory structure
    sudo("mkdir -p /srv/www/%(project_name)s/%(project_name)s" % env)
    with cd("/srv/www/%(project_name)s" % env):
        sudo("mkdir -p conf db logs site_media/static site_media/media")
    # Set permissions
    sudo("chown -R %(project_name)s:%(project_name)s /srv/virtualenvs/%(project_name)s" % env)
    sudo("chown -R www-data /srv/www/%(project_name)s/db" % env)
    sudo("chown -R www-data /srv/www/%(project_name)s/site_media" % env)
    # TODO: Any other permissions to set?
    upload_apache_config()

def upload_apache_config():
    "Upload a customized apache configuration to the server."
    env.project_site_packages = sudo('workon %(project_name)s && python -c "from distutils.sysconfig import get_python_lib; print get_python_lib();"' % env)
    upload_template(template("apache.conf"), "/etc/apache2/sites-available/%(project_name)s" % env, context=env, use_sudo=True)

def upload_project():
    "Uploads the entire project to the server."
    # Make sure the project directory exists
    run("mkdir -p /srv/www/%(project_name)s/%(project_name)s" % env)
    # Package the appropriate branch, move it to the server, then clean up
    local("git archive --format=tar %(project_branch)s | gzip > project.tar.gz" % env)
    put("project.tar.gz", "~" % env)
    sudo("mv project.tar.gz /srv/www/%(project_name)s/%(project_name)s/" % env)
    local("rm project.tar.gz")
    # Unpackage the code, then clean up
    with cd("/srv/www/%(project_name)s/%(project_name)s" % env):
        sudo("tar zxf project.tar.gz")
        sudo("rm project.tar.gz")
        # Turn debugging off
        sudo("sed -i.bak -r -e 's/^[ \\t]*DEBUG[ \\t]*=[ \\t]*True[ \\t]*$/DEBUG = False/g' settings.py")
