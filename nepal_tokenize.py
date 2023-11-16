import xml.etree.ElementTree as ET
import os
from rdflib import RDF, Graph, Literal, Namespace, URIRef, BNode


def judge_repetition(word, word_list):
    if not word_list:
        return None
    
    for i, item in enumerate(word_list):
        if item == word:
            return i
    
    return None

# Load the XML file
NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

xml_file_path = os.path.join("data", "K_0440_0007.xml")
tree = ET.parse(xml_file_path)
root = tree.getroot()


DOI = root.get("{http://www.w3.org/XML/1998/namespace}id").lower()

#get physDesc_id
physDesc_id = root.find(".//tei:physDesc", NS)
ref_element = physDesc_id.find(".//tei:ref", NS)
if ref_element is not None and "target" in ref_element.attrib:
    target = ref_element.attrib["target"]
    ref_num = target.rsplit("/", 1)[-1]
    physDesc_id = ref_num

# Find all the <w> elements
w_elements = root.findall(".//tei:w", NS)
w_list = []

g = Graph()

nepaltokens = Namespace("http://example.com/nepaltokens")
ontolex = Namespace("http://www.w3.org/ns/lemon/ontolex#")

g.bind('ontolex', ontolex)

# Add an id attribute to each <w> element
for i, w_element in enumerate(w_elements, start=1):
    w = w_element.text
    index = judge_repetition(w, w_list)
    if index == None:
        w_list.append(w)
        w_element.set("id", f"w_{len(w_list)}")
    else:
        w_element.set("id", f"w_{index}")


for i, word in enumerate(w_list):
    format_id = "{:06}".format(i+1)
    nepaltokens_node = URIRef(f"nepalica:{physDesc_id}#ne{format_id}")
    g.add((nepaltokens_node, ontolex.Form, Literal(word, lang = "ne")))


# Save the modified XML to a new file
tree.write("modified_xml_file.xml", encoding="utf-8", xml_declaration=True, default_namespace="")


rdf_xml_output_file_path = os.path.join(os.getcwd(), "output", "nepaltokens.ttl")
g.serialize(rdf_xml_output_file_path, format="turtle")


