import json
import defusedxml.ElementTree as ET
from metadata.term_metadata_scraper import extract_term_meaning


NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace"
}


def load_ont_item_occurrences(json_file):
    '''
    Loads the ont_item_occurrences JSON data from the specified file.
    '''
    with open(json_file, "r") as file:
        data = json.load(file)
    return data


def get_ont_item_ids(n_value, ont_item_occurrences, matching_xml_identifier):
    '''
    Retrieves the ont_item_id for a given n_value from the ont_item_occurrences data
    with the matching xml_identifier value.
    '''
    ont_item_ids = []
    for item in ont_item_occurrences:
        if item.get("xml_identifier") == matching_xml_identifier and item.get("xml_entity_id") == n_value:
            ont_item_ids.append(item.get("ont_item_id"))
    return ont_item_ids


def extract_metadata_from_xml(xml_file, json_file):
    try:
        ont_item_occurrences = load_ont_item_occurrences(json_file)

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

        # Find the matching XML identifier from the JSON file
        matching_xml_identifier = None
        for item in ont_item_occurrences:
            if item.get("xml_identifier") == tei_id:
                matching_xml_identifier = item.get("xml_identifier")
                break

        dict_ont_id = {}
        for item in ont_item_occurrences:
            if item['type'] == 'table' and item['name'] == 'ont_item_occurrences':
                for entry in item['data']:
                    if entry['xml_identifier'] == tei_id:
                        ont_item_id = entry['ont_item_id']
                        xml_entity_id = entry['xml_entity_id']
                        if ont_item_id not in dict_ont_id:
                            dict_ont_id[ont_item_id] = []
                        dict_ont_id[ont_item_id].append(xml_entity_id)
        
        for pers_name in pers_names:
            if pers_name.text is not None:
                pers_name_text = " ".join(pers_name.text.split())
                n_value = pers_name.get("n")
                metadata["persons"].append({"n": n_value, "person_name": pers_name_text})

        for place_name in place_names:
            if place_name.text is not None:
                place_name_text = " ".join(place_name.text.split())
                n_value = place_name.get("n")
                if matching_xml_identifier:
                    ont_item_ids = get_ont_item_ids(n_value, ont_item_occurrences, matching_xml_identifier)
                    metadata["places"].append({"n": ", ".join(ont_item_ids), "place_name": place_name_text})

        for term in terms:
            if term.text is not None:
                term_text = " ".join(term.text.split())
                term_ref = term.get("ref")
                term_meaning = extract_term_meaning(base_url, term_ref)
                metadata["terms"].append({"term": term_text, "meaning": term_meaning})

        print("Metadata extracted successfully from XML file.")
        print(metadata)
        return metadata

    except Exception as e:
        print("Error generating XML-TEI file:", e)
        return None
