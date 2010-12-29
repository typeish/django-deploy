from __future__ import with_statement
from django_deploy.system import reload_webserver
from django_deploy.utils import manage, template
from fabric.api import cd, env, local, run, sudo
from fabric.contrib.files import append, exists, upload_template
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
    "Deploy the project."
    if not exists("/srv/www/%(project_name)s" % env):
        # Create project's directory structure
        sudo("mkdir -p /srv/www/%(project_name)s" % env)
        with cd("/srv/www/%(project_name)s" % env):
            sudo("mkdir -p conf db logs releases site_media/static site_media/media")
        # Set permissions
        # TODO: Need to make sure this user exists before assigning them permissions
        # This is so that a user can install things to their virtualenv without sudo
        # It isn't needed yet, so leaving it out for now.
        #sudo("chown -R %(project_name)s:%(project_name)s /srv/virtualenvs/%(project_name)s" % env)
        sudo("chown -R www-data /srv/www/%(project_name)s/db" % env)
        sudo("chown -R www-data /srv/www/%(project_name)s/site_media" % env)
    if not exists("/srv/virtualenvs/%(project_name)s" % env):
        sudo("mkvirtualenv %(project_name)s" % env)
    if not exists("/etc/apache2/sites-available/%(project_name)s" % env):
        upload_apache_config()
    disable_project()
    upload_project()
    link_release()
    install_project_requirements()
    build_static_media()
    manage("syncdb --noinput")
    enable_project()

def disable_project():
    "Disable the site in Apache."
    if exists("/etc/apache2/sites-available/%(project_name)s" % env):
        sudo("a2dissite %(project_name)s" % env)
        reload_webserver()

def enable_project():
    "Enable the site in Apache."
    sudo("a2ensite %(project_name)s" % env)
    reload_webserver()

def install_project_requirements():
    "Install everything in requirements.txt to the project's virtualenv."
    # Make sure we don't have existing source checkouts in the virtualenv
    # They tend to cause upgrades to fail, which is annoying
    if exists("/srv/virtualenvs/%(project_name)s/src" % env):
        sudo("rm -rf /srv/virtualenvs/%(project_name)s/src" % env)
    with cd("/srv/www/%(project_name)s/%(project_name)s" % env):
        sudo("workon %(project_name)s && pip install -U -r requirements.txt" % env)

def link_release():
    "Remove previous symbolic link and create one to the new release"
    if exists("/srv/www/%(project_name)s/%(project_name)s" % env):
        sudo("rm /srv/www/%(project_name)s/%(project_name)s" % env)
    with cd("/srv/www/%(project_name)s/" % env):
        sudo("ln -s releases/%(deploy_time)s/ %(project_name)s" % env)

def remove_project():
    "Totally remove a deployed project from the server."
    disable_project()
    # Remove Apache config, project directory, and virtualenv
    # TODO: These should have proper permissions and NOT need to run as sudo
    if exists("/etc/apache2/sites-available/%(project_name)s" % env):
        sudo("rm /etc/apache2/sites-available/%(project_name)s" % env)
    if exists("/srv/www/%(project_name)s" % env):
        sudo("rm -rf /srv/www/%(project_name)s" % env)
    if exists("/srv/virtualenvs/%(project_name)s" % env):
        sudo("rmvirtualenv %(project_name)s" % env)

def upload_apache_config():
    "Upload a customized apache configuration to the server."
    # This is used to render the apache config template
    env.project_site_packages = sudo('workon %(project_name)s && python -c "from distutils.sysconfig import get_python_lib; print get_python_lib();"' % env)
    upload_template(template("apache.conf"), "/etc/apache2/sites-available/%(project_name)s" % env, context=env, use_sudo=True)

def upload_project():
    "Uploads the entire project to the server."
    # Create the release directory
    run("mkdir -p /srv/www/%(project_name)s/releases/%(deploy_time)s" % env)
    # Package the appropriate branch, move it to the server, then clean up
    local("git archive --format=tar %(project_branch)s | gzip > project.tar.gz" % env)
    # Upload to the home directory first, since we can't `sudo put`
    put("project.tar.gz", "~" % env)
    sudo("mv project.tar.gz /srv/www/%(project_name)s/releases/%(deploy_time)s/" % env)
    local("rm project.tar.gz")
    # Unpackage the code, then clean up
    with cd("/srv/www/%(project_name)s/releases/%(deploy_time)s" % env):
        sudo("tar zxf project.tar.gz")
        sudo("rm project.tar.gz")
        # Turn debugging off
        sudo("sed -i.bak -r -e 's/^[ \\t]*DEBUG[ \\t]*=[ \\t]*True[ \\t]*$/DEBUG = False/g' settings.py")
