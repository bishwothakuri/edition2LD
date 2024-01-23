import logging
import requests
from bs4 import BeautifulSoup, NavigableString
import re
import shelve
from datetime import datetime

logging.basicConfig(level=logging.INFO)


def fetch_ontology_page(ontology_url, ont_item_id):
    cache_filename = "ontology_cache.db"

    try:
        with shelve.open(cache_filename, writeback=True) as cache:
            # Check if the page is already in the cache and get the cached timestamp
            if ont_item_id in cache:
                cached_data = cache[ont_item_id]
                cached_time = cached_data.get("timestamp")

                if cached_time and is_cache_old(cached_time):
                    try:
                        # Fetch the page because the cached data is older than 7 days
                        response = requests.get(ontology_url + ont_item_id)
                        response.raise_for_status()  # Raise an HTTPError for bad responses

                        content = response.content

                        # Save the fetched page to the cache with the current timestamp
                        cache[ont_item_id] = {
                            "content": content,
                            "timestamp": datetime.now(),  # Timestamp when the data was cached
                        }
                        return BeautifulSoup(content, "html.parser")
                    except requests.RequestException as e:
                        print("Error fetching page:", e)
                else:
                    # Use the cached data directly
                    return BeautifulSoup(cached_data["content"], "html.parser")

            else:
                # If the page is not in the cache, fetch the page and store it in the cache
                response = requests.get(ontology_url + ont_item_id)
                content = response.content

                cache[ont_item_id] = {
                    "content": content,
                    "timestamp": datetime.now(),  # Timestamp when the data was cached
                }
                return BeautifulSoup(content, "html.parser")

    except Exception as e:
        print("Error in fetch_ontology_page:", e)
        return None


def is_cache_old(cached_time):
    # Check if the cache timestamp is older than 7 days
    time_difference = datetime.now() - cached_time
    return time_difference.days > 7


def extract_item_note_and_surname(ontology_url, ont_item_id):
    # Fetch the ontology page content
    soup = fetch_ontology_page(ontology_url, ont_item_id)

    # Check if the page content is not None
    if soup is not None:
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
    else:
        # Handle the case where the page content is None
        print("Error: Page content is None.")
        return None



def extract_additional_info_from_note(note_text):
    '''
    Use regular expressions to extract content of specific identifier
    Input: note_text
    Output: dictionary includes indentifier name and correspoinding content

    Reference example: https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/178
    https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/304
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

    # Define a regular expression pattern to match the first underscore at the start of a word
    underscore_pattern = r'\b_(\w)'

    # Initialize cleaned content lists
    wiki_content_cleaned = []
    dbr_content_cleaned = []

    # Loop through the lists and clean each string
    # for content in wiki_content:
        # cleaned_content = re.sub(underscore_pattern, r'\1', content)
        # wiki_content_cleaned.append(cleaned_content)

    # for content in dbr_content:
    #     cleaned_content = re.sub(underscore_pattern, r'\1', content)
    #     dbr_content_cleaned.append(cleaned_content)

    #Delete #... until end of entry-no matter what comes after it
    checked_index = note_text.find("#")
    note_text = note_text[:checked_index]

    # Remove leading and trailing spaces
    note_text = note_text.strip()

    content_dict = {"gnd": gnd_content, "viaf": viaf_content, "wiki": wiki_content_cleaned, "wikidata": wikidata_content, "dbr": dbr_content_cleaned, "geonames": geonames_content, "gender": gender_content}
    keys = content_dict.keys()
    elements = [content_dict[key] for key in keys]

    return keys, elements, note_text



def fetch_with_caching(url, cache_key):
    cache_filename = "metadata_cache.db"

    try:
        with shelve.open(cache_filename, writeback=True) as cache:
            # Check if the URL is already in the cache and get the cached timestamp
            if cache_key in cache:
                cached_data = cache[cache_key]
                cached_time = cached_data.get("timestamp")

                # Check if the cache is older than 7 days
                if cached_time and is_cache_old(cached_time):
                    try:
                        # Fetch the page because the cached data is older than 7 days
                        response = requests.get(url)
                        response.raise_for_status()  # Raise an HTTPError for bad responses

                        content = response.content

                        # Save the fetched page to the cache with the current timestamp
                        cache[cache_key] = {
                            "content": content,
                            "timestamp": datetime.now(),  # Timestamp when the data was cached
                        }
                        return BeautifulSoup(content, "html.parser")
                    except requests.RequestException as e:
                        print(f"Error fetching {url}:", e)
                        # Handle the error (e.g., return None, log the error, etc.)
                else:
                    # Use the cached data directly
                    return BeautifulSoup(cached_data["content"], "html.parser")

        # If the URL is not in the cache or the cache is older than 7 days, fetch the page
        response = requests.get(url)
        content = response.content

        # Save the fetched page to the cache with the current timestamp
        with shelve.open(cache_filename, writeback=True) as cache:
            cache[cache_key] = {
                "content": content,
                "timestamp": datetime.now(),  # Timestamp when the data was cached
            }

        print(f"Fetched new data for {url}")
        return BeautifulSoup(content, "html.parser")

    except Exception as e:
        print(f"Error fetching {url}:", e)
        return None


def extract_metadata_of_the_document(physDesc_id):
    try:
        # URL of the webpage to scrape
        url = f"https://nepalica.hadw-bw.de/nepal/catitems/viewitem/{physDesc_id}"

        # Fetch the webpage content with caching
        soup = fetch_with_caching(url, f"metadata_{physDesc_id}")

        # Check if the page content is not None
        if soup is not None:
            # Find the table element containing the data
            data_table = soup.find("table")

            # Initialize a dictionary to store the scraped data
            scraped_data = {}

            # Check if the table was found
            if data_table and not isinstance(data_table, NavigableString):
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
            # Handle the case where the page content is None
            print(f"Error: Page content is None for {url}")
            return None

    except Exception as e:
        print(f"Error extracting metadata from the document:", e)
