from django.core.management.base import BaseCommand, CommandError
from django_deploy.project import redeploy_project
from django_deploy.utils import fab_task

class Command(BaseCommand):
    
    @fab_task
    def handle(self, *args, **kwargs):
        redeploy_project()
