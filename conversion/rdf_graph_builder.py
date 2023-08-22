from typing import Dict
from rdflib import RDF, Graph, Literal, Namespace, URIRef, BNode

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

geonames = Namespace("https://sws.geonames.org/")
dbr = Namespace("https://dbpedia.org/resource/")
wiki = Namespace("https://de.wikipedia.org/wiki/")
viaf = Namespace("https://viaf.org/viaf/")
gnd = Namespace("https://d-nb.info/gnd/")
wikidata = Namespace("https://www.wikidata.org/wiki/")


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


    # Bind custom namespaces using the NamespaceManager
    g.namespace_manager.bind("nepalica", nepalica, override=False)
    g.bind("nepalica-reg", nepalica_reg)

    person_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}person")
    )
    for person in persons:
        person_node = URIRef(f"{person_uri}#{person['person_name'].replace(' ', '_')}")
        g.add((person_node, RDF.type, FOAF_NS.Person))
        g.add((person_node, FOAF_NS.name, Literal(person["person_name"])))
        
        # Extract alternative names and add them to the RDF graph
        alternative_names = [alt_name for alt_name in person.get("alternative_names", []) if alt_name != person["person_name"]]
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

    # Loop through place entries and add them to the RDF graph
    place_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}place")
    )
    for place in places:
        # Create a URI reference for the place node
        place_node = URIRef(f"{place_uri}#{place['place_name'].replace(' ', '_')}")
        g.add((place_node, RDF.type, GN_NS.Feature))
        g.add((place_node, GN_NS.name, Literal(place["place_name"])))
       # Extract alternative names and exclude the main place name from the list
        alternative_names = [alt_name for alt_name in place.get("alternative_names", []) if alt_name != place["place_name"]]
        for alt_name in alternative_names:
            g.add((place_node, SKOS_NS.altLabel, Literal(alt_name)))
        # Add the value for nepalica-reg:{{ place['n'] }}
        place_ref_value = place.get("n")
        if place_ref_value:
            rdfs_see_also_parent = nepalica_reg[place_ref_value]
            g.add((place_node, rdfs.seeAlso, rdfs_see_also_parent))

            # Add the LOD identifiers extracted from the metadata dictionary
            for lod_identifier_key, lod_identifier_values in place.items():
                if lod_identifier_key in ["gnd", "viaf", "wiki", "dbr", "geonames", "wikidata"]:
                    for lod_identifier_value in lod_identifier_values:
                        if lod_identifier_value:
                            lod_uri = URIRef(f"{lod_identifier_key}:{lod_identifier_value}")
                            g.add((place_node, rdfs.seeAlso, lod_uri))
            
            # # Sort the LOD identifiers to ensure nepalica-reg comes first
            # sorted_lod_identifiers = sorted(lod_identifiers, key=lambda x: str(x) != str(nepalica_reg[place_ref_value]))
            
            # # Add the sorted LOD identifiers to the RDF graph
            # for lod_uri in sorted_lod_identifiers:
            #     g.add((place_node, rdfs.seeAlso, lod_uri))

        # Add the note_text to the graph 
        note_text = place["note_text"]
        if note_text:
            g.add((place_node, rdfs.comment, Literal(note_text)))

    # Loop through term entries and add them to the RDF graph
    term_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}term")
    )
    for term in terms:
        term_node = URIRef(f"{term_uri}#{term['prefLabel'].replace(' ', '_')}")
        g.add((term_node, RDF.type, SKOS_NS.Concept))
        g.add((term_node, SKOS_NS.prefLabel, Literal(term["prefLabel"])))
        g.add((term_node, SKOS_NS.comment, Literal(term["meaning"])))
        # Add alternative labels as skos:altLabel
        alt_labels = term.get("altLabel", [])
        for alt_label in alt_labels:
            g.add((term_node, SKOS_NS.altLabel, Literal(alt_label)))
        # Add the value for nepalica-gloss
        term_ref_value = term.get("term_ref")
        if term_ref_value:
            g.add((term_node, rdfs.seeAlso, nepalica_gloss[term_ref_value]))

    return g
