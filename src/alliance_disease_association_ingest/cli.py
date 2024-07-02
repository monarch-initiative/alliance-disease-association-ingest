import logging
from pathlib import Path
import typer
from kghub_downloader.download_utils import download_from_yaml
from koza.cli_utils import transform_source
import sys

app = typer.Typer()
logger = logging.getLogger(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG for detailed logs

@app.callback()
def callback(
    version: bool = typer.Option(False, "--version", is_eager=True),
):
    """alliance-disease-association-ingest CLI."""
    if version:
        from alliance_disease_association_ingest import __version__

        typer.echo(f"alliance-disease-association-ingest version: {__version__}")
        raise typer.Exit()

@app.command()
def download(force: bool = typer.Option(False, help="Force download of data, even if it exists")):
    """Download data for alliance-disease-association-ingest."""
    typer.echo("Downloading data for alliance-disease-association-ingest...")
    download_config = Path(__file__).parent / "download.yaml"
    download_from_yaml(yaml_file=download_config, output_dir=".", ignore_cache=force)

@app.command()
def transform(
    output_dir: str = typer.Option("output", help="Output directory for transformed data"),
    row_limit: int = typer.Option(None, help="Number of rows to process"),
    verbose: int = typer.Option(False, help="Whether to be verbose"),
):
    """Run the Koza transform for alliance-disease-association-ingest."""
    typer.echo("Transforming data for alliance-disease-association-ingest...")
    transform_code = Path(__file__).parent / "transform.yaml"

    # Add detailed logging around the transform process
    logger.debug(f"Starting transformation with row_limit={row_limit}, verbose={verbose}")

    try:
        transform_source(
            source=transform_code,
            output_dir=output_dir,
            output_format="tsv",
            row_limit=row_limit,
            verbose=verbose,
        )
    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        raise

    logger.debug("Transformation completed successfully")
    sys.exit(0)  # Explicitly exit after completion

if __name__ == "__main__":
    app()
