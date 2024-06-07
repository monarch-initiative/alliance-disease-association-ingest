import uuid
import pandas as pd
from biolink_model.datamodel.pydanticmodel_v2 import (
    GeneToDiseaseAssociation,
    GenotypeToDiseaseAssociation,
    VariantToDiseaseAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum
)
from koza.cli_utils import get_koza_app

# Load the CSV file
mapping_file = ".tsv" # MONDO-DOID mapping file
mapping_df = pd.read_csv(mapping_file, delimiter='\t')

# Create a mapping dictionary from DOID to MONDO
doid_to_mondo_mapping = dict(zip(mapping_df['object_id'], mapping_df['subject_id']))

# Continue with your existing code
koza_app = get_koza_app("alliance_disease_association")

source_map = {
    "FB": "infores:flybase",
    "MGI": "infores:mgi",
    "RGD": "infores:rgd",
    "HGNC": "infores:rgd",  # Alliance contains RGD curation of human genes
    "SGD": "infores:sgd",
    "WB": "infores:wormbase",
    "Xenbase": "infores:xenbase",
    "ZFIN": "infores:zfin",
}

predicate_map = {
    "is_implicated_in": "biolink:contributes_to",
    "is_marker_for": "biolink:associated_with",
    "is_model_of": "biolink:model_of"
}

# Set to keep track of unique associations
seen_associations = set()

while (row := koza_app.get_row()) is not None:
    subject_category = row["DBobjectType"]
    if subject_category == 'gene':
        continue  # Skip processing for 'gene'

    #if subject_category == 'gene':
    #    AssociationClass = GeneToDiseaseAssociation
    if subject_category == 'allele':
        AssociationClass = VariantToDiseaseAssociation
    elif subject_category == 'affected_genomic_model':
        AssociationClass = GenotypeToDiseaseAssociation
    else:
        koza_app.next_row()
        continue

    association_type = row["AssociationType"]
    predicate = predicate_map.get(association_type)

    if predicate is None:
        koza_app.next_row()
        continue

    unique_id = (row["DBObjectID"], predicate, row["DOID"], row["AssociationType"])

    if unique_id in seen_associations:
        koza_app.next_row()
        continue

    seen_associations.add(unique_id)

    # Replace DOID with MONDO if available
    object_id = doid_to_mondo_mapping.get(row["DOID"], row["DOID"])

    print(subject_category, row["DBObjectID"], predicate, row["DOID"], object_id, row["AssociationType"])

    association = AssociationClass(
        id=str(uuid.uuid1()),
        subject=row["DBObjectID"],
        predicate=predicate,
        object=object_id,
        has_evidence=[row["EvidenceCode"]],
        primary_knowledge_source=source_map[row["DBObjectID"].split(':')[0]],
        aggregator_knowledge_source=["infores:monarchinitiative", "infores:agrkb"],
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.manual_agent
        # TODO: capture row["ExperimentalCondition"], probably as qualifier?
        # TODO: capture row["Reference"] as publications. Might bring in redundancy?
        # TODO: set KnowledgeLevelEnum and AgentTypeEnum, it looks like there are inferred edges and that can show up in the KL/AT
    )

    koza_app.write(association)