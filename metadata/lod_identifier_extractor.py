import json
from typing import Dict


def extract_place_identifiers(json_file_path: str, n: str) -> Dict[str, str]:
    with open(json_file_path, "r") as f:
        data = json.load(f)

    ont_data = data.get("ont_data", [])
    place_identifiers = {}

    for identifier in ont_data:
        if identifier["ont_item_id"] == n:
            place_identifiers = {
                "ont_item_id": identifier["ont_item_id"],
                "geonames": identifier["geonames"],
                "dbr": identifier["dbr"],
                "wiki": identifier["wiki"],
                "wikidata": identifier["wikidata"],
                "viaf": identifier["viaf"],
                "gnd": identifier["gnd"]
            }
            break
    return place_identifiers



def extract_person_identifiers(json_file_path: str, n: str) -> Dict[str, str]:
    with open(json_file_path, "r") as f:
        data = json.load(f)

    ont_data = data.get("ont_data", [])
    person_identifiers = {}

    for identifier in ont_data:
        if identifier["ont_item_id"] == n:
            person_identifiers = {
                "ont_item_id": identifier["ont_item_id"],
                "geonames": identifier["geonames"],
                "dbr": identifier["dbr"],
                "wiki": identifier["wiki"],
                "wikidata": identifier["wikidata"],
                "viaf": identifier["viaf"],
                "gnd": identifier["gnd"]
            }
            break
    return person_identifiers



def extract_term_identifiers(json_file_path: str, term_ref: str) -> Dict[str, str]:
    with open(json_file_path, "r") as f:
        data = json.load(f)

    word_data = data.get("word_data", [])
    term_identifiers = {}

    for identifier in word_data:
        if identifier["id"] == term_ref:
            term_identifiers = {
                "id": identifier["id"],
                "geonames": identifier["geonames"],
                "dbr": identifier["dbr"],
                "wiki": identifier["wiki"],
                "wikidata": identifier["wikidata"],
                "viaf": identifier["viaf"],
                "gnd": identifier["gnd"]
            }
            break
    return term_identifiers


