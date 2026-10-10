"""Run the complete cached collection/training workflow from any directory."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for command in [[sys.executable,str(root/'collect.py')],['node',str(root/'features.cjs')],[sys.executable,str(root/'train.py')],[sys.executable,str(root/'fit_tracks.py')],['node',str(root/'check.cjs')]]:
 subprocess.run(command,check=True)
