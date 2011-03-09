from __future__ import with_statement
from django_deploy.utils import script
from fabric.api import cd, run, sudo
from fabric.colors import yellow
from fabric.contrib.files import append, contains
from fabric.operations import put


def start_webserver():
    run("/etc/init.d/apache2 start")

def stop_webserver():
    run("/etc/init.d/apache2 stop")

def restart_webserver():
    run("/etc/init.d/apache2 restart")

def reload_webserver():
    run("/etc/init.d/apache2 reload")

def setup_server():
    "Set up a server for the first time in preparation for deployments."
    upgrade_packages()
    # Install required system packages for deployment, plus some extras
    apt_packages = ["apache2", "python-psycopg2", "python-setuptools",
        "postgresql", "postgresql-contrib", "libapache2-mod-wsgi", "git-core",
        "subversion", "python-imaging", "postgresql-server-dev-8.4",
        "build-essential", "binutils", "libxml2-dev", "screen", "memcached",
        "mercurial", ]
    install_packages(apt_packages)
    # Install pip, and use it to install virtualenv and virtualenvwrapper
    sudo("easy_install -U pip")
    sudo("pip install -U virtualenv virtualenvwrapper")
    setup_virtualenvwrapper()
    upgrade_packages()

def setup_virtualenvwrapper(profile="~/.profile"):
    "Set up virtualenvwrapper in the appropriate profile"
    virtualenvwrapper_settings = """
# virtualenvwrapper settings
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=/srv/virtualenvs
"""
    if not contains(profile, "export WORKON_HOME"):
        sudo("mkdir -p /srv/virtualenvs")
        append(profile, virtualenvwrapper_settings)
    else:
        print(yellow("'export WORKON_HOME' is already present in ~./profile : skipping virtualenvwrapper setup."))

def install_packages(packages):
    "Install packages, given a list of package names"
    sudo("apt-get install -y %s" % " ".join(packages))

def upgrade_packages():
    "Bring all the installed packages up to date"
    sudo("apt-get update -y")
    sudo("apt-get upgrade -y")

# TODO: A lot about this could be more robust...but it works!
def setup_geodjango():
    "Set up everything the server needs to support projects running GeoDjango"
    install_packages(["proj", ])
    run("mkdir -p ~/pkgs")
    with cd("~/pkgs"):
        # http://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#ibex
        # Download and install some more stuff for proj (from the Django documentation)
        run("wget http://download.osgeo.org/proj/proj-datumgrid-1.4.tar.gz")
        run("mkdir -p nad")
        with cd("nad"):
            run("tar xzf ../proj-datumgrid-1.4.tar.gz")
            run("nad2bin null < null.lla")
            sudo("cp null /usr/share/proj")
        # Download and install the latest GEOS package (http://trac.osgeo.org/geos/).
        # Ubuntu provides a version that is too old for our purposes.
        run("wget http://download.osgeo.org/geos/geos-3.2.2.tar.bz2")
        run("tar xvjf geos-3.2.2.tar.bz2")
        with cd("geos-3.2.2"):
            run("./configure")
            sudo("make && make install")
        # Download and install the latest PostGIS package
        run("wget http://postgis.refractions.net/download/postgis-1.5.2.tar.gz")
        run("tar xvzf postgis-1.5.2.tar.gz")
        with cd("postgis-1.5.2"):
            run("./configure")
            sudo("make && make install")
        # Download and install GDAL
        run("wget http://download.osgeo.org/gdal/gdal-1.7.3.tar.gz")
        run("tar xzf gdal-1.7.3.tar.gz")
        with cd("gdal-1.7.3"):
            run("./configure")
            sudo("make && make install")
    # Make sure PostGIS can find GEOS
    sudo("ldconfig")
    # Set up template_postgis database
    with cd("/var/lib/postgresql"):
        put(script("create_template_postgis-1.5.sh"), ".", mode="0755")
        sudo("./create_template_postgis-1.5.sh", user="postgres")
