#/bin/bash

directory="${1:-.}"

find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "logs" -exec rm -rf {} +
