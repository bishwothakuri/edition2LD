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

    tei_element = base_xml_tree
    xml_id_element = base_xml_tree.find(".//id", namespace_dict)
    title_main_element = base_xml_tree.find(
        ".//tei:title[@type='main']", namespace_dict
    )
    title_short_element = base_xml_tree.find(
        ".//tei:title[@type='short']", namespace_dict
    )
    title_sub_element = base_xml_tree.find(".//tei:title[@type='sub']", namespace_dict)
    author_role_issuer_element = base_xml_tree.find(
        ".//tei:author[@role='issuer']", namespace_dict
    )
    main_editor_element = base_xml_tree.find(
        ".//tei:name[@type='main_editor']", namespace_dict
    )

    ref_element = base_xml_tree.find(".//tei:ref", namespace_dict)
    person_list_element = base_xml_tree.find(
        ".//tei:list[@type='person']", namespace_dict
    )
    place_list_element = base_xml_tree.find(
        ".//tei:list[@type='place']", namespace_dict
    )
    term_list_element = base_xml_tree.find(".//tei:list[@type='gloss']", namespace_dict)

    # Set the xml:id dynamically
    if "id" in metadata:
        base_xml_tree.attrib["{" + namespace_dict["xml"] + "}id"] = metadata["id"]

    # Set the values of title elements dynamically
    for title_type in ["main", "short", "sub"]:
        title_element = base_xml_tree.find(
            f".//tei:title[@type='{title_type}']", namespace_dict
        )
        if f"title_{title_type}" in metadata:
            title_element.text = metadata[f"title_{title_type}"]

    # Set the value of author element dynamically
    if "author_role_issuer" in metadata:
        author_role_issuer_element.text = metadata["author_role_issuer"]

    # Set the value of main editor dynamically
    if "main_editor" in metadata:
        main_editor_element.text = metadata["main_editor"]

    # Set the physDesc_ref_target dynamically
    if "physDesc_ref_target" in metadata and ref_element is not None:
        ref_element.set("target", metadata["physDesc_ref_target"])

    # Add the extracted metadata to the appropriate elements in the base XML
    for i, person in enumerate(metadata["persons"]):
        person_element = ET.SubElement(
            person_list_element, "persName", attrib={"n": person["n"]}
        )
        person_element.text = person["person_name"]

    for i, place in enumerate(metadata["places"]):
        place_element = ET.SubElement(
            place_list_element, "placeName", attrib={"n": place["n"]}
        )
        place_element.text = place["place_name"]

    for term in metadata["terms"]:
        term_element = ET.SubElement(
            term_list_element, "{http://www.tei-c.org/ns/1.0}term"
        )
        label_element = ET.SubElement(
            term_element, "{http://www.tei-c.org/ns/1.0}label"
        )
        label_element.text = term["term"]
        def_element = ET.SubElement(term_element, "{http://www.tei-c.org/ns/1.0}def")
        def_element.text = term["meaning"]

    # Serialize the XML tree to bytes with the declaration
    xml_bytes = ET.tostring(base_xml_tree, encoding="utf-8", xml_declaration=True)
    xml_bytes = xml_bytes.replace(b"ns0:", b"")

    return xml_bytes