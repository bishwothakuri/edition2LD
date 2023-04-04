from typing import Dict

from rdflib import Graph, Literal, Namespace, URIRef

from serializers.rdfa_serializer import serialize_graph_to_rdf_xml

FOAF_NS = Namespace("http://xmlns.com/foaf/0.1/")
GN_NS = Namespace("http://www.geonames.org/ontology#")
SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC_NS = Namespace("http://purl.org/dc/elements/1.1/")


def create_rdf_graph(metadata: Dict) -> Graph:
    persons = metadata.get("persons", [])
    places = metadata.get("places", [])
    terms = metadata.get("terms", [])

    g = Graph()
    for i, person in enumerate(persons):
        person_uri = URIRef(f"http://example.org/person/{i}")
        g.add((person_uri, FOAF_NS.name, Literal(person)))

    for i, place in enumerate(places):
        place_uri = URIRef(f"http://example.org/place/{i}")
        g.add((place_uri, GN_NS.name, Literal(place)))

    for i, term in enumerate(terms):
        term_uri = URIRef(f"http://example.org/term/{i}")
        g.add((term_uri, SKOS_NS.prefLabel, Literal(term)))

    return g


def convert_to_rdf_xml(metadata: Dict) -> bytes:
    g = create_rdf_graph(metadata)
    rdf_xml = g.serialize(format="application/rdf+xml")
    return rdf_xml.encode("utf-8")
