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
    # Initialize the list to store tokens with tag information
    tokens_list = []

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
        id_counter = count(start=1)

        # Create a single tokenizer for reuse
        tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')

        # Combine the XPath expressions for better readability and potential optimization
        for element in et_div.xpath('.//*[not(ancestor-or-self::tei:note)]'
                                     '| .//*[not(ancestor-or-self::tei:note)]/text()'
                                     '| .//tei:note/preceding-sibling::text()', namespaces=ns):
            if isinstance(element, etree._Element):
                tag_name = etree.QName(element).localname
                if tag_name in {'persName', 'placeName', 'term'}:
                    # If it's a valid tag, tokenize its content
                    tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')
                    text_tokens = tokenizer.tokenize(element.text)
                    valid_tokens = [token for token in text_tokens if valid_token_pattern.match(token)]
                    tokens_list.extend([{
                        'token_id': f"en_{next(id_counter):06}",
                        'text': token,
                        'tag_name': tag_name
                    } for token in valid_tokens])
                elif element.text and element.text.strip():
                    # If it's normal text, tokenize without tag information
                    text_tokens = tokenizer.tokenize(element.text)
                    valid_tokens = [token for token in text_tokens if valid_token_pattern.match(token)]
                    tokens_list.extend([{
                        'token_id': f"en_{next(id_counter):06}",
                        'text': token
                    } for token in valid_tokens])

    return {'words': tokens_list}
