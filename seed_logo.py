import os
import shutil
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_calendar.settings')
django.setup()

from calendar_app.models import Branding

def seed_logo():
    # Source image path (User provided)
    source_path = r'C:/Users/chhet/.gemini/antigravity/brain/3b1783d6-b881-45f2-b0ef-1f49a80a07e7/uploaded_image_1765347227856.jpg'
    
    # Destination directory (media/branding)
    media_dir = os.path.join(settings.MEDIA_ROOT, 'branding')
    os.makedirs(media_dir, exist_ok=True)
    
    # Destination file path
    dest_filename = 'logo.jpg'
    dest_path = os.path.join(media_dir, dest_filename)
    
    print(f"Copying from {source_path} to {dest_path}")
    
    try:
        shutil.copy2(source_path, dest_path)
        print("File copied successfully.")
        
        # Update Branding object
        branding = Branding.objects.first()
        if not branding:
            branding = Branding.objects.create(primary_color='#00ff9d')
            print("Created new Branding object.")
            
        # Set the logo field to the relative path within MEDIA_ROOT
        branding.logo = 'branding/logo.jpg'
        branding.save()
        print(f"Branding updated with logo: {branding.logo}")
        
    except FileNotFoundError:
        print(f"Error: Source file not found at {source_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    seed_logo()
