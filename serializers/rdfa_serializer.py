from rdflib.plugins.serializers.rdfxml import XMLSerializer


def serialize_graph_to_rdf_xml(graph):
    serializer = XMLSerializer()
    rdf_xml = graph.serialize(
        format="application/rdf+xml", destination=None, serializer=serializer
    )
    return rdf_xml
