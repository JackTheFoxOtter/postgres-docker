"""
This scripts acts as a process supervisor for Postgres and the custom Quart API.
When launched, it will spawn subprocesses for both, logging stdout and stderr to the console.
Notably, the two processes handle terminations differently.

When the Quart API process ends, it will automatically be restarted. This should
reliably recover it in case of an exception.

When the Postgres process ends, it will NOT be automatically restarted. In that case
an exception is raised, which will lead to the entire supervisor script terminating with
exit code 1. That will stop the Docker container so that the Docker daemon can decide how
to proceed depending on configuration. Usually that means restarting the container.

"""
from asyncio import StreamReader, create_subprocess_shell
from asyncio.subprocess import Process, PIPE
from datetime import datetime, UTC
from typing import Any, List
import asyncio
import logging
import signal
import sys
import os


shutdown_requested : bool = False
processes : List[Process] = []


def setup_logging() -> None:
    """
    Function to setup logging configuration. Should only be called once at startup.

    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Setup formatter
    formatter = logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %H:%M:%S')

    # Setup stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.formatter = formatter
    root_logger.addHandler(stream_handler)

    # Setup file handler
    utc_timestamp = datetime.now(UTC).strftime('%Y%m%d%H%M%S')
    file_handler = logging.FileHandler(f'/logs/{utc_timestamp}_supervisor.log')
    file_handler.formatter = formatter
    root_logger.addHandler(file_handler)

    # Handle uncaught exceptions with logger as well
    def _handle_uncaught_exception(exc_type : Any, exc_value : Any, exc_traceback : Any) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            root_logger.critical("KeyboardInterrupt received.")
        else:
            root_logger.critical("App has encountered an unhandled exception!", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _handle_uncaught_exception


async def log_lines_continuously(process_name : str, pipe_name : str, reader : StreamReader) -> None:
    """
    Continuously logs the provided reader's lines to the console as they show up, 
    until there are no new lines to log (indicating process termination).

    """
    while True:
        line = await reader.readline()
        if not line: break
        logging.info(f"[{process_name} > {pipe_name}] {line.decode('utf-8').rstrip(os.linesep)}")


async def execute_subprocess_shell(name : str, command : str) -> int:
    """
    Starts a subprocess for the provided shell command and begins to continuously log
    its stdout and stderr streams to the console until the process terminates.
    Once that happens, the process's exit code is returned.

    """
    process = await create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)
    
    global processes
    processes.append(process)

    await asyncio.gather(
        log_lines_continuously(name, 'stdout', process.stdout),
        log_lines_continuously(name, 'stderr', process.stderr)
    )

    await process.wait() # Wait for process to have ended (returncode isn't immediately accessible)
    return process.returncode
    

async def start_supervised_process(name : str, command : str, restart : bool = False, critical : bool = True) -> None:
    """
    Runs a shell command as a new supervised process.
    If restart = True, will automatically restart the process when it terminates.
    If critical = True an Exception will be raised should the process stop (without being restarted)

    """
    logging.info(f"[Supervisor] Creating subprocess '{name}' for shell command '{command}'...")

    while True:
        returncode = await execute_subprocess_shell(name, command)
        logging.info(f"[Supervisor] Subprocess '{name}' exited with code {returncode}.")

        if restart and not shutdown_requested:
            # Subprocess should be restarted
            logging.info(f"[Supervisor] Restarting subprocess '{name}' for shell command '{command}'...")

        else:
            # Subprocess should not be restarted
            logging.info(f"[Supervisor] Subprocess '{name}' will NOT be restarted.")
            break

    if critical and not shutdown_requested:
        # A critical process has ended. Throw exception to take down the container
        raise Exception("Critical process has ended!")


async def main():
    try:
        # Start supervised processes
        await asyncio.gather(
            start_supervised_process("Postgres", '/usr/local/bin/docker-entrypoint.sh postgres -c log_line_prefix="%t "', restart=False, critical=True),
            start_supervised_process("QuartAPI", 'python -u /api/run.py', restart=True, critical=False),
        )
        logging.info(f"[Supervisor] All processes have ended without indication of error.")
        exit(0)
    
    except Exception as ex:
        # Exception occured, exit to kill container
        logging.info(f"[Supervisor] Exception: {str(ex)}")
        exit(1)


def signal_handler(signal_int : int, frame : Any):
    """
    Any termination signal should initiate the shutdown procedure.
    Once the shutdown procedure is initiated, stopped processes will not restart anymore.
    Ever subprocess will receive the SIGTERM signal to shut it down.

    """
    signal_name = signal.Signals(signal_int).name
    logging.info(f"{signal_name} received, shutting down...")
    
    global shutdown_requested
    shutdown_requested = True

    process : Process
    for process in processes:
        process.send_signal(signal.SIGTERM)


if __name__ == '__main__':
    setup_logging()

    logging.info(f"[Supervisor] Registering termination signals...")
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    logging.info(f"[Supervisor] Starting process supervisor...")
    asyncio.run(main())
