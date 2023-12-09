import os
import re
import defusedxml.ElementTree as ET
from metadata.ont_item_mapper import extract_item_entity_id
from metadata.term_metadata_scraper import extract_term_meaning
from metadata.lod_identifier_extractor import (
    extract_term_identifiers,
    extract_place_identifiers,
    extract_person_identifiers
)
from metadata.webcrawler import (
    extract_additional_info_from_note,
    extract_item_note_and_surname,
    extract_metadata_of_the_document
)
from metadata.ontology_query_tool import process_query_by_id


NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


def extract_metadata_from_xml(xml_file, json_file):
    try:
        base_url = "https://nepalica.hadw-bw.de/nepal/words/viewitem/"
        ontology_url = "https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/"
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract the id attribute from the root element
        tei_id = root.attrib[f"{{{NS['xml']}}}id"]
        title_main = root.find(".//tei:title[@type='main']", NS).text
        title_short = root.find(".//tei:title[@type='short']", NS).text
        title_sub = root.find(".//tei:title[@type='sub']", NS).text
        author_role_issuer = root.find(".//tei:author[@role='issuer']", NS).text
        main_editor = root.find(".//tei:respStmt/tei:name[@type='main_editor']", NS).text

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
            "document_metadata": None,
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
        
        # Call extract_metadata_of_the_document wiht the physDesc_id
        document_metadata = extract_metadata_of_the_document(metadata["physDesc_id"]) or {}
        # Store the document metadata in the 'metadata' dictionary under "document_metadata" key
        metadata["document_metadata"] = document_metadata
       
        ont_item_occurrences = extract_item_entity_id(tei_id, json_file)

        # Extract person names and LOD identifiers
        name_dict = {}  # Dictionary to store names by ont_item_id
        for pers_name in root.findall(".//tei:persName", NS):
            n_value = pers_name.get("n", "")
            pers_name_text = " ".join([re.sub(r'\s+', ' ', w.text or "").strip() for w in pers_name.findall(".//tei:w", NS)] + [re.sub(r'\s+', ' ', pers_name.text or "").strip()])
            pers_name_text = pers_name_text.strip()

            # Check if there are tei:w elements inside persName
            label_name = "devanagari_name" if pers_name.findall(".//tei:w", NS) else "anglicized_name"

            # Retrieve ont_item_id based on xml_identifier
            ont_item_ids = ont_item_occurrences.get(n_value, [])

            # Group names by ont_item_id
            for ont_item_id in ont_item_ids:
                if ont_item_id not in name_dict:
                    name_dict[ont_item_id] = {"n": ont_item_id}

                if label_name == "devanagari_name":
                    name_dict[ont_item_id][label_name] = pers_name_text
                else:
                    name_info = name_dict.setdefault(ont_item_id, {"n": n_value})
                    if "anglicized_name" not in name_info:
                        name_info["anglicized_name"] = pers_name_text
                    else:
                        name_info.setdefault("alternative_names", []).append(pers_name_text)

        # Process the name_dict to assign the names correctly and extract LOD identifiers
        for ont_item_id, name_info in name_dict.items():
            metadata["persons"].append(name_info)

            # Call process_query_by_id with ont_item_id as individual_id and capture the results
            query_results = process_query_by_id(ont_item_id)

            # Check if query_results is not None before accessing it
            if query_results:
                for key, value in query_results.items():
                    if value is not None:
                        name_info[key] = value

            # Extract the LOD identifiers and gender from the note
            note_text_and_surname = extract_item_note_and_surname(ontology_url, ont_item_id)
            if note_text_and_surname is not None:
                note_text = note_text_and_surname["note_text"].replace('\n',' ').replace('\r',' ').replace('\t',' ')
                surname = note_text_and_surname["surname"]

                keys, elements, note_text = extract_additional_info_from_note(note_text)

                for key, element in zip(keys, elements):
                    if element is not None:
                        name_info[key] = [element] if not isinstance(element, list) else element

                    # Try to update LOD identifiers from the second method only if there are missing or empty
                    for key in ["gnd", "viaf", "wiki", "wikidata", "dbr", "geonames", "gender"]:
                        if not name_info.get(key):
                            ont_items_enhanced_file_path = os.path.join("data", "ont_items_enhanced_sample.json")
                            person_identifiers = extract_person_identifiers(ont_items_enhanced_file_path, ont_item_id)
                            if person_identifiers.get(key) is not None:
                                name_info[key] = [person_identifiers[key]] if not isinstance(person_identifiers[key], list) else person_identifiers[key]

                name_info["note_text"] = note_text
                name_info["surname"] = surname

        # Extract place names 
        place_name_dict = {}

        for place_name in root.findall(".//tei:placeName", NS):
            n_value = place_name.get("n")
            place_name_text = " ".join([re.sub(r'\s+', ' ', w.text or "").strip() for w in place_name.findall(".//tei:w", NS)] + [re.sub(r'\s+', ' ', place_name.text or "").strip()])
            place_name_text = place_name_text.strip()

            # Check if there is tei:w element inside placeName
            label_name = "devanagari_name" if place_name.findall(".//tei:w", NS) else "primary_name"

            # Retrieve ont_item_id based on xml_identifier
            ont_item_ids = ont_item_occurrences.get(n_value, [])

            # Group place names by ont_item_id
            for ont_item_id in ont_item_ids:
                if ont_item_id not in place_name_dict:
                    place_name_dict[ont_item_id] = {"n": ont_item_id, "primary_name": "", "devanagari_name": "", "alternative_names": []}

                place_data = place_name_dict[ont_item_id]

                if label_name == "devanagari_name":
                    place_data[label_name] = place_name_text
                else:
                    if not place_data["primary_name"]:
                        place_data["primary_name"] = place_name_text
                    elif label_name == "primary_name" and place_data["primary_name"] != place_name_text:
                        place_data["alternative_names"].append(place_name_text)

        # Extracting metadata for each ont_item_id
        for ont_item_id, place_data in place_name_dict.items():
            place_entry = {"n": ont_item_id, "place_name": place_data["primary_name"]}

            # Adding devanagari_place_name if present
            devanagari_place_name = place_data["devanagari_name"]
            if devanagari_place_name:
                place_entry["devanagari_name"] = devanagari_place_name

            # Adding alternative_names if present
            alternative_names = place_data["alternative_names"]
            if alternative_names:
                place_entry["alternative_names"] = alternative_names

            # Extract the LOD identifiers and gender from the note
            note_text_and_surname = extract_item_note_and_surname(ontology_url, ont_item_id)
            if note_text_and_surname is not None:
                note_text = note_text_and_surname.get("note_text", "").replace('\n', ' ').replace('\r', ' ').replace('\t', '')


                keys, elements, note_text = extract_additional_info_from_note(note_text)

                for key, element in zip(keys, elements):
                    if element is not None:
                        place_entry[key] = [element] if not isinstance(element, list) else element

                # Try to update LOD identifiers from the second method only if they are missing or empty
                for key in ["gnd", "viaf", "wiki", "wikidata", "dbr", "geonames"]:
                    if not place_entry.get(key):
                        ont_items_enhanced_file_path = os.path.join("data", "ont_items_enhanced_sample.json")
                        place_identifiers = extract_place_identifiers(ont_items_enhanced_file_path, ont_item_id)
                        if place_identifiers.get(key) is not None:
                            place_entry[key] = [place_identifiers[key]] if not isinstance(place_identifiers[key], list) else place_identifiers[key]

                place_entry["note_text"] = note_text
                metadata["places"].append(place_entry)


        # Initialize an empty dictionary to store terms
        term_name_dict = {}

        # Loop through each term in the list of terms
        for term in terms:
            if term.text is not None:
                term_text = " ".join(term.text.split())
                term_ref = term.get("ref")

                # Extract the meaning of the term using its reference
                term_meaning = extract_term_meaning(base_url, term_ref)

                # Check if the term reference is already present in the term_name_dict
                if term_ref not in term_name_dict:
                    term_name_dict[term_ref] = {
                        "prefLabel": term_text,
                        "meaning": term_meaning,
                        "altLabel": []
                    }
                else:
                    # Check if the term_text is not already in prefLabel, then append
                    if term_text != term_name_dict[term_ref]["prefLabel"]:
                        term_name_dict[term_ref]["altLabel"].append(term_text)

        for term_ref, term_data in term_name_dict.items():
            pref_label = term_data["prefLabel"]
            alt_labels = term_data["altLabel"]
            meaning = term_data["meaning"]

            term_entry = {"term_ref": term_ref, "prefLabel": pref_label, "meaning": meaning}

            # Add altLabel if it exists
            if alt_labels:
                term_entry["altLabel"] = alt_labels

            # Extract the LOD identifiers from the second method
            ont_items_enhanced_file_path = os.path.join("data", "words_enhanced_sample.json")
            term_identifiers = extract_term_identifiers(ont_items_enhanced_file_path, term_ref)
            for key in ["gnd", "viaf", "wiki", "wikidata", "dbr", "geonames"]:
                if term_identifiers.get(key) is not None:
                    term_entry[key] = [term_identifiers[key]] if not isinstance(term_identifiers[key], list) else term_identifiers[key]

            metadata["terms"].append(term_entry)

        print("Metadata extracted successfully from XML file.")
        return metadata

    except Exception as e:
        print("Error extracting metadata:", e)
        return None
