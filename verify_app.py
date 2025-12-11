import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_calendar.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from calendar_app.models import Event, Branding, Team

User = get_user_model()

def verify():
    print("Verifying setup...")
    
    # 1. Create Superuser (if not exists)
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        # Also set role to admin as per our model
        u = User.objects.get(username='admin')
        u.role = 'admin'
        u.save()
        print("Created superuser: admin / admin")
    else:
        print("Superuser 'admin' already exists.")

    # 2. Check Branding
    if not Branding.objects.exists():
        Branding.objects.create(primary_color='#00ff9d')
        print("Created default branding.")
        
    # 3. Create Sample Event
    if not Event.objects.exists():
        from django.utils import timezone
        Event.objects.create(
            title="TEST MATCH",
            event_type='match',
            start_time=timezone.now(),
            location="Server 1"
        )
        print("Created sample event.")

    # 4. Test Client
    c = Client()
    
    # Login page
    resp = c.get('/login/')
    print(f"Login Page Status: {resp.status_code}")
    
    # Signup page
    resp = c.get('/signup/')
    print(f"Signup Page Status: {resp.status_code}")
    if resp.status_code != 200:
        print("ERROR: Signup page failed!")
    
    # Dashboard (redirect if not logged in)
    resp = c.get('/')
    print(f"Dashboard (Unauth) Status: {resp.status_code} (Should be 302)")
    
    # Login
    login_resp = c.post('/login/', {'username': 'admin', 'password': 'admin'})
    print(f"Login Attempt Status: {login_resp.status_code} (Should be 302 to dashboard)")
    
    # Dashboard (Auth)
    resp = c.get('/', follow=True)
    print(f"Dashboard (Auth) Status: {resp.status_code}")
    if "TEST MATCH" in str(resp.content):
        print("SUCCESS: Sample event found on dashboard.")
    else:
        print("WARNING: Sample event NOT found on dashboard.")

    # Calendar Navigation
    resp = c.get('/', {'year': 2026, 'month': 1}, follow=True)
    print(f"Calendar Navigation Status: {resp.status_code}")
    if "January 2026" in str(resp.content):
        print("SUCCESS: Calendar navigation working (found 'January 2026').")
    else:
        print("WARNING: Calendar navigation text not found.")

    # Check for Logo
    if '/media/branding/logo.jpg' in str(resp.content):
        print("SUCCESS: Logo image found in response.")
    else:
        print("WARNING: Logo image NOT found in response.")

if __name__ == '__main__':
    verify()
