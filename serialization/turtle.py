import re
from rdflib import Graph, Namespace

# Define the custom namespaces
custom_namespaces = {
    'geonames': Namespace("https://sws.geonames.org/"),
    'dbr': Namespace("https://dbpedia.org/resource/"),
    'wiki':  Namespace("https://de.wikipedia.org/wiki/"),
    'viaf': Namespace("https://viaf.org/viaf/"),
    'gnd': Namespace("https://d-nb.info/gnd/"),
    'wikidata': Namespace("https://www.wikidata.org/wiki/"),
    'nepalica_gloss' : Namespace("https://nepalica.hadw-bw.de/nepal/words/viewitem/"),
    'ontolex' : Namespace("http://www.w3.org/ns/lemon/ontolex#") ,
    'lime' : Namespace("http://www.w3.org/ns/lemon/lime#")
}

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
        'nepalica_gloss': Namespace("https://nepalica.hadw-bw.de/nepal/words/viewitem/"),
        'lexvo' : Namespace("http://lexvo.org/id/iso639-3/")

    }

    # Serialize the graph in Turtle format
    turtle_data = graph.serialize(format='turtle')

    # Split the Turtle data into header and data parts
    header_part, data_part = turtle_data.split('\n\n', 1)

    # Create a custom namespace declaration string
    custom_namespace_declarations = ""
    for prefix, namespace in custom_namespaces.items():
        custom_namespace_declarations += f'@prefix {prefix}: <{namespace}> .\n'


    # Replace the full URIs with namespace prefixes in the data part
    for prefix, namespace in namespaces.items():
        # Use regular expressions to replace full URIs with namespace prefixes
        data_part = re.sub(r'<{}(.*?)>'.format(namespace), '{}:\\1'.format(prefix), data_part)

    # Remove the angle brackets around subject, object, and predicate in the data part
    data_part = data_part.replace("<", "").replace(">", "")

    data_part = re.sub(r',\n', ' ,\n', data_part)

    #replace # into _ to form link
    # data_part = re.sub(r'(nepalica:\d+)#(\w)', r'\1#\2', data_part) 
    
    # Use regular expressions to add spaces before commas (,) within Turtle objects in the data part
    # data_part = re.sub(r'([^,])\s*,', r'\1 ,', data_part)

    # Combine the header and modified data parts
    modified_turtle_data = header_part + '\n' + custom_namespace_declarations + '\n\n' + data_part

    # Save the modified Turtle serialization to the file
    with open(file_path, 'w') as f:
        f.write(modified_turtle_data)
