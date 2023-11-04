import os
from lxml import etree
import nltk
import re
from nltk.tokenize import word_tokenize
from itertools import count

# Download NLTK's Punkt tokenizer models (only required once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
# Define a regular expression pattern to match valid tokens (e.g., words with alphabetic characters other than "s")
valid_token_pattern = re.compile(r"^(?!s$)[A-Za-z]+$")

def tokenize_xml_text(xml_file_path):
    # Initialize the dictionary to store token IDs and their corresponding tokens
    tokens_dict = {}

    # Create an XML parser with 'xml' option
    parser = etree.XMLParser(recover=True)

    # Parse the XML content with lxml
    tree = etree.parse(xml_file_path, parser=parser)
    root = tree.getroot()

    # Use xpath to directly select the element with xml:id="et"
    et_div = root.xpath('//tei:div[@xml:id="et"]', namespaces={"tei": "http://www.tei-c.org/ns/1.0"})

    if et_div:
        et_div = et_div[0]  # Select the first element if there are multiple
        text = et_div.xpath('.//text()')
        text = ' '.join(text).strip()

        # Tokenize the text using NLTK, but only keep valid tokens
        tokens = word_tokenize(text)
        valid_tokens = [token for token in tokens if valid_token_pattern.match(token)]

        # Generate unique IDs for valid tokens
        id_counter = count(start=1)
        token_ids = [f"en_{next(id_counter):06}" for _ in valid_tokens]  # Add "en_" before the six-digit token number

        # Populate the tokens_dict with token IDs and their corresponding tokens
        for token, token_id in zip(valid_tokens, token_ids):
            tokens_dict[token_id] = token

    return tokens_dict

