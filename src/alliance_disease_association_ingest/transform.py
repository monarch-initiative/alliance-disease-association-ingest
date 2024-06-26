import uuid
import pandas as pd
import traceback
from biolink_model.datamodel.pydanticmodel_v2 import (
    GenotypeToDiseaseAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum
)
from koza.cli_utils import get_koza_app
import sys

# Constants
#mapping_file = "data/mondo_exactmatch_doid.sssom.tsv"
mapping_file = "data/doid.sssom.tsv"
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

# Load mapping data
mapping_df = pd.read_csv(mapping_file, delimiter='\t', skiprows=34)
doid_to_mondo_mapping = dict(zip(mapping_df['object_id'], mapping_df['subject_id']))

# Initialize Koza application
koza_app = get_koza_app("alliance_disease")

# Track associations
merged_associations = {}

# Main processing loop
print("Starting to process rows...")

try:
    while True:
        try:
            row = koza_app.get_row()
            if row is None:
                print("No more rows to process. Breaking out of loop.")
                break  # Exit the loop when there are no more rows

            subject_category = row.get("DBobjectType")
            if not subject_category or row.get("ExperimentalCondition") or row.get("Modifier"):
                continue

            if subject_category == 'affected_genomic_model':
                AssociationClass = GenotypeToDiseaseAssociation
            else:
                continue

            association_type = row.get("AssociationType")
            predicate = predicate_map.get(association_type)
            if not predicate:
                continue

            object_id = doid_to_mondo_mapping.get(row.get("DOID"), row.get("DOID"))
            unique_id = (row.get("DBObjectID"), predicate, row.get("DOID"), object_id)

            if unique_id in merged_associations:
                merged_associations[unique_id]['has_evidence'].append(row.get("EvidenceCode"))
                merged_associations[unique_id]['publications'].append(row.get("Reference"))
            else:
                merged_associations[unique_id] = {
                    'subject': row.get("DBObjectID"),
                    'predicate': predicate,
                    'original_object': row.get("DOID"),
                    'object': object_id,
                    'has_evidence': [row.get("EvidenceCode")],
                    'publications': [row.get("Reference")],
                    'primary_knowledge_source': source_map.get(row.get("DBObjectID").split(':')[0], "unknown"),
                }
        except StopIteration:
            print("Reached end of data. Finalizing the associations.")
            count = 0
            for unique_id, association_data in merged_associations.items():
                count += 1
                print(str(uuid.uuid1()), unique_id, list(set(association_data['has_evidence'])), list(set(association_data['publications'])), count)
                association = GenotypeToDiseaseAssociation(
                    id=str(uuid.uuid1()),
                    subject=association_data['subject'],
                    predicate=association_data['predicate'],
                    object=association_data['object'],
                    original_object=association_data['original_object'],
                    has_evidence=list(set(association_data['has_evidence'])),
                    publications=list(set(association_data['publications'])),  # Ensure unique publications
                    primary_knowledge_source=association_data['primary_knowledge_source'],
                    aggregator_knowledge_source=["infores:monarchinitiative", "infores:agrkb"],
                    knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                    agent_type=AgentTypeEnum.manual_agent
                )
                koza_app.write(association)
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            break

    print("Processing complete.")
    sys.exit(0)  # Explicitly exit after processing

except Exception as main_e:
    print(f"Main error: {main_e}")
    traceback.print_exc()
    sys.exit(1)  # Exit with error code if there is an exception
