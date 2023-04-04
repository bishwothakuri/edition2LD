from typing import Dict

from rdflib import RDF, Graph, Literal, Namespace, URIRef

FOAF_NS = Namespace("http://xmlns.com/foaf/0.1/")
GN_NS = Namespace("http://www.geonames.org/ontology#")
SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC_NS = Namespace("http://purl.org/dc/elements/1.1/")


def create_rdf_graph(metadata: Dict[str, list]) -> Graph:
    persons = metadata.get("persons", [])
    places = metadata.get("places", [])
    terms = metadata.get("terms", [])

    g = Graph()
    g.bind("foaf", FOAF_NS)
    g.bind("gn", GN_NS)
    g.bind("skos", SKOS_NS)
    g.bind("dc", DC_NS)

    for i, person in enumerate(persons):
        person_uri = URIRef(f"http://example.org/person/{i}")
        g.add((person_uri, RDF.type, FOAF_NS.Person))
        g.add((person_uri, FOAF_NS.name, Literal(person)))

    for i, place in enumerate(places):
        place_uri = URIRef(f"http://example.org/place/{i}")
        g.add((place_uri, RDF.type, GN_NS.Feature))
        g.add((place_uri, GN_NS.name, Literal(place)))

    for i, term in enumerate(terms):
        term_uri = URIRef(f"http://example.org/term/{i}")
        g.add((term_uri, RDF.type, SKOS_NS.Concept))
        g.add((term_uri, SKOS_NS.prefLabel, Literal(term["term"])))
        g.add((term_uri, SKOS_NS.definition, Literal(term["meaning"])))

    return g


def convert_to_rdf_xml(metadata: Dict[str, list]) -> bytes:
    g = create_rdf_graph(metadata)
    rdf_xml = g.serialize(format="application/rdf+xml")
    return rdf_xml.encode("utf-8")
