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

def extract_regular_expression(notes_text):
    '''
    Use regular expressions to extract content of specific identifier
    Input: notes_text
    Output: dictionary includes indentifier name and correspoinding content

    Reference example: https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/178
    '''
    gnd_pattern = r'gnd:(\d+)'
    viaf_pattern = r'viaf:(\d+)'
    wiki_pattern = r'wiki:(\S+)'

    gnd_match = re.search(gnd_pattern, notes_text)
    viaf_match = re.search(viaf_pattern,notes_text)
    wiki_match = re.search(wiki_pattern, notes_text)

    gnd_content = gnd_match.group(1) if gnd_match else None
    viaf_content = viaf_match.group(1) if viaf_match else None
    wiki_content = wiki_match.group(1) if wiki_match else None

    #print("gnd:", gnd_content)
    #print("viaf:", viaf_content)
    #print("wiki:", wiki_content)

    content_dict = {"gnd": gnd_content, "viaf": viaf_content, "wiki": wiki_content}
    # print(content_dict)

    keys = content_dict.keys()
    elements = [content_dict[key] for key in keys]

    return keys, elements
#notes = "born: 1720 at Gorkha; died: 11 January 1775 at Devighat; gender: male; father: Narabhūpāla Śāha, king of Gorkha; spouse: Indra Kumārī Devī, Narendra Rājyalakṣmī Devī; children: Pratāpa Siṃha Śāha, Bahādura Śāha, Vilāsa Kumārī Śāha; details: king of Gorkha (r. 3 April 1743–1768); king of Nepal (r. 1768-1775); normdata: gnd:119173816, viaf:5735314,  #checked#MG:add cross-links#"
#extract_regular_expression(notes)

