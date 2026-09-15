"""
WSGI config for launchpad project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')

application = get_wsgi_application()


import os
import time
import threading


def keep_alive():
    while True:
        try:
            url = "https://drid-launchpad.onrender.com/"
            res = requests.get(url, timeout=10)
            print(f"Pinged at {time.ctime()}: Status {res.status_code}")
        except Exception as e:
            print(f"Error pinging at {time.ctime()}: {e}")
        time.sleep(60 * 12)  # every 12 minutes


#ping this man
t = threading.Thread(target=keep_alive, daemon=True)
t.start()