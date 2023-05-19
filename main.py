import logging
import os
from typing import Dict

from src.rdfa_transformer import convert_to_rdf_xml
from src.xml_parser import extract_metadata


def main(xml_file_path: str, output_file_path: str) -> None:
    """
    Extracts metadata from an XML file, converts it to RDF graph and serializes it in RDF/XML format.

    Args:
        xml_file_path: Path to the XML file to extract metadata from.
        output_file_path: Path to the output file where RDF/XML will be saved.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified XML file path does not exist.
        ValueError: If the specified XML file is empty or invalid.
    """
    try:
        metadata = extract_metadata(xml_file_path)
        rdf_xml = convert_to_rdf_xml(metadata)
        with open(output_file_path, "wb") as f:
            f.write(rdf_xml)
        logging.info("RDF/XML file generated successfully at %s", output_file_path)
    except Exception as e:
        logging.error("Error generating RDF/XML file: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    xml_file_path = os.path.join("data", "K_0440_0007.xml")
    output_file_path = os.path.join(
        "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".rdf"
    )
    try:
        main(xml_file_path, output_file_path)
    except FileNotFoundError as e:
        logging.error("The specified XML file path does not exist: %s", e)
    except ValueError as e:
        logging.error("The specified XML file is empty or invalid: %s", e)
