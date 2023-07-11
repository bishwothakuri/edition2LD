from typing import Dict
from rdflib import RDF, Graph, Literal, Namespace, URIRef

FOAF_NS = Namespace("http://xmlns.com/foaf/0.1/")
GN_NS = Namespace("http://www.geonames.org/ontology#")
SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC_NS = Namespace("http://purl.org/dc/elements/1.1/")

nepalica = Namespace("https://nepalica.hadw-bw.de/nepal/editions/show/")
nepalica_doi = Namespace("https://digi.hadw-bw.de/view/")
nepalica_meta = Namespace("https://nepalica.hadw-bw.de/nepal/catitems/viewitem/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
nepalica_reg = Namespace("https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/")
gn = Namespace("https://www.geonames.org/")
gn_id = Namespace("https://www.geonames.org/")
dbr = Namespace("http://dbpedia.org/resource/")
wiki = Namespace("https://www.wikipedia.org/")
nepalica_gloss = Namespace("https://nepalica.hadw-bw.de/nepal/words/viewitem/")


def create_rdf_graph(metadata: Dict[str, list]) -> Graph:
    persons = metadata.get("persons", [])
    places = metadata.get("places", [])
    terms = metadata.get("terms", [])
    physDescs = metadata.get("physDescs", [])

    g = Graph()
    g.bind("foaf", FOAF_NS)
    g.bind("gn", GN_NS)
    g.bind("skos", SKOS_NS)
    g.bind("dc", DC_NS)
    g.namespace_manager.bind("nepalica", nepalica, override=False)  # Use NamespaceManager to bind the prefix

    uri_ref = URIRef(nepalica + physDescs[0]) if physDescs else URIRef(f"{nepalica}person")
    for person in persons:
        person_node = URIRef(f"{uri_ref}#{person.replace(' ', '_')}")
        g.add((person_node, RDF.type, FOAF_NS.Person))
        g.add((person_node, FOAF_NS.name, Literal(person)))

    place_uri = URIRef(nepalica + physDescs[0]) if physDescs else URIRef(f"{nepalica}place")
    for place in places:
        place_node = URIRef(f"{place_uri}#{place.replace(' ', '_')}")
        g.add((place_node, RDF.type, GN_NS.Feature))
        g.add((place_node, GN_NS.name, Literal(place)))
        # Add alternative names as skos:altLabel
        alternative_names = place.get("alternative_names", [])
        for alt_name in alternative_names:
            g.add((place_node, SKOS_NS.altLabel, Literal(alt_name)))


    term_uri = URIRef(nepalica + physDescs[0]) if physDescs else URIRef(f"{nepalica}term")
    for term in terms:
        term_node = URIRef(f"{term_uri}#{term['term'].replace(' ', '_')}")
        ref_num = term.get("ref_num")  # Extract the reference number from the term metadata
        g.add((term_node, RDF.type, SKOS_NS.Concept))
        g.add((term_node, SKOS_NS.prefLabel, Literal(term["term"])))
        g.add((term_node, SKOS_NS.comment, Literal(term["meaning"])))
        if ref_num:
            ref_num = ref_num.split("/")[-1]  # Extract the number value from the full URI
            g.add((term_node, SKOS_NS.related, URIRef(ref_num)))  # Use prefix in the related gloss term

    return g
