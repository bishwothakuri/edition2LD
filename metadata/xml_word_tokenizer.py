import re
from lxml import etree
import nltk
from nltk.tokenize import RegexpTokenizer
from itertools import count

# Download NLTK's Punkt tokenizer models (only required once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Define a regular expression pattern to match valid tokens (e.g., words with alphabetic characters including diacritics)
valid_token_pattern = re.compile(r"^(?!s$)\w+$", flags=re.UNICODE)

def tokenize_xml_text(xml_file_path):
    # Initialize the dictionary to store token IDs and their corresponding tokens
    tokens_dict = {}

    # Create an XML parser with 'xml' option
    parser = etree.XMLParser(recover=True)

    # Parse the XML content with lxml
    tree = etree.parse(xml_file_path, parser=parser)
    root = tree.getroot()

    # Define the namespace
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Use xpath to directly select the element with xml:id="et"
    et_div = root.xpath('//tei:div[@xml:id="et"]', namespaces=ns)

    if et_div:
        et_div = et_div[0]  # Select the first element if there are multiple

        # Extract and tokenize text from text() and foreign elements sequentially
        tokens = []
        id_counter = count(start=1)

        for element in et_div.xpath('.//text() | .//foreign', namespaces=ns):
            if isinstance(element, str):
                # If it's a string, tokenize its content
                tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')
                text_tokens = tokenizer.tokenize(element)
                valid_tokens = [token for token in text_tokens if valid_token_pattern.match(token)]
                tokens.extend([(f"en_{next(id_counter):06}", token) for token in valid_tokens])
            elif element.tag == '{http://www.tei-c.org/ns/1.0}foreign':
                # If it's a foreign tag, extract and tokenize its text content
                foreign_text = ' '.join([t.strip() for t in element.xpath('.//text()', namespaces=ns)])
                tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')
                foreign_tokens = tokenizer.tokenize(foreign_text)
                tokens.extend([(f"en_{next(id_counter):06}", token) for token in foreign_tokens])

        # Populate the tokens_dict with token IDs and their corresponding tokens
        for token_id, token in tokens:
            tokens_dict[token_id] = token

    return tokens_dict

