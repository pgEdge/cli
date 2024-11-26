import os
import signal
import psutil

import util

pid_file = "ace/ace_daemon.pid"


def is_process_running(pid):
    """Check if a process with the given PID is running."""
    try:
        return psutil.pid_exists(pid)
    except Exception as e:
        util.exit_message(f"Error checking process status: {e}")
        return False


def stop_daemon():
    """Stop the running ace_daemon process if it's running."""
    try:
        if os.path.exists(pid_file):
            with open(pid_file, "r") as pidf:
                pid = int(pidf.read().strip())

            if is_process_running(pid):
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                util.message(
                    f"ACE Daemon and its subprocesses have been stopped (PID: {pid})."
                )
            else:
                util.message(
                    f"No running process found for PID {pid}."
                    " Cleaning up stale PID file."
                )

            os.remove(pid_file)
        else:
            util.message("No PID file found. Daemon may not be running.")
    except Exception as e:
        util.exit_message(f"Error stopping ACE Daemon: {e}")


if __name__ == "__main__":
    stop_daemon()
