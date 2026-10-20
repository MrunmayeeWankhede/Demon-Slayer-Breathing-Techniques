#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
for breathing_python in python3.11 python3.12 python3; do
  if command -v "$breathing_python" >/dev/null 2>&1; then
    if "$breathing_python" -c 'import sys; assert sys.version_info[:2] in [(3,11),(3,12)]' >/dev/null 2>&1; then
      "$breathing_python" launcher.py
      exit $?
    fi
  fi
done
echo 'Install Python 3.11 or 3.12 for macOS from https://www.python.org/downloads/'
echo 'Then open this file again.'
read -r -p 'Press Enter to close.'
