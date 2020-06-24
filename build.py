
import os
import subprocess

# Gui call for debug:
# subprocess.call(["auto-py-to-exe", "main.py"])

# Main call for build
call = "pyinstaller --noconfirm --onefile --console --hidden-import \"pkg_resources.py2_warn\"  \"{}\main.py\""
subprocess.call(call.format(os.getcwd()))
