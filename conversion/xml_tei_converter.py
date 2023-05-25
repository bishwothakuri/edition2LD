import xml.etree.ElementTree as ET

def create_new_xml_tei(metadata):
    base_xml_file = "templates/base.xml"  # Path to the base XML-TEI template

    # Load the base XML template
    base_tree = ET.parse(base_xml_file)
    base_root = base_tree.getroot()

    # Find the relevant elements in the base XML
    ns = {"ns0": "http://www.tei-c.org/ns/1.0"}  # Namespace dictionary
    list_person_element = base_root.find(".//ns0:listPerson", ns)
    list_place_element = base_root.find(".//ns0:listPlace", ns)
    term_list_element = base_root.find(".//ns0:termList", ns)

    # Sort terms based on a key such as term or index
    # sorted_terms = sorted(metadata["terms"], key=lambda x: x["term"])

    # Add the extracted metadata to the appropriate elements in the base XML
    for i, person in enumerate(metadata["persons"]):
        person_element = ET.SubElement(list_person_element, "persName", attrib={"n": str(i)})
        person_element.text = person
        

    for place in metadata["places"]:
        place_element = ET.SubElement(list_place_element, "{http://www.tei-c.org/ns/1.0}placeName")
        place_element.text = place

    for term in metadata["terms"]:
        term_element = ET.SubElement(term_list_element, "{http://www.tei-c.org/ns/1.0}term")
        # term_element.text = term["term"]
        # term_element.set("meaning", term["meaning"])

        # Create orth and def elements inside term element
        orth_element = ET.SubElement(term_element, "{http://www.tei-c.org/ns/1.0}orth")
        orth_element.text = term["term"]
        def_element = ET.SubElement(term_element, "{http://www.tei-c.org/ns/1.0}def")
        def_element.text = term["meaning"]

    # Return the modified XML tree
    return ET.tostring(base_root, encoding="utf-8")
