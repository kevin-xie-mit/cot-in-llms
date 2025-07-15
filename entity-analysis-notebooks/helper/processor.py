import os
import json
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

class Processor:
    def __init__(self):
        pass
        
    def get_entity_info(self, root):
        # Extract all entity elements (ones with "ontologyConceptArr" attribute). A "mention" is a "textsem:XXXMention" element.
        mention_arr = []
        for mention in root.iter():
            if 'ontologyConceptArr' in mention.attrib:
                mention_arr.append(mention)

        entity_dict = {} # Maps entity xmi --> information about that entity
        for xxx_mention in mention_arr:
            # Get all entities in a given "textsem:XXXMention" (can be more than 1 per)
            ontology_concept_arr = xxx_mention.attrib['ontologyConceptArr']
            xmi_ids = [int(id) for id in ontology_concept_arr.split(" ")]

            # All of the ids in "ontologyConceptArr" are the xmi_ids obtained previously from UmlsConcept

            # Store in a dictionary. Maps entity xmi (unique XML identifier) to the entity information
            for xmi_id in xmi_ids:
                entity_dict[xmi_id] = {
                    'begin': xxx_mention.attrib['begin'],
                    'end': xxx_mention.attrib['end'],
                    'polarity': xxx_mention.attrib['polarity'],
                    'subject': xxx_mention.attrib['subject'],
                    'historyOf': xxx_mention.attrib['historyOf']
                }

        # maps entity xmi (unique XML identifier) to the more fine-grained information about the entity
        return entity_dict
    
    def extract_all_entities(self, xmi_file_path):
        """
        Given the path to a .xmi file, this function will extract the UMLS concepts from the .xmi file
        and return them as a list of dictionaries.
        """
        # Parse the .xmi file
        tree = ET.parse(xmi_file_path)
        root = tree.getroot()

        # Extract all <refsem:UmlsConcept> elements
        namespaces = {
            "refsem": "http:///org/apache/ctakes/typesystem/type/refsem.ecore",
            "tcas": "http:///uima/tcas.ecore",
            "xmi": "http://www.omg.org/XMI"
        }
        umls_concepts = root.findall(".//refsem:UmlsConcept", namespaces)  # This finds all UMLS concepts in the .xmi file

        entity_dict = self.get_entity_info(root)

        output_dict = {}
        for umls_concept in umls_concepts:
            xmi_id = int(umls_concept.attrib.get("{http://www.omg.org/XMI}id"))
            entity_preferred_text = umls_concept.attrib.get("preferredText")

            # Maps unique entity ID --> entity information (entity name, begin, end, polarity, subject, historyOf)
            entity_dict[xmi_id]["entity"] = entity_preferred_text
            entity_dict[xmi_id]["xmi_id"] = xmi_id

        # TESTING
        # with open("test_out.txt", "w") as f:
        #     f.write(json.dumps(entity_dict, indent=4))
        
        return entity_dict
    

def test():
    file_path = "/Users/kevinxie/Desktop/LLM CoT/LLM-CoT/gold_labels_for_inputs/1-1.ADE-ADE identification/input_18870.txt.xmi"
    processor = Processor()

    all_entities = processor.extract_all_entities(file_path)
    print("ALL ENTITIES: ", all_entities)

if __name__ == "__main__":
    print("**" *30 + "TESTING" + "**" * 30)
    test()
    print("**" * 60)