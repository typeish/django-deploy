from django.core.management.base import BaseCommand, CommandError
from django_deploy.project import deploy_project
from django_deploy.utils import fab_task

class Command(BaseCommand):
    
    @fab_task
    def handle(self, *args, **kwargs):
        deploy_project()
