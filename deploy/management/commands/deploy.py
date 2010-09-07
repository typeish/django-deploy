from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    A command that pulls setting from the project's settings file and deploys
    accordingly. It expects a DEPLOYS dictionary to be defined with at least a
    "default" dictionary within it, similar to DATABASES in Django 1.2+. E.g.:
    
    DEPLOYS = {
        "default": {
            "DOMAIN": "example.com",
            "HOST": "12.34.56.78",
            "NAME": "example_project",
            "USER": "root",
            "PASSWORD": "",
            "BRANCH": "",
        }
    }
    """
    
    def handle(self, *args, **kwargs):
        def get_required_val(dictionary, key, err_msg):
            value = dictionary.get(key, None)
            if value:
                return value
            else:
                raise CommandError(err_msg)
        
        deploys = getattr(settings, 'DEPLOYS', None)
        if not deploys:
            raise CommandError("DEPLOYS has not been defined in your project's settings.py file.")
        
        default = get_required_val(deploys, 'default','A "default" deployment has not been defined in your project\'s settings file.')
        
        domain = get_required_val(default, 'DOMAIN', "DOMAIN must be defined for your default deployment.")
        host = get_required_val(default, 'HOST', "HOST must be defined for your default deployment.")
        name = get_required_val(default, 'NAME', "NAME must be defined for your default deployment.")
        user = get_required_val(default, 'USER', "USER must be defined for your default deployment.")
        
        password = default.get('PASSWORD', None)
        branch = default.get('BRANCH', 'master')
        
