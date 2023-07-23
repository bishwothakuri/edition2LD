import json
from typing import Dict


def extract_term_identifiers(json_file_path: str, term_ref: str) -> Dict[str, str]:
    with open(json_file_path, "r") as f:
        data = json.load(f)

    word_data = data.get("word_data", [])
    term_identifiers = {}

    for term in word_data:
        if term["id"] == term_ref:
            term_identifiers = {
                "id": term["id"],
                "geonames": term["geonames"],
                "dbr": term["dbr"],
                "wiki": term["wiki"],
                "wikidata": term["wikidata"],
                "viaf": term["viaf"],
                "gnd": term["gnd"]
            }
            break

    return term_identifiers


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
