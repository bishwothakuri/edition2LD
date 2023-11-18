import logging
import os
import json

from rdflib import Graph
from metadata.xml_tei_parser import extract_metadata_from_xml
from metadata.xml_word_tokenizer import tokenize_xml_text
from conversion.xml_tei_converter import generate_xml_tei_from_metadata
from conversion.rdf_graph_builder import create_rdf_graph
from conversion.word_rdf_mapper import create_rdf_graph_from_tokenized_word
from conversion.rdfa_creator import generate_rdfa_from_graph
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
        # xml_tei = generate_xml_tei_from_metadata(metadata)
        # output_file_path = os.path.join(
        #     "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".xml"
        # )
        # with open(output_file_path, "wb") as f:
        #     f.write(xml_tei)
        # logging.info("XML-TEI file generated successfully at %s", output_file_path)
        token_dict = tokenize_xml_text(xml_file_path)
        # Store the token_dict in a JSON file
        token_output_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + "_tokens.json"
        )
        with open(token_output_file_path, "w",  encoding="utf-8") as f:
            json.dump(token_dict, f, ensure_ascii=False, indent=4)
        logging.info("Token dictionary generated successfully at %s", token_output_file_path)
            

        # Store metadata in a separate JSON file
        json_output_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".json"
        )
        with open(json_output_file_path, "w",  encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        logging.info("JSON file generated successfully at %s", json_output_file_path)

        # Create RDF graph from metadata
        g_metadata: Graph = create_rdf_graph(metadata)
         # Serialize RDF graph to RDF/XML
        rdf_xml_output_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + "_metadata.rdf"
        )
        g_metadata.serialize(rdf_xml_output_file_path, format="xml")
        logging.info("RDF graph serialized to RDF/XML at %s", rdf_xml_output_file_path)


        # Create RDF graph from tokenized words
        g_tokenized: Graph = create_rdf_graph_from_tokenized_word(metadata, token_dict, g_metadata)
         # Serialize RDF graph to RDF/XML
        rdf_xml_output_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + "_tokenized.rdf"
        )
        g_tokenized.serialize(rdf_xml_output_file_path, format="xml")
        logging.info("RDF graph serialized to RDF/XML for tokenized words at %s", rdf_xml_output_file_path)


        # Generate RDFa from the graph 
        rdfa_html = generate_rdfa_from_graph(g_metadata, os.path.splitext(os.path.basename(xml_file_path))[0])
        
        # Write RDFa XHTML file
        rdfa_html_output_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + ".xhtml"
        )
        with open(rdfa_html_output_file_path, "wb") as f:
            f.write(rdfa_html)
        logging.info("RDFa XHTML file generated successfully at %s", rdfa_html_output_file_path)

        # Save Turtle serialization for the first graph (metadata)
        turtle_metadata_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + "_metadata.ttl"
        )
        save_turtle_serialization(g_metadata, turtle_metadata_file_path)
        logging.info("Turtle serialization file for metadata generated successfully at %s", turtle_metadata_file_path)

        # Save Turtle serialization for the second graph (tokenized words)
        turtle_tokenized_file_path = os.path.join(
            "output", os.path.splitext(os.path.basename(xml_file_path))[0] + "_tokenized.ttl"
        )
        save_turtle_serialization(g_tokenized, turtle_tokenized_file_path)
        logging.info("Turtle serialization file for tokenized words generated successfully at %s", turtle_tokenized_file_path)

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
