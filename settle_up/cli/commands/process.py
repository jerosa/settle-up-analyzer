"""CLI command for processing Settle Up data."""
from pathlib import Path
from typing import Optional

import click

from settle_up.core.processor import ProcessorConfig, SettleUpProcessor


@click.command()
@click.argument(
    "workdir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--file",
    "-f",
    "filename",
    help="Specific transactions file to process. If not provided, uses the latest file.",
    default="auto",
)
@click.option(
    "--user",
    "-u",
    "user",
    help="User to analyze expenses for",
    required=True,
)
@click.option(
    "--output-format",
    "-o",
    type=click.Choice(["excel", "csv"]),
    default="excel",
    help="Output format for processed data",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Directory for output files. Defaults to workdir if not specified.",
)
def process_command(
    workdir: Path,
    filename: str,
    user: str,
    output_format: str,
    output_dir: Optional[Path],
) -> None:
    """Process Settle Up transaction data.
    
    WORKDIR is the directory containing the transaction CSV files.
    """
    click.echo(f"Processing Settle Up data from {workdir}")
    
    config = ProcessorConfig(
        workdir=workdir,
        filename_to_process=filename,
        user_to_analyse=user,
    )
    
    processor = SettleUpProcessor(config)
    
    try:
        processor.process_data()
        
        output_path = processor.export_processed_data(output_format)
        click.echo(f"Exported processed data to: {output_path}")
            
    except Exception as e:
        click.echo(f"Error processing data: {str(e)}", err=True)
        raise click.Abort() 
