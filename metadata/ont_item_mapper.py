import json

def extract_item_entity_id(tei_id, json_file):
    with open(json_file, 'r') as file:
        data_occurrences = json.load(file)

    dict_ont_id = {}

    for item in data_occurrences:
        if item.get('type') == 'table' and item.get('name') == 'ont_item_occurrences':
            for entry in item.get('data', []):
                if entry.get('xml_identifier') == tei_id:
                    ont_item_id = entry.get('ont_item_id')
                    xml_entity_id = entry.get('xml_entity_id')
                    dict_ont_id.setdefault(xml_entity_id, []).append(ont_item_id)

    return dict_ont_id
