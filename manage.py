#!/usr/bin/env python
import os
import sys
import workbench

from django.conf import settings

if __name__ == "__main__":
    xblock_sdk_dir = os.path.dirname(os.path.dirname(workbench.__file__))
    sys.path.append(xblock_sdk_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workbench.settings")
    settings.INSTALLED_APPS.append('problem_builder')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
