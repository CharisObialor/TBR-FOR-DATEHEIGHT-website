import inspect
import os
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

MARKER = os.path.join(HERE, ".deps_ok")
LOCK = os.path.join(HERE, ".deps.lock")
INSTALL_LOG = os.path.join(HERE, "deps_install.log")
STARTUP_ERR = os.path.join(HERE, "startup_error.log")
RUNNER = os.path.join(HERE, "deps_bootstrap.py")
LOCK_MAX_AGE = 1800


def _log(msg):
    try:
        with open(INSTALL_LOG, "a", encoding="utf-8") as f:
            f.write(msg)
    except Exception:
        pass


def _spawn_installer():
    try:
        if os.path.exists(LOCK):
            age = time.time() - os.path.getmtime(LOCK)
            if age < LOCK_MAX_AGE:
                _log("installer already running (lock age %ds)\n" % int(age))
                return False
            try:
                os.remove(LOCK)
            except Exception:
                pass
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except OSError:
        return False
    try:
        logh = open(INSTALL_LOG, "a", encoding="utf-8")
        subprocess.Popen(
            [sys.executable, RUNNER],
            stdin=subprocess.DEVNULL,
            stdout=logh,
            stderr=logh,
            cwd=HERE,
            start_new_session=True,
        )
        _log("installer spawned at %s\n" % time.strftime("%H:%M:%S"))
        return True
    except Exception:
        try:
            os.remove(LOCK)
        except Exception:
            pass
        try:
            with open(STARTUP_ERR, "a", encoding="utf-8") as f:
                f.write("\n\nFailed to spawn dependency installer:\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
        return False


if os.path.exists(MARKER):
    _import_ok = True
    try:
        from a2wsgi import ASGIMiddleware
        from main import app
    except Exception:
        _import_ok = False
        try:
            with open(STARTUP_ERR, "w", encoding="utf-8") as f:
                f.write("App failed to import. Python: %s\n\n" % sys.version)
                traceback.print_exc(file=f)
        except Exception:
            pass
else:
    _import_ok = False
    _log("\n==== boot without deps at %s ====\n" % time.strftime("%H:%M:%S"))
    _spawn_installer()


if _import_ok:
    _started = False

    async def _run_startup():
        startup = getattr(app.router, "startup", None)
        if callable(startup):
            await startup()
            return
        for handler in getattr(app.router, "on_startup", []):
            result = handler()
            if inspect.isawaitable(result):
                await result

    async def _serve(scope, receive, send):
        global _started
        if not _started:
            _started = True
            try:
                await _run_startup()
            except Exception:
                try:
                    with open(STARTUP_ERR, "a", encoding="utf-8") as f:
                        f.write("\n\nStartup handler failed:\n")
                        traceback.print_exc(file=f)
                except Exception:
                    pass
                raise
        await app(scope, receive, send)

    application = ASGIMiddleware(_serve)

else:

    def application(environ, start_response):
        start_response(
            "503 Service Unavailable",
            [("Content-Type", "text/plain")],
        )
        if not os.path.exists(MARKER):
            body = (
                b"Backend is installing dependencies - refresh in a few "
                b"minutes. Progress: deps_install.log in the app folder."
            )
        else:
            body = (
                b"Application failed to start - see startup_error.log "
                b"in the app folder"
            )
        return [body]
