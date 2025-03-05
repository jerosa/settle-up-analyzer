"""Main entry point for the CLI."""
import click

from finanalyzer.cli.commands.process import process_command


@click.group()
def cli():
    """Financial data processing and analysis tools."""
    pass


cli.add_command(process_command, name="process")


if __name__ == "__main__":
    cli() 
