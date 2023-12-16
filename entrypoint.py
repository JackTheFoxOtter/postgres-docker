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
from asyncio.subprocess import PIPE
import asyncio


async def print_lines_continuously(process_name : str, pipe_name : str, reader : StreamReader):
    """
    Continuously logs the provided reader's lines to the console as they show up, 
    until there are no new lines to log (indicating process termination).

    """
    while True:
        line = await reader.readline()
        if not line: break
        print(f"{process_name} > {pipe_name}  | {line.decode('utf-8')}", end="")


async def execute_subprocess_shell(name : str, command : str) -> int:
    """
    Starts a subprocess for the provided shell command and begins to continuously log
    its stdout and stderr streams to the console until the process terminates.
    Once that happens, the process's exit code is returned.

    """
    process = await create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)
    
    await asyncio.gather(
        print_lines_continuously(name, 'stdout', process.stdout),
        print_lines_continuously(name, 'stderr', process.stderr)
    )

    await process.wait() # Wait for process to have ended (returncode isn't immediately accessible)
    return process.returncode
    

async def start_supervised_process(name : str, command : str, restart : bool = False, critical : bool = True):
    """
    Runs a shell command as a new supervised process.
    If restart = True, will automatically restart the process when it terminates.
    If critical = True an Exception will be raised should the process stop (without being restarted)

    """
    print(f"Creating subprocess '{name}' for shell command '{command}'...")

    while True:
        returncode = await execute_subprocess_shell(name, command)
        print(f"Subprocess '{name}' exited with code {returncode}.")

        if restart:
            # Subprocess should be restarted
            print(f"Restarting subprocess '{name}' for shell command '{command}'...")

        else:
            # Subprocess should not be restarted
            print(f"Subprocess '{name}' will NOT be restarted.")
            break

    if critical:
        # A critical process has ended. Throw exception to take down the container
        raise Exception("Critical process has ended!")


async def main():
    try:
        # Start supervised processes
        await asyncio.gather(
            start_supervised_process("Postgres", '/usr/local/bin/docker-entrypoint.sh postgres', restart=False, critical=True),
            start_supervised_process("QuartAPI", 'python -u /api/run.py', restart=True, critical=False),
        )
        print(f"All processes have ended without indication of error.")
        exit(0)
    
    except Exception as ex:
        # Exception occured, exit to kill container
        print(f"Exception: {str(ex)}")
        exit(1)


if __name__ == '__main__':
    print("Starting process supervisor...")
    asyncio.run(main())