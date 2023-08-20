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
    gnd_pattern = r'gnd:(\d+),|gnd:(\d+).|gnd:(\d+-\d+),|gnd:(\d+-\d+).'
    viaf_pattern = r'viaf:(\d+),|viaf:(\d+).'
    wiki_pattern = r'wiki:(\S+),|wiki:(\S+).'
    geonames_pattern = r'geonames:(\d+),|geonames:(\d+).|geonames:(\s+\d+),|geonames:(\s+\d+).'
    dbr_pattern = r'dbr:(\S+),|dbr:(\S+).'


    gnd_match = re.findall(gnd_pattern, notes_text)
    viaf_match = re.findall(viaf_pattern,notes_text)
    dbr_match = re.findall(dbr_pattern, notes_text)
    wiki_match = re.findall(wiki_pattern, notes_text)
    geos_match = re.findall(geonames_pattern, notes_text)


    notes_text = re.sub(gnd_pattern, '', notes_text)
    notes_text = re.sub(viaf_pattern, '', notes_text)
    notes_text = re.sub(dbr_pattern, '', notes_text)
    notes_text = re.sub(wiki_pattern, '', notes_text)
    notes_text = re.sub(geonames_pattern, '', notes_text)

    gnd_content = [item.strip() for match in gnd_match for item in match if item]


    gnd_content = []
    for match in gnd_match:
        for item in match:
            if item != '':
                gnd_content.append(item.strip())

    viaf_content = []
    for match in viaf_match:
        for item in match:
            if item != '':
                viaf_content.append(item.strip())
    
    dbr_content = []
    for match in dbr_match:
        for item in match:
            if item != '':
                dbr_content.append(item.strip())
    
    wiki_content = []
    for match in wiki_match:
        for item in match:
            if item != '':
                wiki_content.append(item.strip())
    
    geonames_content = []
    for match in geos_match:
        for item in match:
            if item != '':
                geonames_content.append(item.strip())

    #Find index of #checked# and delete it and following characterss
    checked_index = notes_text.find("#checked#")
    notes_text = notes_text[:checked_index]


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
