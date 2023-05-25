import defusedxml.ElementTree as ET

from metadata.term_metadata_scraper import extract_term_meaning

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def extract_metadata(xml_file):
    base_url = "https://nepalica.hadw-bw.de/nepal/words/viewitem/"
    tree = ET.parse(xml_file)
    root = tree.getroot()

    persNames = root.findall(".//tei:persName", NS)
    placeNames = root.findall(".//tei:placeName", NS)
    terms = root.findall(".//tei:term", NS)

    metadata = {"persons": [], "places": [], "terms": []}

    for persName in persNames:
        if persName.text is not None:
            persName_text = " ".join(persName.text.split())
    
    
            metadata["persons"].append(persName_text)
    
    for placeName in placeNames:
        if placeName.text is not None:
            placeName_text = " ".join(placeName.text.split())
            metadata["places"].append(placeName_text)

    for term in terms:
        if term.text is not None:
            term_text = " ".join(term.text.split())
            term_ref = term.get("ref")
            # Call extract_term_meaning to get the meaning of the term
            term_meaning = extract_term_meaning(base_url, term_ref)
            metadata["terms"].append({"term": term_text, "meaning": term_meaning})

    print("Metadata extracted successfully from XML file.")
    return metadata
