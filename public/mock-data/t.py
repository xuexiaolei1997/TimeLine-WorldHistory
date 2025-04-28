import os

os.chdir(os.path.dirname(__file__))

import json

with open("periods.json", "r", encoding="utf8") as f:
    event = json.load(f)

print()
