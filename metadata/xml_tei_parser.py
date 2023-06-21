import defusedxml.ElementTree as ET
from metadata.term_metadata_scraper import extract_term_meaning

NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace"

    }

def extract_metadata_from_xml(xml_file):
    base_url = "https://nepalica.hadw-bw.de/nepal/words/viewitem/"
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Extract the id attribute from the root element
    tei_id = root.attrib["{" + NS["xml"] + "}id"]
    title_main = root.find(".//tei:title[@type='main']", NS).text
    title_short = root.find(".//tei:title[@type='short']", NS).text
    title_sub = root.find(".//tei:title[@type='sub']", NS).text
    author_role_issuer = root.find(".//tei:author[@role='issuer']", NS).text
    main_editor = root.find(".//tei:respStmt/tei:name[@type='main_editor']", NS).text

    pers_names = root.findall(".//tei:persName", NS)
    place_names = root.findall(".//tei:placeName", NS)
    terms = root.findall(".//tei:term", NS)
    ref_element = root.find(".//tei:physDesc//tei:ref", NS)

    metadata = {
        "id": tei_id,
        "title_main": title_main,
        "title_short": title_short,
        "title_sub": title_sub,
        "author_role_issuer": author_role_issuer,
        "main_editor": main_editor,
        "physDesc_ref_target": None,
        "persons": [],
        "places": [],
        "terms": []
    }

    if ref_element is not None:
        physDesc_ref_target = ref_element.attrib["target"]
        metadata["physDesc_ref_target"] = physDesc_ref_target

    for pers_name in pers_names:
        if pers_name.text is not None:
            pers_name_text = " ".join(pers_name.text.split())
            metadata["persons"].append(pers_name_text)
    
    for place_name in place_names:
        if place_name.text is not None:
            place_name_text = " ".join(place_name.text.split())
            metadata["places"].append(place_name_text)

    for term in terms:
        if term.text is not None:
            term_text = " ".join(term.text.split())
            term_ref = term.get("ref")
            term_meaning = extract_term_meaning(base_url, term_ref)
            metadata["terms"].append({"term": term_text, "meaning": term_meaning})

    print("Metadata extracted successfully from XML file.")
    print(metadata)
    return metadata
