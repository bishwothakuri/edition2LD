import os
import defusedxml.ElementTree as ET
from metadata.ont_item_mapper import extract_item_entity_id
from metadata.term_metadata_scraper import extract_term_meaning
from metadata.lod_identifier_extractor import (
    extract_term_identifiers,
    extract_place_identifiers
)
from metadata.place_metadata_scraper import (
    extract_item_note,
    extract_lod_identifiers_from_note
)


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

        ont_item_occurrences = extract_item_entity_id(tei_id, json_file)

        # Extract person names
        pers_name_dict = {}
        for pers_name in pers_names:
            if pers_name.text is not None:
                pers_name_text = " ".join(pers_name.text.split())
                n_value = pers_name.get("n")
                ont_item_ids = ont_item_occurrences.get(n_value, [])
                for ont_item_id in ont_item_ids:
                    pers_entry = pers_name_dict.setdefault(
                        ont_item_id, {"primary_name": pers_name_text, "alternative_names": []}
                        )
                    pers_entry["alternative_names"].append(pers_name_text) 
        
        #metadata["persons"].append({"n": n_value, "person_name": pers_name_text})
        for ont_item_id, pers_data in pers_name_dict.items():
            pers_entry = {"n": ont_item_id, "person_name": pers_data["primary_name"]}
            alternative_names = pers_data["alternative_names"]
            if alternative_names:
                pers_entry["alternative_names"] = alternative_names
            notes_text = extract_item_note(ontology_url, ont_item_id).replace('\n',' ').replace('\r',' ').replace('\t',' ')
            

            keys, elements, notes_text = extract_lod_identifiers_from_note(notes_text)
            pers_entry["notes"] =notes_text

            for key, element in zip(keys, elements):
                pers_entry[key] = element
                metadata["persons"].append(pers_entry)

                # metadata["persons"].append({"n": n_value, "person_name": pers_name_text})


        # Extract place names 
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
            # Extract the place LOD identifiers using the ont_item_id
            ont_items_enhanced_file_path = os.path.join("data", "ont_items_enhanced_sample.json")
            place_identifiers = extract_place_identifiers(ont_items_enhanced_file_path, ont_item_id)
            if place_identifiers:
                # Update the place_entry with the extracted LOD identifiers
                place_entry.update(place_identifiers)
            # Extract the place LOD identifiers from notes using the first method
            notes_text = extract_item_note(ontology_url, ont_item_id).replace('\n',' ').replace('\r',' ').replace('\t',' ')
            keys, elements, notes_text = extract_lod_identifiers_from_note(notes_text)
            
            for key, element in zip(keys, elements):
                if element is not None:
                    place_entry[key] = element
                else:
                    # If the value is None, try the second method
                    ont_items_enhanced_file_path = os.path.join("data", "ont_items_enhanced_sample.json")
                    place_identifiers = extract_place_identifiers(ont_items_enhanced_file_path, ont_item_id)
                    if place_identifiers.get(key) is not None:
                        place_entry[key] = place_identifiers[key]
            
            place_entry["note_text"] = notes_text
            metadata["places"].append(place_entry)

        # Initialize an empty dictionary to store terms
        terms_dict = {}
        # Loop through each term in the list of terms
        for term in terms:
            if term.text is not None:
                term_text = " ".join(term.text.split())
                term_ref = term.get("ref")
                # Extract the meaning of the term using its reference
                term_meaning = extract_term_meaning(base_url, term_ref)
                # Check if the term reference is already present in the terms_dict
                if term_ref not in terms_dict:
                    terms_dict[term_ref] = {
                        "prefLabel": term_text,
                        "meaning": term_meaning,
                        "altLabel": []
                    }
                else:
                    # Check if the term_text is not already in pefLabel, then append
                    if term_text != terms_dict[term_ref]["prefLabel"]:
                        terms_dict[term_ref]["altLabel"].append(term_text)
        
        # Loop through the collected term information in terms_dict
        for term_ref, term_data in terms_dict.items():
            pref_label = term_data["prefLabel"]
            alt_labels = term_data["altLabel"]
            meaning = term_data["meaning"]
        
            term_entry = {"term_ref": term_ref, "prefLabel": pref_label, "meaning": meaning}
                
            # Add altLabel if it exists
            if alt_labels:
                term_entry["altLabel"] = alt_labels
            
            # Extract the term identifiers using the term_ref
            words_enhanced_file_path = os.path.join("data", "words_enhanced_sample.json")
            term_identifiers = extract_term_identifiers(words_enhanced_file_path, term_ref)
            if term_identifiers:
                term_entry.update(term_identifiers)
        
            metadata["terms"].append(term_entry)

        print("Metadata extracted successfully from XML file.")
        print(metadata)
        return metadata

    except Exception as e:
        print("Error extracting metadata:", e)
        return None
