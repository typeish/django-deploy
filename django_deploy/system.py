from __future__ import with_statement
from fabric.api import cd, run, sudo
from fabric.colors import yellow
from fabric.contrib.files import contains


def start_webserver():
    run("/etc/init.d/apache2 start")

def stop_webserver():
    run("/etc/init.d/apache2 stop")

def restart_webserver():
    run("/etc/init.d/apache2 stop")
    run("/etc/init.d/apache2 start")

def reload_webserver():
    run("/etc/init.d/apache2 reload")

def setup_server():
    "Set up a server for the first time in preparation for deployments."
    upgrade_packages()
    # Install required system packages for deployment, plus some extras
    apt_packages = ['apache2', 'python-psycopg2', 'python-setuptools',
        'postgresql', 'postgresql-contrib', 'libapache2-mod-wsgi', 'git-core',
        'subversion', 'python-imaging', 'postgresql-server-dev-8.4',
        'build-essential', 'binutils', 'libxml2-dev', 'screen', 'memcached',
        'mercurial', 'proj', ]
    run("apt-get install -y %s" % " ".join(apt_packages))
    # Install pip, and use it to install virtualenv and virtualenvwrapper
    run("easy_install -U pip")
    run("pip install -U virtualenv virtualenvwrapper")
    setup_virtualenvwrapper()
    upgrade_packages()

def setup_virtualenvwrapper():
    "Set up virtualenvwrapper in .bashrc"
    virtualenvwrapper_settings = """
# virtualenvwrapper settings
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=/srv/virtualenvs
"""
    if not contains("export WORKON_HOME", "~/.profile"):
        run("mkdir -p /srv/virtualenvs")
        append("~/.profile", virtualenvwrapper_settings)
    else:
        print(yellow("'export WORKON_HOME' is already present in ~./profile : skipping virtualenvwrapper setup."))

def upgrade_packages():
    "Bring all the installed packages up to date."
    run("apt-get update -y")
    run("apt-get upgrade -y")

def geodjango_setup():
    "Set up everything the server needs to support projects running GeoDjango."
    run("mkdir ~/pkgs")
    with cd("~/pkgs"):
        # http://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#ibex
        # Download and install some more stuff for proj (from the Django documentation)
        run("wget http://download.osgeo.org/proj/proj-datumgrid-1.4.tar.gz")
        run("mkdir nad")
        with cd("nad"):
            run("tar xzf ../proj-datumgrid-1.4.tar.gz")
            run("nad2bin null < null.lla")
            run("cp null /usr/share/proj")
        # Download and install the latest GEOS package (http://trac.osgeo.org/geos/).
        # Ubuntu provides a version that is too old for our purposes.
        run("wget http://download.osgeo.org/geos/geos-3.2.2.tar.bz2")
        run("tar xvjf geos-3.2.2.tar.bz2")
        with cd("geos-3.2.2"):
            run("./configure")
            run("make && make install")
        # Download and install the latest PostGIS package
        run("wget http://postgis.refractions.net/download/postgis-1.5.1.tar.gz")
        run("tar xvzf postgis-1.5.1.tar.gz")
        with cd("postgis-1.5.1"):
            run("./configure")
            run("make && make install")
    # Make sure PostGIS can find GEOS
    run("ldconfig")

# TODO: Need to get the GeoDjango database stuff working...
def postgis_database():
    # Create the database with the proper encoding (Ubuntu 10.04 defaults to ASCII encoding for some reason)
    # sudo("psql -c \"CREATE DATABASE template_postgis WITH ENCODING = 'UTF-8' TEMPLATE template0;\"", user="postgres")
    # Set up the template database (from the Django documentation)
    env.shell = "/bin/bash -c"
    with sudo("POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5", user="postgres"):
        sudo("createlang -d template_postgis plpgsql # Adding PLPGSQL language support.", user="postgres")
        sudo("psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\"", user="postgres")
        sudo("psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql # Loading the PostGIS SQL routines", user="postgres")
        sudo("psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql", user="postgres")
        sudo("psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\" # Enabling users to alter spatial tables.", user="postgres")
        sudo("psql -d template_postgis -c \"GRANT ALL ON geography_columns TO PUBLIC;\"", user="postgres")
        sudo("psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\"", user="postgres")
    env.shell = "/bin/bash -l -c"
