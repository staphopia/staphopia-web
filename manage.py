#!/usr/bin/env python3
import os
import socket
import sys

if __name__ == "__main__":
    if socket.gethostname() == 'staphopia':
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              "staphopia.settings.www")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              "staphopia.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
