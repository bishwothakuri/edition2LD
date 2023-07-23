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
