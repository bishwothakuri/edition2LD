import lxml.etree as ET


def generate_xml_tei_from_metadata(metadata):
    base_xml_filepath = "templates/base.xml"  # Path to the base XML-TEI template

    # Load the base XML template
    with open(base_xml_filepath, "r") as file:
        base_xml_content = file.read()

    # Replace the placeholder with the actual id value
    xml_content = base_xml_content.replace("{{id}}", metadata.get("id", ""))

    # Encode the XML content as bytes
    xml_bytes = xml_content.encode("utf-8")

    # Parse the modified XML content
    base_xml_tree = ET.fromstring(xml_bytes)

    # Find the relevant elements in the base XML
    namespace_dict = {
        "tei": "http://www.tei-c.org/ns/1.0",
        "xml": "http://www.w3.org/XML/1998/namespace",
    }

    # Set the xml:id dynamically
    if "id" in metadata:
        base_xml_tree.attrib[f"{{{namespace_dict['xml']}}}id"] = metadata["id"]

    # Set the values of title elements dynamically
    for title_type in ["main", "short", "sub"]:
        title_element = base_xml_tree.find(
            f".//tei:title[@type='{title_type}']", namespace_dict
        )
        if f"title_{title_type}" in metadata:
            title_element.text = metadata[f"title_{title_type}"]

    # Set the value of author element dynamically
    if "author_role_issuer" in metadata:
        author_role_issuer_element = base_xml_tree.find(
            ".//tei:author[@role='issuer']", namespace_dict
        )
        author_role_issuer_element.text = metadata["author_role_issuer"]

    # Set the value of main editor dynamically
    if "main_editor" in metadata:
        main_editor_element = base_xml_tree.find(
            ".//tei:name[@type='main_editor']", namespace_dict
        )
        main_editor_element.text = metadata["main_editor"]

    # Set the physDesc_ref_target dynamically
    if "physDesc_id" in metadata:
        ref_element = base_xml_tree.find(".//tei:ref", namespace_dict)
        if ref_element is not None:
            ref_element.set("target", f"#p{metadata['physDesc_id']}")

    # Add the extracted metadata to the appropriate elements in the base XML
    person_list_element = base_xml_tree.find(".//tei:list[@type='person']", namespace_dict)
    place_list_element = base_xml_tree.find(".//tei:list[@type='place']", namespace_dict)
    term_list_element = base_xml_tree.find(".//tei:list[@type='gloss']", namespace_dict)

    # Add persons using list comprehension and SubElement
    for person in metadata["persons"]:
        person_element = ET.SubElement(
            person_list_element, "persName", attrib={"n": person["n"]}
        )
        person_element.text = person["person_name"]

    # Add places using list comprehension and SubElement
    for place in metadata["places"]:
        place_element = ET.SubElement(
            place_list_element, "{http://www.tei-c.org/ns/1.0}placeName", attrib={"n": place["n"]}
        )
        primary_name_element = ET.SubElement(place_element, "{http://www.tei-c.org/ns/1.0}placeName")
        primary_name_element.text = place["place_name"]

        for alt_name in place.get("alternative_names", []):
            alt_name_element = ET.SubElement(place_element, "{http://www.tei-c.org/ns/1.0}altName")
            alt_name_element.text = alt_name

    # Add terms using list comprehension and SubElement
    for term in metadata["terms"]:
        term_element = ET.SubElement(
            term_list_element, "{http://www.tei-c.org/ns/1.0}term"
        )
        label_element = ET.SubElement(
            term_element, "{http://www.tei-c.org/ns/1.0}prefLabel"
        )
        label_element.text = term["prefLabel"]
        def_element = ET.SubElement(term_element, "{http://www.tei-c.org/ns/1.0}def")
        def_element.text = term["meaning"]

        for alt_label in term.get("altLabel", []):
            alt_label_element = ET.SubElement(
                term_element, "{http://www.tei-c.org/ns/1.0}altLabel"
            )
            alt_label_element.text = alt_label

    # Serialize the XML tree to bytes with the declaration
    xml_bytes = ET.tostring(base_xml_tree, encoding="utf-8", xml_declaration=True)
    xml_bytes = xml_bytes.replace(b"ns0:", b"")

    return xml_bytes
