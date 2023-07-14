import logging
import os

from rdflib import Graph
from metadata.xml_tei_parser import extract_metadata_from_xml
from conversion.xml_tei_converter import generate_xml_tei_from_metadata
from conversion.rdf_graph_builder import create_rdf_graph
from conversion.rdfa_creater import generate_rdfa_from_graph
from serialization.turtle import save_turtle_serialization


def main(xml_file_path: str, json_file_path: str) -> None:
    """
    Extracts metadata from an XML file, converts it to RDF graph and serializes it in RDF/XML format.

    Args:
        xml_file_path: Path to the XML file to extract metadata from.
        json_file_path: Path to the JSON file containing metadata mappings.
        
    Returns:
        None

    Raises:
        FileNotFoundError: If the specified XML file path does not exist.
        ValueError: If the specified XML file is empty or invalid.
    """
    try:
        metadata = extract_metadata_from_xml(xml_file_path, json_file_path)
        xml_tei = generate_xml_tei_from_metadata(metadata)
        output_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".xml"
        )
        with open(output_file_path, "wb") as f:
            f.write(xml_tei)
        logging.info("XML-TEI file generated successfully at %s", output_file_path)
        # Create RDF graph from metadata
        g: Graph = create_rdf_graph(metadata)
        # Generate RDFa from the graph 
        rdfa_html = generate_rdfa_from_graph(g, os.path.splitext(os.path.basename(xml_file_path))[0])
        # Save RDF/XML serialization in the output folder
        rdf_xml_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".rdf"
        )
        g.serialize(rdf_xml_file_path, format="xml")
        logging.info("RDF/XML file generated successfully at %s", rdf_xml_file_path)
        # Save Turtle serialization in the output folder
        turtle_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".ttl"
        )
        try:
            save_turtle_serialization(g, turtle_file_path)
            logging.info("Turtle serialization file generated successfully at %s", turtle_file_path)
        except Exception as e:
            logging.error("An error occurred while saving Turtle serialization: %s", e)
        # with open(output_file_path, "w") as f:
            # f.write(rdfa_html.decode("utf-8"))
        # logging.info("RDFa HTML file generated successfully at %s", output_file_path)
    except FileNotFoundError as e:
        logging.error("The specified XML file path does not exist: %s", e)
    except ValueError as e:
        logging.error("The specified XML file is empty or invalid: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    xml_file_path = os.path.join("data", "K_0440_0007.xml")
    json_file_path = os.path.join("data", "ont_item_occurrences.json")
    try:
        main(xml_file_path, json_file_path)
    except FileNotFoundError as e:
        logging.error("The specified XML file path does not exist: %s", e)
    except ValueError as e:
        logging.error("The specified XML file is empty or invalid: %s", e)
