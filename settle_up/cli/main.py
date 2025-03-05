"""Main entry point for the Settle Up CLI."""
import click

from settle_up.cli.commands.process import process_command


@click.group()
def cli():
    """Settle Up data processing and analysis tools."""
    pass


cli.add_command(process_command, name="process")


if __name__ == "__main__":
    cli() 
