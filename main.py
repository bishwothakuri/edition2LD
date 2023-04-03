import logging
import os
from typing import Dict

from src.xml_parser import extract_metadata


def main(xml_file_path: str) -> Dict[str, list]:
    """
    Extracts metadata from an XML file and returns it as a dictionary.

    Args:
        xml_file_path: Path to the XML file to extract metadata from.

    Returns:
        A dictionary containing the extracted metadata, with the keys 'persons',
        'places', and 'terms' and the corresponding values as lists of strings.

    Raises:
        FileNotFoundError: If the specified XML file path does not exist.
        ValueError: If the specified XML file is empty or invalid.
    """
    logging.info("Extracting metadata from XML file at %s", xml_file_path)
    metadata = extract_metadata(xml_file_path)
    logging.info("Metadata extracted successfully from XML file.")
    return metadata


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    xml_file_path = os.path.join("data", "K_0440_0007.xml")
    try:
        metadata = main(xml_file_path)
        # print(metadata)
        # Do something with the extracted metadata
    except FileNotFoundError as e:
        logging.error("The specified XML file path does not exist: %s", e)
    except ValueError as e:
        logging.error("The specified XML file is empty or invalid: %s", e)
