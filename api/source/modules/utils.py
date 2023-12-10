from source.modules.api_helper import ArgumentValidationError
from pathvalidate import validate_filename, ValidationError
from asyncio import StreamReader, create_subprocess_shell
from asyncio.subprocess import PIPE
from datetime import datetime, UTC
from logging import Logger
from pathlib import Path
import asyncio
import os


def filename_validator(filename : str):
    """
    Validates an API argument provided filename.
    Raises ArgumentValidationError if invalid.
    
    """
    try:
        validate_filename(filename)
    except ValidationError:
        raise ArgumentValidationError("Not a valid filename")


def get_timestamped_filename(filename : str, extension : str = '') -> str:
    """
    Returns a filename with current UTC timestamp prefixed.

    """
    utc_now = datetime.now(tz=UTC) # Timezone aware current timestamp converted to UTC
    return f"{utc_now:%Y%m%d%H%M%S}_{filename}" + (f".{extension}" if len(extension) > 0 else "")


def get_unique_filename(directory : str, filename : str) -> str:
    """
    Returns a filename that's unique to the specified directory (by postfixing a counter).

    """
    file_name, file_extension = os.path.splitext(filename)
    
    current_filename = filename
    i = 2
    while Path(os.path.join(directory, current_filename)).is_file():
        current_filename = f"{file_name}_{i}{file_extension}"
        i += 1
    
    return current_filename


async def log_lines_continuously(logger : Logger, process_name : str, pipe_name : str, reader : StreamReader):
    """
    Continuously logs the provided reader's lines to the console as they show up, 
    until there are no new lines to log (indicating process termination).

    """
    while True:
        line = await reader.readline()
        if not line: break
        if pipe_name == 'stderr':
            # Log as error
            logger.error(f"Subprocess {process_name}: {line.decode('utf-8').rstrip(os.linesep)}")
        else:
            # Log as info
            logger.info(f"Subprocess {process_name}: {line.decode('utf-8').rstrip(os.linesep)}")


async def execute_subprocess_shell(logger : Logger, name : str, command : str) -> int:
    """
    Starts a subprocess for the provided shell command and begins to continuously log
    its stdout and stderr streams to the console until the process terminates.
    Once that happens, the process's exit code is returned.
    
    """
    process = await create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)
    
    await asyncio.gather(
        log_lines_continuously(logger, name, 'stdout', process.stdout),
        log_lines_continuously(logger, name, 'stderr', process.stderr)
    )

    await process.wait() # Wait for process to have ended (returncode isn't immediately accessible)
    return process.returncode