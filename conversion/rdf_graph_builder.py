import os
import json
from typing import Dict
from rdflib import RDF, Graph, Literal, Namespace, URIRef, BNode
from rdflib.util import guess_format


# Define RDF namespaces for the ontology
FOAF_NS = Namespace("http://xmlns.com/foaf/0.1/")
GN_NS = Namespace("http://www.geonames.org/ontology#")
SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC_NS = Namespace("http://purl.org/dc/elements/1.1/")


# Define custom namespaces specific to the Nepali ontology
nepalica = Namespace("https://nepalica.hadw-bw.de/nepal/editions/show/")
nepalica_doi = Namespace("https://digi.hadw-bw.de/view/")
nepalica_meta = Namespace("https://nepalica.hadw-bw.de/nepal/catitems/viewitem/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
nepalica_reg = Namespace("https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/")
gn = Namespace("https://www.geonames.org/")
gn_id = Namespace("https://www.geonames.org/")
nepalica_gloss = Namespace("https://nepalica.hadw-bw.de/nepal/words/viewitem/")
schema = Namespace("http://schema.org/")
nepalpeople = Namespace("https://example.com/nepalpeople#")


geonames = Namespace("https://sws.geonames.org/")
dbr = Namespace("https://dbpedia.org/resource/")
wiki = Namespace("https://de.wikipedia.org/wiki/")
viaf = Namespace("https://viaf.org/viaf/")
gnd = Namespace("https://d-nb.info/gnd/")
wikidata = Namespace("https://www.wikidata.org/wiki/")
gndo = Namespace("https://d-nb.info/standards/elementset/gnd#")


# Load the ontology file
ontology_file_path = os.path.join("data", "nepalpeople.ttl")
g_ontology = Graph()
g_ontology.parse(ontology_file_path, format="turtle")

def create_rdf_graph(metadata: Dict[str, list]) -> Graph:
    persons = metadata.get("persons", [])
    places = metadata.get("places", [])
    terms = metadata.get("terms", [])
    physDesc_ref_target = metadata.get("physDesc_id")
    
    # Initialize an RDF graph
    g = Graph()

    # Bind RDF namespaces for use in the graph
    g.bind("foaf", FOAF_NS)
    g.bind("gn", GN_NS)
    g.bind("skos", SKOS_NS)
    g.bind("dc", DC_NS)
    g.bind("dbr", dbr)
    g.bind("wiki", wiki)
    g.bind("geonames", geonames)
    g.bind("viaf", viaf)
    g.bind("gnd", gnd)
    g.bind("wikidata", wikidata)
    g.bind("gndo", gndo)
    g.bind("schema", schema)

    # Bind custom namespaces using the NamespaceManager
    g.namespace_manager.bind("nepalica", nepalica, override=False)
    g.namespace_manager.bind("nepalica_reg", nepalica_reg)

    
    # Continue with the rest of your code to add data from the `persons` dictionary
    person_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}person")
    )
    
    for person in persons:
        person_node = URIRef(f"{person_uri}#{person['anglicized_name'].replace(' ', '_')}")
        g.add((person_node, RDF.type, FOAF_NS.Person))
        g.add((person_node, FOAF_NS.name, Literal(person["anglicized_name"], lang='ne')))
        g.add((person_node, rdfs.label, Literal(person["anglicized_name"], lang='ne')))

        # Add devanagari_name as a custom property
        if "devanagari_name" in person:
            g.add((person_node, rdfs.devanagariLabel, Literal(person["devanagari_name"], lang='ne')))

        # Extract alternative names and add them to the RDF graph
        alternative_names = [alt_name for alt_name in person.get("alternative_names", []) if alt_name != person["anglicized_name"]]
        for alt_name in alternative_names:
            g.add((person_node, SKOS_NS.altLabel, Literal(alt_name)))
        
        # Add the value for nepalica-reg:{{ person['n'] }}
        person_ref_value = person.get("n")
        if person_ref_value:
            rdfs_see_also_parent = nepalica_reg[person_ref_value]
            g.add((person_node, rdfs.seeAlso, rdfs_see_also_parent))
        
        # Add the LOD identifiers extracted from the metadata dictionary
        for lod_identifier_key, lod_identifier_values in person.items():
            if lod_identifier_key in ["gnd", "viaf", "wiki", "dbr", "geonames", "wikidata"]:
                for lod_identifier_value in lod_identifier_values:
                    if lod_identifier_value:
                        lod_uri = URIRef(f"{lod_identifier_key}:{lod_identifier_value}")
                        g.add((person_node, rdfs.seeAlso, lod_uri))

        # Add the note_text to the graph 
        note_text = person["note_text"]
        if note_text:
            g.add((person_node, rdfs.comment, Literal(note_text)))
        
    # Add places information to the RDF graph
    for place in places:
        place_node = URIRef(f"{geonames}{place['n']}")
        g.add((place_node, RDF.type, GN_NS.Feature))
        g.add((place_node, DC_NS.title, Literal(place["place_name"], lang='en')))

        # Add alternative names for the place
        alternative_names = [alt_name for alt_name in place.get("alternative_names", []) if alt_name != place["place_name"]]
        for alt_name in alternative_names:
            g.add((place_node, SKOS_NS.altLabel, Literal(alt_name)))

        # Add note_text to the graph for the place
        note_text = place["note_text"]
        if note_text:
            g.add((place_node, rdfs.comment, Literal(note_text)))

    # Add terms information to the RDF graph
    for term in terms:
        term_node = URIRef(f"{nepalica_gloss}{term['term_ref']}")
        g.add((term_node, RDF.type, SKOS_NS.Concept))
        g.add((term_node, SKOS_NS.prefLabel, Literal(term["prefLabel"], lang='en')))
        g.add((term_node, SKOS_NS.definition, Literal(term["meaning"], lang='en')))

        # Enrich the RDF graph with data from the sample ontology
        g += g_ontology

    return g
