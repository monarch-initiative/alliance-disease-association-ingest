"""
Test file for the Alliance disease association transform.

Uses the Koza 2.x testing pattern with KozaRunner and MockWriter.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for transform import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from koza.io.writer.writer import KozaWriter
from koza.runner import KozaRunner, KozaTransformHooks

from transform import transform_record


class MockWriter(KozaWriter):
    """Mock writer that collects entities for testing."""

    def __init__(self):
        self.items = []

    def write(self, entities):
        self.items += entities

    def write_nodes(self, nodes):
        self.items += list(nodes)

    def write_edges(self, edges):
        self.items += list(edges)

    def finalize(self):
        pass


# Define the ingest name and transform script path
INGEST_NAME = "alliance_disease"


def run_transform(row):
    """Helper function to run the transform on a single row."""
    writer = MockWriter()
    runner = KozaRunner(
        data=iter([row]),
        writer=writer,
        hooks=KozaTransformHooks(transform_record=[transform_record])
    )
    runner.run()
    return writer.items


# Define the mock koza transform on an example row
@pytest.fixture
def mgi_agm():
    row = {
        'Taxon': 'NCBITaxon:10090',
        'SpeciesName': 'Mus musculus',
        'DBobjectType': 'affected_genomic_model',
        'DBObjectID': 'MGI:3799157',
        'DBObjectSymbol': 'None [background:] C58/J',
        'AssociationType': 'is_model_of',
        'DOID': 'DOID:0060041',
        'DOtermName': 'autism spectrum disorder',
        'WithOrtholog': '',
        'InferredFromID': '',
        'InferredFromSymbol': '',
        'ExperimentalCondition': '',
        'Modifier': '',
        'EvidenceCode': 'ECO:0000033',
        'EvidenceCodeName': 'author statement supported by traceable reference',
        'Reference': 'PMID:29885454',
        'Date': '20181028',
        'Source': 'MGI'
    }
    return run_transform(row)


def test_mgi_agm(mgi_agm):
    entities = mgi_agm
    assert len(entities) == 1
    association = entities[0]
    assert association
    assert association.category == ['biolink:GenotypeToDiseaseAssociation']
    assert association.subject == 'MGI:3799157'
    assert association.predicate == 'biolink:model_of'
    assert association.object == 'DOID:0060041'
    assert association.has_evidence == ['ECO:0000033']
    assert association.publications == ['PMID:29885454']


@pytest.fixture
def zfin_agm():
    row = {
        'Taxon': 'NCBITaxon:7955',
        'SpeciesName': 'Danio rerio',
        'DBobjectType': 'affected_genomic_model',
        'DBObjectID': 'ZFIN:ZDB-FISH-160908-10',
        'DBObjectSymbol': 'TU + MO2-mybpc2b',
        'AssociationType': 'is_model_of',
        'DOID': 'DOID:423',
        'DOtermName': 'myopathy',
        'WithOrtholog': '',
        'InferredFromID': '',
        'InferredFromSymbol': '',
        'ExperimentalCondition': 'Has Condition: standard conditions',
        'Modifier': '',
        'EvidenceCode': 'ECO:0000305',
        'EvidenceCodeName': 'curator inference used in manual assertion',
        'Reference': 'PMID:27022191',
        'Date': '20240314',
        'Source': 'ZFIN'
    }
    return run_transform(row)


def test_zfin_agm(zfin_agm):
    entities = zfin_agm
    assert len(entities) == 1
    association = entities[0]
    assert association
    assert association.category == ['biolink:GenotypeToDiseaseAssociation']
    assert association.subject == 'ZFIN:ZDB-FISH-160908-10'
    assert association.predicate == 'biolink:model_of'
    assert association.object == 'DOID:423'
    assert association.has_evidence == ['ECO:0000305']
    assert association.publications == ['PMID:27022191']


@pytest.fixture
def zfin_agm_chemical_environment():
    row = {
        'Taxon': 'NCBITaxon:7955',
        'SpeciesName': 'Danio rerio',
        'DBobjectType': 'affected_genomic_model',
        'DBObjectID': 'ZFIN:ZDB-FISH-150901-29105',
        'DBObjectSymbol': 'WT',
        'AssociationType': 'is_model_of',
        'DOID': 'DOID:0060668',
        'DOtermName': 'anencephaly',
        'WithOrtholog': '',
        'InferredFromID': '',
        'InferredFromSymbol': '',
        'ExperimentalCondition': 'Has Condition: chemical treatment by environment: SU5402',
        'Modifier': '',
        'EvidenceCode': 'ECO:0000305',
        'EvidenceCodeName': 'curator inference used in manual assertion',
        'Reference': 'PMID:29488319',
        'Date': '20240314',
        'Source': 'ZFIN'
    }
    return run_transform(row)


def test_zfin_agm_chemical_environment(zfin_agm_chemical_environment):
    entities = zfin_agm_chemical_environment
    assert len(entities) == 0
    assert entities == []
