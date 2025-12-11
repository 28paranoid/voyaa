import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_calendar.settings')
django.setup()

from calendar_app.models import Branding

def update_color():
    branding = Branding.objects.first()
    if not branding:
        branding = Branding.objects.create(primary_color='#c0705a')
    else:
        branding.primary_color = '#c0705a'
        branding.save()
    print(f"Branding updated. Primary Color: {branding.primary_color}")

if __name__ == '__main__':
    update_color()
