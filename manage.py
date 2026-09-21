#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

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


if __name__ == '__main__':
    main()
