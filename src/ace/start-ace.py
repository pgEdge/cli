import subprocess
import os
import psutil
import sys
import util

log_file = "ace/ace_daemon.log"
pid_file = "ace/ace_daemon.pid"


def is_process_running(pid):
    """Check if a process with the given PID is running."""
    try:
        return psutil.pid_exists(pid)
    except Exception as e:
        util.exit_message(f"Error checking process status: {e}")
        return False


def start_daemon():
    """Start the ace_daemon process in the background and log its output."""
    with open(log_file, "a") as log:
        process = subprocess.Popen(
            ["python", "-c", "import ace_daemon; ace_daemon.start_ace()"],
            stdout=log,
            stderr=log,
            # Create a new session and process group for the daemon
            # since ACE needs to create multiple subprocesses
            preexec_fn=os.setsid,
        )

        with open(pid_file, "w") as pidf:
            pidf.write(str(process.pid))

        util.message(
            f"ACE Daemon started with PID {process.pid}, logging to {log_file}"
        )


def main():
    if os.path.exists(pid_file):
        with open(pid_file, "r") as pidf:
            pid = int(pidf.read().strip())

        if is_process_running(pid):
            util.exit_message(f"ACE Daemon is already running with PID {pid}. Exiting.")
            sys.exit(0)
        else:
            util.message(
                f"Stale PID file found for PID {pid}. Starting new daemon instance."
            )
            os.remove(pid_file)

    start_daemon()


if __name__ == "__main__":
    main()
