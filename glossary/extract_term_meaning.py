import defusedxml.ElementTree as ET
import requests
from bs4 import BeautifulSoup


def extract_term_meaning(xml_file_path, base_url):
    # Parse the XML-TEI file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Extract the 'ref' attribute of the 'term' element using XPath
    term_ref = root.findall(".//term")[0].get("ref")

    # Concatenate the base URL and the 'ref' attribute to form the URL for the term
    term_url = base_url + term_ref

    # Get the HTML content of the URL using requests
    response = requests.get(term_url, timeout=20)

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


if __name__ == "__main__":
    xml_file_path = "../data/test.xml"
    base_url = "https://nepalica.hadw-bw.de/nepal/words/viewitem/"
    meaning = extract_term_meaning(xml_file_path, base_url)
    print(meaning)
