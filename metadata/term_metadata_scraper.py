import requests
from bs4 import BeautifulSoup
import os

def extract_term_meaning(base_url, term_ref):
    try:
        # Concatenate the base URL and the 'ref' attribute to form the URL for the term
        term_url = base_url + term_ref

        # Get the HTML content of the URL using requests
        response = requests.get(term_url, timeout=20)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find_all("table")[0]

        # Extract the meaning from the table
        meaning = None
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2 and cells[0].text.strip() == "Notes":
                meaning = cells[1].text.strip()
            elif (
                meaning is not None and len(cells) == 2 and cells[0].text.strip() == "Type"
            ):
                meaning += " " + cells[1].text.strip()

        # Return the meaning
        return meaning

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Handle 404 error (Not Found)
            print(f"Term {term_ref} not found. Skipping.")
            return None
        else:
            # Re-raise the HTTPError for other status codes
            raise e

    except requests.RequestException as e:
        # Log the error or handle it appropriately
        print(f"Error in extract_term_meaning: {e}")
        return None

    except Exception as e:
        # Handle other exceptions if needed
        print(f"Unexpected error in extract_term_meaning: {e}")
        return None
