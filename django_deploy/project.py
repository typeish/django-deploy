from __future__ import with_statement
from django_deploy.system import reload_webserver
from django_deploy.utils import manage, template
from fabric.api import cd, env, local, run, sudo
from fabric.contrib.files import exists, upload_template
from fabric.operations import put


def collect_static_media():
    "Collect the static media for the project."
    # Purge the old before building the new
    sudo("rm -rf %(deploy_root)s/site_media/static/*" % env)
    manage("collectstatic --noinput")
    sudo("chown -R www-data %(deploy_root)s/site_media" % env)

def createsuperuser():
    username = raw_input("Enter name for new super user: ")
    manage("createsuperuser %s" % username)

def deploy_project():
    "Deploy the project."
    if not exists(env.deploy_root):
        # Create project's directory structure
        sudo("mkdir -p %(deploy_root)s" % env)
        with cd(env.deploy_root):
            sudo("mkdir -p conf db logs site_media/static site_media/media")
        # Set permissions
        # TODO: Need to make sure this user exists before assigning them permissions
        # This is so that a user can install things to their virtualenv without sudo
        # It isn't needed yet, so leaving it out for now.
        #sudo("chown -R %(project_name)s:%(project_name)s /srv/virtualenvs/%(project_name)s" % env)
        sudo("chown -R www-data %(deploy_root)s/db" % env)
        sudo("chown -R www-data %(deploy_root)s/site_media" % env)
    if not exists(env.virtualenv_dir):
        sudo("mkvirtualenv %(project_name)s" % env)
    if not exists("/etc/apache2/sites-available/%(project_name)s" % env):
        upload_apache_config()
    disable_project()
    upload_project()
    disable_debug()
    install_project_requirements()
    collect_static_media()
    sync_and_migrate()
    enable_project()

def disable_debug():
    with cd(env.project_root):
        sudo("sed -i.bak -r -e 's/^[ \\t]*DEBUG[ \\t]*=[ \\t]*True[ \\t]*$/DEBUG = False/g' settings.py")

def enable_debug():
    with cd(env.project_root):
        sudo("sed -i.bak -r -e 's/^[ \\t]*DEBUG[ \\t]*=[ \\t]*False[ \\t]*$/DEBUG = True/g' settings.py")

def disable_project():
    "Disable the site in Apache."
    if exists("/etc/apache2/sites-available/%(project_name)s" % env):
        sudo("a2dissite %(project_name)s" % env)
        reload_webserver()

def enable_project():
    "Enable the site in Apache."
    if exists("/etc/apache2/sites-available/%(project_name)s" % env):
        sudo("a2ensite %(project_name)s" % env)
        reload_webserver()

def install_project_requirements():
    "Install everything in requirements.txt to the project's virtualenv."
    # Make sure we don't have existing source checkouts in the virtualenv
    # They tend to cause upgrades to fail, which is annoying
    if exists("%(virtualenv_dir)s/src" % env):
        sudo("rm -rf %(virtualenv_dir)s/src" % env)
    if exists("%(virtualenv_dir)s/build" % env):
        sudo("rm -rf %(virtualenv_dir)s/build" % env)
    with cd(env.project_root):
        sudo("workon %(project_name)s && pip install -U -r requirements.txt" % env)

def remove_project():
    "Totally remove a deployed project from the server."
    disable_project()
    # Remove Apache config, project directory, and virtualenv
    # TODO: These should have proper permissions and NOT need to run as sudo
    if exists("/etc/apache2/sites-available/%(project_name)s" % env):
        sudo("rm /etc/apache2/sites-available/%(project_name)s" % env)
    if exists(env.deploy_root):
        sudo("rm -rf %(deploy_root)s" % env)
    if exists(env.virtualenv_dir):
        sudo("rmvirtualenv %(project_name)s" % env)

def sync_and_migrate():
    """
    Runs Django's syncdb management command (without taking user input)
    and then 
    """
    manage("syncdb --noinput")
    if env.uses_south:
        manage("migrate")

def upload_apache_config():
    "Upload a customized apache configuration to the server."
    # This is used to render the apache config template
    env.project_site_packages = sudo('workon %(project_name)s && python -c "from distutils.sysconfig import get_python_lib; print get_python_lib();"' % env)
    upload_template(template("apache.conf"), "/etc/apache2/sites-available/%(project_name)s" % env, context=env, use_sudo=True)

def upload_project():
    "Uploads the entire project to the server."
    run("mkdir -p %(project_root)s" % env)
    # Package the appropriate branch, move it to the server, and clean up
    local("git archive --format=tar %(project_branch)s | gzip > project.tar.gz" % env)
    put("project.tar.gz", "%(project_root)s" % env, use_sudo=True)
    local("rm project.tar.gz")
    # Unpackage the code and clean up
    with cd(env.project_root):
        sudo("tar zxf project.tar.gz")
        sudo("rm project.tar.gz")
