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
        'nepalica': Namespace("https://nepalica.hadw-bw.de/nepal/editions/show/")
    }

    # Serialize the graph in Turtle format
    turtle_data = graph.serialize(format='turtle')

    # Replace the full URIs with namespace prefixes
    for prefix, namespace in namespaces.items():
        turtle_data = turtle_data.replace(str(namespace), f"{prefix}:")


    # Remove the angle brackets around subject, object, and predicate
    turtle_data = turtle_data.replace("<", "").replace(">", "")

    # Save the modified Turtle serialization to the file
    with open(file_path, 'w') as f:
        # Write the namespaces in the heading
        for prefix, namespace in namespaces.items():
            f.write(f"@prefix {prefix}: <{namespace}> .\n")
        f.write('\n')
        f.write(turtle_data)
