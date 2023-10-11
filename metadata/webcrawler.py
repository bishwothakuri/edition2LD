import requests
from bs4 import BeautifulSoup
import re

def fetch_ontology_page(ontology_url, ont_item_id):
    response = requests.get(ontology_url + ont_item_id)
    return BeautifulSoup(response.content, "html.parser")

def extract_item_note_and_surname(ontology_url, ont_item_id):
    soup = fetch_ontology_page(ontology_url, ont_item_id)
    
    notes_row = None
    surname_row = None
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    for row in rows:
        data = [x.text.strip() for x in row.find_all('td')]
        if 'Notes' in data:
            notes_row = row
        elif 'Surname' in data:
            surname_row = row
            
    note_text = notes_row.find_all('td')[1].text.strip() if notes_row else ''
    surname_text = surname_row.find_all('td')[1].text.strip() if surname_row else ''
    
    return {"note_text": note_text, "surname": surname_text}


def extract_additional_info_from_note(note_text):
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
    gender_pattern = r'gender:\s*(\w+);'


    # Replace multiple spaces with a single space
    note_text = re.sub(r'\s+', ' ', note_text)

    gnd_match = re.findall(gnd_pattern, note_text)
    viaf_match = re.findall(viaf_pattern, note_text)
    dbr_match = re.findall(dbr_pattern, note_text)
    wiki_match = re.findall(wiki_pattern, note_text)
    wikidata_match = re.findall(wikidata_pattern, note_text)
    geos_match = re.findall(geonames_pattern, note_text)
    gender_match = re.search(gender_pattern, note_text)

    note_text = re.sub(gnd_pattern, '', note_text)
    note_text = re.sub(viaf_pattern, '', note_text)
    note_text = re.sub(dbr_pattern, '', note_text)
    note_text = re.sub(wiki_pattern, '', note_text)
    note_text = re.sub(geonames_pattern, '', note_text)
    note_text = re.sub(gender_pattern, '', note_text)

    gnd_content = [item.strip('.').strip() for match in gnd_match for item in match if item]
    viaf_content = [item.strip('.').strip() for match in viaf_match for item in match if item]
    dbr_content = [item.strip('.').strip() for match in dbr_match for item in match if item]
    wiki_content = [item.strip('.').strip() for match in wiki_match for item in match if item]
    wikidata_content = [item.strip('.').strip() for match in wikidata_match for item in match if item]
    geonames_content = [item.strip('.').strip() for match in geos_match for item in match if item]
    gender_content = gender_match.group(1).strip() if gender_match else None

    #Delete #... until end of entry-no matter what comes after it
    checked_index = note_text.find("#")
    note_text = note_text[:checked_index]

    # Remove leading and trailing spaces
    note_text = note_text.strip()

    content_dict = {"gnd": gnd_content, "viaf": viaf_content, "wiki": wiki_content, "wikidata": wikidata_content, "dbr": dbr_content, "geonames": geonames_content, "gender": gender_content}
    keys = content_dict.keys()
    elements = [content_dict[key] for key in keys]

    return keys, elements, note_text



def extract_metadata_of_the_document(physDesc_id):
    try:
        # URL of the webpage to scrape
        url = f"https://nepalica.hadw-bw.de/nepal/catitems/viewitem/{physDesc_id}"

        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the webpage using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the table element containing the data
            data_table = soup.find("table")

            # Initialize a dictionary to store the scraped data
            scraped_data = {}

            # Check if the table was found
            if data_table:
                # Loop through the table rows
                for row in data_table.find_all("tr"):
                    # Extract the table cells (td) in each row
                    cells = row.find_all("td")
                    if len(cells) == 2:
                        # Get the text content of the first cell as the key and the second cell as the value
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()

                        # Store the key-value pair in the dictionary
                        scraped_data[key] = value

            return scraped_data  # Return the scraped data as a dictionary
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    except Exception as e:
        print("Error extracting metadata from the document:", e)
