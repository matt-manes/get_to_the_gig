import os
import sys
from pathier import Pathier

root = Pathier(__file__).parent

print("Installing requirements... ")
os.system(f"{sys.executable} -m pip install -r {root/'requirements.txt'}")

print("Initializing database if it doesn't exist...")
os.system(f"{sys.executable} {root/'database_init.py'}")

print("Set up complete.")

print("Note: This project uses firefox for its selenium browser.")
print(
    "If you do not have geckodriver.exe in your PATH or in this directory, then you should download the appropriate version for your system here:"
)
print("https://github.com/mozilla/geckodriver/releases/tag/v0.32.0")
input("Press any key to close... ")
