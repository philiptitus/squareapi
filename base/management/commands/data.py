from django.core.management.base import BaseCommand
from base.models import Point

class Command(BaseCommand):
    help = 'Update types of all Point objects to General'

    def handle(self, *args, **kwargs):
        points = Point.objects.all()
        for point in points:
            point.types = 'General'
            point.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated all points to type General.'))
