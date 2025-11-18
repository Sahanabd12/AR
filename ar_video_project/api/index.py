# ar_video_project/api/index.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ar_video_project.settings')
application = get_wsgi_application()

# Vercel requires the variable name to be "app"
app = application