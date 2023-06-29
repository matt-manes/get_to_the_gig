import os
import sys
from pathier import Pathier

root = Pathier(__file__).parent

if __name__ == "__main__":

    print("Installing requirements... ")
    os.system(f"{sys.executable} -m pip install -r {root/'requirements.txt'}")

    print("Initializing database if it doesn't exist...")
    os.system(f"{sys.executable} {root/'gigbased.py'}")

    print("Set up complete.")

    print("Note: This project uses firefox for its selenium browser.")
    print(
        "If you do not have geckodriver.exe in your PATH or in this directory, then you should download the appropriate version for your system here:"
    )
    print("https://github.com/mozilla/geckodriver/releases")
    input("Press any key to close... ")
