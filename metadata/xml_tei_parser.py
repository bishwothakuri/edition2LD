import json
import defusedxml.ElementTree as ET
from metadata.ont_item_mapper import extract_item_entity_id
from metadata.term_metadata_scraper import extract_term_meaning
# from metadata.place_metadata_scraper import extract_place_meaning


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
        tei_id = root.attrib[f"{{{NS['xml']}}}id"]
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
            "physDesc_id": None,
            "persons": [],
            "places": [],
            "terms": []
        }
        
        physDesc_id = root.find(".//tei:physDesc", NS)
        ref_element = physDesc_id.find(".//tei:ref", NS)
        if ref_element is not None and "target" in ref_element.attrib:
            target = ref_element.attrib["target"]
            ref_num = target.rsplit("/", 1)[-1]
            metadata["physDesc_id"] = ref_num

        for pers_name in pers_names:
            if pers_name.text is not None:
                pers_name_text = " ".join(pers_name.text.split())
                n_value = pers_name.get("n")
                metadata["persons"].append({"n": n_value, "person_name": pers_name_text})

        # Extract place names 
        ont_item_occurrences = extract_item_entity_id(tei_id, json_file)
        place_name_dict = {}

        for place_name in place_names:
            if place_name.text is not None:
                place_name_text = " ".join(place_name.text.split())
                n_value = place_name.get("n")
                ont_item_ids = ont_item_occurrences.get(n_value, [])
                for ont_item_id in ont_item_ids:
                    place_entry = place_name_dict.setdefault(
                        ont_item_id, {"primary_name": place_name_text, "alternative_names": []}
                    )
                    place_entry["alternative_names"].append(place_name_text)

        for ont_item_id, place_data in place_name_dict.items():
            place_entry = {"n": ont_item_id, "place_name": place_data["primary_name"]}
            alternative_names = place_data["alternative_names"]
            if alternative_names:
                place_entry["alternative_names"] = alternative_names
            # Extract the notes for each place
            # place_ref = ont_item_id.rsplit("/", 1)[-1]
            # place_entry["notes"] = extract_place_meaning(place_ref)
            # print(place_entry)
            metadata["places"].append(place_entry)

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
