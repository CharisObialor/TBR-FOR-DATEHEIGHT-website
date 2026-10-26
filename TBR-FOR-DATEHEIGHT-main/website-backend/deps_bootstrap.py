"""One-shot dependency installer for the cPanel deployment.

Run detached by passenger_wsgi.py when the .deps_ok marker is missing.
Installs requirements.txt into whatever interpreter/venv launched it,
then writes the marker so subsequent Passenger spawns import normally.
"""

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "deps_install.log")
MARKER = os.path.join(HERE, ".deps_ok")
REQ = os.path.join(HERE, "requirements.txt")


def main():
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            "\n==== deps install start %s | Python %s ====\n"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), sys.version.split()[0])
        )
        f.flush()
        rc = subprocess.call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "--disable-pip-version-check",
                "-r",
                REQ,
            ],
            stdout=f,
            stderr=f,
            cwd=HERE,
        )
        f.write(
            "==== pip exit=%s at %s ====\n"
            % (rc, time.strftime("%Y-%m-%d %H:%M:%S"))
        )
    if rc == 0:
        with open(MARKER, "w", encoding="utf-8") as m:
            m.write("installed %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
