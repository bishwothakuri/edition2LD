import re
from rdflib import Graph, Namespace

def save_turtle_serialization(graph: Graph, file_path: str) -> None:
    """
    Serializes the RDF graph in Turtle format and saves it to the specified file path.

    Args:
        graph: The RDF graph to be serialized.
        file_path: The file path where the Turtle serialization will be saved.

    Returns:
        None
    """
    # Define the namespaces
    namespaces = {
        'nepalica': Namespace("https://nepalica.hadw-bw.de/nepal/editions/show/"),
        'nepalica_reg': Namespace("https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/"),
        'nepalica_gloss': Namespace("https://nepalica.hadw-bw.de/nepal/words/viewitem/")
    }

    # Serialize the graph in Turtle format
    turtle_data = graph.serialize(format='turtle')

    # Split the Turtle data into header and data parts
    header_part, data_part = turtle_data.split('\n\n', 1)

    # Replace the full URIs with namespace prefixes in the data part
    for prefix, namespace in namespaces.items():
        # Use regular expressions to replace full URIs with namespace prefixes
        data_part = re.sub(r'<{}(.*?)>'.format(namespace), '{}:\\1'.format(prefix), data_part)

    # Remove the angle brackets around subject, object, and predicate in the data part
    data_part = data_part.replace("<", "").replace(">", "")

    # Use regular expressions to add spaces before commas (,) within Turtle objects in the data part
    data_part = re.sub(r'([^,])\s*,', r'\1 ,', data_part)

    # Combine the header and modified data parts
    modified_turtle_data = header_part + '\n\n' + data_part

    # Save the modified Turtle serialization to the file
    with open(file_path, 'w') as f:
        f.write(modified_turtle_data)
