import json
import defusedxml.ElementTree as ET
from metadata.ont_item_mapper import extract_item_entity_id

# from metadata.term_metadata_scraper import extract_term_meaning


NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


def extract_metadata_from_xml(xml_file, json_file):
    try:
        base_url = "https://nepalica.hadw-bw.de/nepal/words/viewitem/"
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract the id attribute from the root element
        tei_id = root.attrib["{" + NS["xml"] + "}id"]
        place_names = root.findall(
            ".//tei:placeName", {"tei": "http://www.tei-c.org/ns/1.0"}
        )

        metadata = {"id": tei_id, "places": []}

        ont_item_occurrences = extract_item_entity_id(tei_id, json_file)
        place_name_dict = {}

        for place_name in place_names:
            if place_name.text is not None:
                place_name_text = " ".join(place_name.text.split())
                n_value = place_name.get("n")
                ont_item_ids = ont_item_occurrences.get(n_value, [])
                if ont_item_ids:
                    for ont_item_id in ont_item_ids:
                        if ont_item_id not in place_name_dict:
                            place_name_dict[ont_item_id] = {"primary_name": place_name_text, "alternative_names": []}
                        else:
                            place_name_dict[ont_item_id]["alternative_names"].append(place_name_text)

        for ont_item_id, place_data in place_name_dict.items():
            place_entry = {"n": ont_item_id, "place_name": place_data["primary_name"]}
            alternative_names = place_data["alternative_names"]
            if alternative_names:
                place_entry["alternative_names"] = alternative_names
            metadata["places"].append(place_entry)
        print("Metadata extracted successfully from XML file.")
        print(metadata)
        return metadata

    except Exception as e:
        print("Error generating XML-TEI file:", e)
        return None
