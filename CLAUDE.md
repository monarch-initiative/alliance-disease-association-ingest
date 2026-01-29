# alliance-disease-association-ingest

This is a Koza ingest repository for transforming Alliance disease association data into Biolink model format.

## Project Structure

- `download.yaml` - Configuration for downloading Alliance disease data
- `src/` - Transform code and configuration
  - `transform.py` / `transform.yaml` - Main transform for disease associations
- `tests/` - Unit tests for transforms
- `output/` - Generated nodes and edges (gitignored)
- `data/` - Downloaded source data (gitignored)

## Key Commands

- `just run` - Full pipeline (download -> transform)
- `just download` - Download Alliance disease data
- `just transform-all` - Run all transforms
- `just test` - Run tests
