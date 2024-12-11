import click
from .. import utils

def run(command, capture_output=False, live_output=False):
    """
    Adapter to pass output device to the utils.run command.

    Args:
        command (str): The command to run.
        capture_output (bool): Whether to capture the output of the command.

    Returns:
        str: The output of the command if capture_output is True.
    """
    return utils.run(command, stream=click.echo, capture_output=capture_output, live_output=live_output)