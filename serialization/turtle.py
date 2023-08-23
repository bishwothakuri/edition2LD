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

    # Remove the angle brackets around subject, object, and predicate
    turtle_data = turtle_data.replace("<", "").replace(">", "")

    # Replace full URIs with namespace prefixes
    for prefix, namespace in namespaces.items():
        if prefix != 'nepalica_reg':  # Exclude nepalica_reg namespace from this part
            turtle_data = turtle_data.replace(str(namespace), f"{prefix}:")

    # lod_identifier_prefixes = ["gnd:", "viaf:", "wiki:", "dbr:", "geonames:", "wikidata:"]
    # for prefix in lod_identifier_prefixes:
    #     replacement = f',\n        {prefix}'  # Add a space after the comma
    #     turtle_data = turtle_data.replace(f',{prefix}', replacement)


    # Save the modified Turtle serialization to the file
    with open(file_path, 'w') as f:
        # Write the namespaces in the heading
        for prefix, namespace in namespaces.items():
            f.write(f"@prefix {prefix}: <{namespace}> .\n")
        f.write('\n')

        # Write the modified Turtle data
        f.write(turtle_data)
