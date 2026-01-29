# alliance-disease-association-ingest

Koza ingest for Alliance of Genome Resources disease association data, transforming gene, allele, and model/genotype to disease associations into Biolink model format.

## Data Source

[Alliance of Genome Resources](https://www.alliancegenome.org/) aggregates disease association data from multiple model organism databases including MGI, ZFIN, FlyBase, WormBase, SGD, RGD, and Xenbase.

Data is downloaded from: `https://fms.alliancegenome.org/download/DISEASE-ALLIANCE_COMBINED.tsv.gz`

## Output

This ingest produces:
- **GenotypeToDiseaseAssociation** - Links affected genomic models to diseases they model
- **VariantToDiseaseAssociation** - Links alleles to associated diseases
- **GeneToDiseaseAssociation** - Links genes to associated diseases

## Usage

```bash
# Install dependencies
just install

# Run full pipeline
just run

# Or run steps individually
just download      # Download Alliance data
just transform-all # Run Koza transform
just test          # Run tests
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- [just](https://github.com/casey/just) command runner

## License

BSD-3-Clause
