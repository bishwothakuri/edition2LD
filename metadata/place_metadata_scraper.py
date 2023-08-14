import requests
from bs4 import BeautifulSoup
import re

def extract_item_note(ontology_url, ont_item_id):
    response = requests.get(ontology_url + ont_item_id)
    soup = BeautifulSoup(response.content, "html.parser")
    notes_row = soup.find_all('tr')
    notes_text = ' '
    for row in notes_row:
        data = [x.text.strip() for x in row.find_all('td')]
        if 'Notes' in data:
            notes_text = data[1]
    return notes_text

def extract_lod_identifiers_from_note(notes_text):
    '''
    Use regular expressions to extract content of specific identifier
    Input: notes_text
    Output: dictionary includes indentifier name and correspoinding content

    Reference example: https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/178
    '''
    gnd_pattern = r'gnd:(\d+)'
    viaf_pattern = r'viaf:(\d+)'
    wiki_pattern = r'wiki:(\S+)'
    dbr_pattern = r'dbr:(\S+)'
    geonames_pattern = r'geonames:(\d+)'

    gnd_match = re.search(gnd_pattern, notes_text)
    viaf_match = re.search(viaf_pattern,notes_text)
    wiki_match = re.search(wiki_pattern, notes_text)
    dbr_match = re.search(dbr_pattern, notes_text)
    geonames_match = re.search(geonames_pattern, notes_text)

    gnd_content = gnd_match.group(1) if gnd_match else None
    viaf_content = viaf_match.group(1) if viaf_match else None
    wiki_content = wiki_match.group(1) if wiki_match else None
    dbr_content = dbr_match.group(1) if dbr_match else None
    geonames_content = geonames_match.group(1) if geonames_match else None
    

    #print("gnd:", gnd_content)
    #print("viaf:", viaf_content)
    #print("wiki:", wiki_content)

    content_dict = {"gnd": gnd_content, "viaf": viaf_content, "wiki": wiki_content, "dbr": dbr_content, "geonames": geonames_content}
    # print(content_dict)

    keys = content_dict.keys()
    elements = [content_dict[key] for key in keys]

    return keys, elements


def clean_note_text(note_text):
    # Remove square brackets and URI patterns like [gnd:1234], [viaf:5678], etc.
    cleaned_text = re.sub(r'\[[^\]]+\]', '', note_text)
    
    # Remove URI patterns like gnd:1234, viaf:5678, etc.
    cleaned_text = re.sub(r'\b(?:gnd|viaf|wiki|dbr|geonames):\S+\b', '', cleaned_text)
    
    # Replace multiple whitespace characters with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Remove leading and trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text