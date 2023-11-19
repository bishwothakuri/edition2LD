import xml.etree.ElementTree as ET
import os
from rdflib import RDF, Graph, Literal, Namespace, URIRef, BNode
from serialization.turtle import save_turtle_serialization
import json
import re

def extract_numbers(string, pattern):
    match = pattern.search(string)
    zero = '0'
    return match.group(1) if match else zero

# Load the XML file
NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

xml_file_path = os.path.join("data", "K_0440_0007.xml")
tree = ET.parse(xml_file_path)
root = tree.getroot()
g = Graph()

#get physDesc_id
physDesc_id = root.find(".//tei:physDesc", NS)
ref_element = physDesc_id.find(".//tei:ref", NS)
if ref_element is not None and "target" in ref_element.attrib:
    target = ref_element.attrib["target"]
    ref_num = target.rsplit("/", 1)[-1]
    physDesc_id = ref_num

p_elements = root.findall(".//tei:p", NS)
p_contents = []
numbered_contents = []

extracted_data = {"places": [],
                  "ropanī": [],
                  "culas": []}

for p_element in p_elements:
    # Initialize flags to track whether tags are encountered
    foreign_tag_found = False
    place_name_tag_found = False

    # Iterate through child elements of the <p> element
    for child in p_element:
        if child.tag.endswith('foreign'):
            foreign_tag_found = True
        elif child.tag.endswith('placeName'):
            place_name_tag_found = True

  
    p_content = ''.join(p_element.itertext()).strip()


    if foreign_tag_found and place_name_tag_found:
        p_contents.append({
            'p content': p_content
        })

        p_places = p_element.findall('{http://www.tei-c.org/ns/1.0}placeName')
        extracted_data["places"].append(p_places[0].text)
        
        ropanis_pattern = re.compile(r'\s*(\d+)\s*ropanīs', re.IGNORECASE)
        culas_pattern = re.compile(r'\s*(\d+)\s*culas', re.IGNORECASE)
        
        num_ropanis = extract_numbers(p_content, ropanis_pattern)
        num_culas = extract_numbers(p_content, culas_pattern)

        extracted_data['ropanī'].append(num_ropanis)
        extracted_data['culas'].append(num_culas)

        numbered_contents.append({
            'placeName': p_places[0].text,
            'ropanis': num_ropanis,
            'culas': num_culas
        })
    

with open(os.path.join(os.getcwd(), "output", "extracted_p_contents"), 'w') as json_file:
    json.dump(p_contents, json_file, indent=2, ensure_ascii=False)

with open(os.path.join(os.getcwd(), "output", "extracted_numbered_ontology"), 'w') as json_file:
    json.dump(numbered_contents, json_file, indent=2, ensure_ascii=False)
