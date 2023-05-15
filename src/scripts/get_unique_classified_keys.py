import json
import os
from pathlib import Path

import numpy as np

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

import sys

sys.path.append(str(project_root))
