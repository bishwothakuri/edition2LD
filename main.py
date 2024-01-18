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
from conversion.nepal_tokenize import create_rdf_from_nepaltokens
from serialization.turtle import save_turtle_serialization
from pathlib import Path


def process_single_file(xml_file_path: str, json_file_path: str) -> None:
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
        # Extract file name without extension
        file_name = os.path.splitext(os.path.basename(xml_file_path))[0]

        # Create a directory with the file name in the output directory
        output_dir = os.path.join("output", file_name)
        os.makedirs(output_dir, exist_ok=True)

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
        token_output_file_path = os.path.join(output_dir, f"{file_name}_tokens.json")
        with open(token_output_file_path, "w",  encoding="utf-8") as f:
            json.dump(token_dict, f, ensure_ascii=False, indent=4)
        logging.info("Token dictionary generated successfully at %s", token_output_file_path)
            

        # Store metadata in a separate JSON file
        json_output_file_path = os.path.join(output_dir, f"{file_name}.json")
        with open(json_output_file_path, "w",  encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        logging.info("JSON file generated successfully at %s", json_output_file_path)

        # Create RDF graph from metadata
        g_metadata: Graph = create_rdf_graph(metadata)
        # Serialize RDF graph to RDF/XML
        rdf_xml_output_file_path = os.path.join(output_dir, f"{file_name}_named_entities.rdf")
        g_metadata.serialize(rdf_xml_output_file_path, format="xml")
        logging.info("RDF graph serialized to RDF/XML at %s", rdf_xml_output_file_path)


        # Create RDF graph from tokenized words
        g_tokenized: Graph = create_rdf_graph_from_tokenized_word(metadata, token_dict, g_metadata)
        # Serialize RDF graph to RDF/XML
        rdf_xml_output_file_path = os.path.join(output_dir, f"{file_name}_named_entities.rdf")
        g_tokenized.serialize(rdf_xml_output_file_path, format="xml")
        logging.info("RDF graph serialized to RDF/XML for tokenized words at %s", rdf_xml_output_file_path)


        # Generate RDFa from the graph 
        rdfa_html = generate_rdfa_from_graph(g_metadata, os.path.splitext(os.path.basename(xml_file_path))[0])
        
        # Write RDFa XHTML file
        rdfa_html_output_file_path = os.path.join(output_dir, f"{file_name}.xhtml")
        with open(rdfa_html_output_file_path, "wb") as f:
            f.write(rdfa_html)
        logging.info("RDFa XHTML file generated successfully at %s", rdfa_html_output_file_path)

        # Save Turtle serialization for the first graph (metadata)
        turtle_metadata_file_path = os.path.join(output_dir, f"{file_name}_metadata.ttl")
        save_turtle_serialization(g_metadata, turtle_metadata_file_path)
        logging.info("Turtle serialization file for metadata generated successfully at %s", turtle_metadata_file_path)

        # Save Turtle serialization for the second graph (tokenized words)
        turtle_tokenized_file_path = os.path.join(output_dir, f"{file_name}_tokenized.ttl")
        save_turtle_serialization(g_tokenized, turtle_tokenized_file_path)
        logging.info("Turtle serialization file for tokenized words generated successfully at %s", turtle_tokenized_file_path)

        # Create RDF graph from nepal tokens -> inserted part 
        g_nepaltokenized = create_rdf_from_nepaltokens(xml_file_path, json_file_path, metadata)
        rdf_xml_output_file_path = os.path.join(output_dir, f"{file_name}_nepaltokens_named_entities.rdf")
        g_nepaltokenized.serialize(rdf_xml_output_file_path, format="xml")
        logging.info("RDF graph serialized to RDF/XML for nepal tokenized words at %s", rdf_xml_output_file_path)
    
        # Save Turtle serialization for the second graph (tokenized words)  -> inserted part
        turtle_tokenized_file_path = os.path.join(output_dir, f"{file_name}_nepaltokenized.ttl")
        save_turtle_serialization(g_nepaltokenized, turtle_tokenized_file_path)
        logging.info("Turtle serialization file for nepal tokenized words generated successfully at %s", turtle_tokenized_file_path)

    except FileNotFoundError as e:
        logging.error("The specified XML file path does not exist: %s", e)
    except ValueError as e:
        logging.error("The specified XML file is empty or invalid: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)



def process_batch(directory, json_file_path):
    for path in Path(directory).rglob("*.xml"):
        process_single_file(str(path), json_file_path)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    xml_dir_path = "data/xml_input"
    json_file_path = os.path.join("data", "ont_item_occurrences.json")
    try:
        process_batch(xml_dir_path, json_file_path)
    except FileNotFoundError as e:
        logging.error("The specified XML file path does not exist: %s", e)
    except ValueError as e:
        logging.error("The specified XML file is empty or invalid: %s", e)
