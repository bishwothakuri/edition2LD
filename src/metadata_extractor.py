import defusedxml.ElementTree as ET

from .extract_term_meaning import extract_term_meaning

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def extract_metadata(file_path):
    base_url = "https://nepalica.hadw-bw.de/nepal/words/viewitem/"

    # Parse the XML-TEI file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Initialize an empty list to hold the extracted metadata
    metadata = []

    # Extract all the 'persName' elements using XPath
    persNames = root.findall(".//tei:persName", NS)
    for persName in persNames:
        # Extract the 'text' of the 'persName' element
        persName_text = persName.text.strip() if persName is not None else ""

        # Append the extracted metadata to the list
        metadata.append(
            {
                "type": "persName",
                "text": persName_text,
            }
        )

    # Extract all the 'placeName' elements using XPath
    placeNames = root.findall(".//tei:placeName", NS)
    for placeName in placeNames:
        # Extract the 'text' of the 'placeName' element
        placeName_text = placeName.text.strip() if placeName is not None else ""

        # Append the extracted metadata to the list
        metadata.append(
            {
                "type": "placeName",
                "text": placeName_text,
            }
        )

    # Extract all the 'term' elements using XPath
    terms = root.findall(".//tei:term", NS)
    for term in terms:
        # Extract the 'text' of the 'term' element
        term_text = term.text.strip() if term is not None else ""

        # Extract the 'ref' attribute of the 'term' element
        term_ref = term.get("ref")

        # Call extract_term_meaning to get the meaning of the term
        term_meaning = extract_term_meaning(term_ref, base_url)

        # Append the extracted metadata to the list
        metadata.append(
            {
                "type": "term",
                "text": term_text,
                "meaning": term_meaning,
            }
        )
    print("-------------- Metadata extracted successfully --------------")
    print(metadata)
    # Return the extracted metadata
    return metadata
