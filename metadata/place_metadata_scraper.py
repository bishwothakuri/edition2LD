import requests
from bs4 import BeautifulSoup
import re

def extract_item_note(ontology_url, ont_item_id):
    response = requests.get(ontology_url + ont_item_id)
    soup = BeautifulSoup(response.content, "html.parser")
    notes_row = soup.find_all('tr')
    note_text = ' '
    for row in notes_row:
        data = [x.text.strip() for x in row.find_all('td')]
        if 'Notes' in data:
            note_text = data[1]
            
    return note_text

def extract_lod_identifiers_from_note(note_text):
    '''
    Use regular expressions to extract content of specific identifier
    Input: note_text
    Output: dictionary includes indentifier name and correspoinding content

    Reference example: https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/178
    '''
    #gnd_pattern = r'gnd:(\d+),|gnd:(\d+).|gnd:(\d+-\d+),|gnd:(\d+-\d+).'
    gnd_pattern = r'gnd:(\d+(?:-\d+)?).|gnd:(\d+(?:-\d+)?),'
    viaf_pattern = r'viaf:(\d+),|viaf:(\d+).'
    wiki_pattern = r'wiki:(\S+),|wiki:(\S+).'
    geonames_pattern = r'geonames:(\d+),|geonames:(\d+).|geonames:\s+(\d+),|geonames:\s+(\d+).'
    dbr_pattern = r'dbr:(\S+),|dbr:(\S+).'
    wikidata_pattern = r'wikidata:(\S+),|wikidata:(\S+).'


    # Replace multiple spaces with a single space
    note_text = re.sub(r'\s+', ' ', note_text)

    gnd_match = re.findall(gnd_pattern, note_text)
    viaf_match = re.findall(viaf_pattern, note_text)
    dbr_match = re.findall(dbr_pattern, note_text)
    wiki_match = re.findall(wiki_pattern, note_text)
    wikidata_match = re.findall(wikidata_pattern, note_text)
    geos_match = re.findall(geonames_pattern, note_text)

    note_text = re.sub(gnd_pattern, '', note_text)
    note_text = re.sub(viaf_pattern, '', note_text)
    note_text = re.sub(dbr_pattern, '', note_text)
    note_text = re.sub(wiki_pattern, '', note_text)
    note_text = re.sub(geonames_pattern, '', note_text)

    gnd_content = [item.strip('.').strip() for match in gnd_match for item in match if item]
    viaf_content = [item.strip('.').strip() for match in viaf_match for item in match if item]
    dbr_content = [item.strip('.').strip() for match in dbr_match for item in match if item]
    wiki_content = [item.strip('.').strip() for match in wiki_match for item in match if item]
    wikidata_content = [item.strip('.').strip() for match in wikidata_match for item in match if item]
    geonames_content = [item.strip('.').strip() for match in geos_match for item in match if item]

    #Delete #... until end of entry-no matter what comes after it
    checked_index = note_text.find("#")
    note_text = note_text[:checked_index]
    '''
    checked_index = note_text.find("#checked#")
    if checked_index != -1:
        note_text = note_text[:checked_index]
    
    # Remove #new#
    note_text = note_text.replace('#new#', '')
    '''
    # Remove leading and trailing spaces
    note_text = note_text.strip()

    content_dict = {"gnd": gnd_content, "viaf": viaf_content, "wiki": wiki_content, "wikidata": wikidata_content, "dbr": dbr_content, "geonames": geonames_content}
    keys = content_dict.keys()
    elements = [content_dict[key] for key in keys]

    return keys, elements, note_text
