#!/bin/bash
exec arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 "$(dirname "$0")/crop.py" "$@"
