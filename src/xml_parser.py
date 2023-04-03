import defusedxml.ElementTree as ET

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def extract_metadata(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    persNames = root.findall(".//tei:persName", NS)
    placeNames = root.findall(".//tei:placeName", NS)
    terms = root.findall(".//tei:term", NS)

    metadata = {"persons": [], "places": [], "terms": []}

    for p in persNames:
        if p.text is not None:
            p_text = " ".join(p.text.split())
            metadata["persons"].append(p_text)

    for pl in placeNames:
        if pl.text is not None:
            pl_text = " ".join(pl.text.split())
            metadata["places"].append(pl_text)

    for t in terms:
        if t.text is not None:
            t_text = " ".join(t.text.split())
            metadata["terms"].append(t_text)

    print("Metadata extracted successfully from XML file.")
    print(metadata)
    return metadata
