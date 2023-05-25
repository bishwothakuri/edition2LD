import xml.etree.ElementTree as ET


def create_new_xml_tei(metadata):
    base_xml_file = "templates/base.xml"  # Path to the base XML-TEI template

    # Load the base XML template
    base_tree = ET.parse(base_xml_file)
    base_root = base_tree.getroot()

    # Find the relevant elements in the base XML
    list_person_element = base_root.find(".//{http://www.tei-c.org/ns/1.0}listPerson")
    list_place_element = base_root.find(".//{http://www.tei-c.org/ns/1.0}listPlace")
    term_list_element = base_root.find(".//{http://www.tei-c.org/ns/1.0}termList")

    # Add the extracted metadata to the appropriate elements in the base XML
    for person in metadata["persons"]:
        person_element = ET.SubElement(list_person_element, "{http://www.tei-c.org/ns/1.0}person")
        person_element.text = person

    for place in metadata["places"]:
        place_element = ET.SubElement(list_place_element, "{http://www.tei-c.org/ns/1.0}place")
        place_element.text = place

    for term in metadata["terms"]:
        term_element = ET.SubElement(term_list_element, "{http://www.tei-c.org/ns/1.0}term")
        term_element.text = term["term"]
        term_element.set("meaning", term["meaning"])

    # Return the modified XML tree
    return ET.tostring(base_root, encoding="utf-8")


    print("New XML-TEI file created successfully.")

