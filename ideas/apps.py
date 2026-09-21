from django.apps import AppConfig


class IdeasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ideas'




import os
import time
import threading
import requests  
from django.apps import AppConfig

def keep_alive():
    while True:
        try:
            url = "https://drid-launchpad.onrender.com/"
            res = requests.get(url, timeout=10)
            print(f"Pinged at {time.ctime()}: Status {res.status_code}")
        except Exception as e:
            print(f"Error pinging at {time.ctime()}: {e}")
        time.sleep(60 * 12)  # every 12 minutes

class IdeasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ideas'  

    def ready(self):
        # Prevent the thread from starting twice during local development reloads
        if os.environ.get('RUN_MAIN', None) != 'true':
            t = threading.Thread(target=keep_alive, daemon=True)
            t.start()