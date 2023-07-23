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
nepalica_gloss = Namespace("https://nepalica.hadw-bw.de/nepal/words/viewitem/")

geonames = Namespace("https://sws.geonames.org/")
dbr = Namespace("https://dbpedia.org/resource/")
wiki = Namespace("https://de.wikipedia.org/wiki/")
viaf = Namespace("https://viaf.org/viaf/")
gnd = Namespace("https://d-nb.info/gnd/")
wikidata = Namespace("https://www.wikidata.org/wiki/")




def create_rdf_graph(metadata: Dict[str, list]) -> Graph:
    # persons = metadata.get("persons", [])
    places = metadata.get("places", [])
    terms = metadata.get("terms", [])
    physDesc_ref_target = metadata.get("physDesc_id")

    g = Graph()
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
    # g.bind("", )

    g.namespace_manager.bind(
        "nepalica", nepalica, override=False
    )  # Use NamespaceManager to bind the prefix
    g.bind("nepalica-reg", nepalica_reg)

    # person_uri = (
        # URIRef(f"{nepalica}{physDesc_ref_target}")
        # if physDesc_ref_target
        # else URIRef(f"{nepalica}person")
    # )
    # for person in persons:
        # person_node = URIRef(f"{person_uri}#{person['person_name'].replace(' ', '_')}")
        # g.add((person_node, RDF.type, FOAF_NS.Person))
        # g.add((person_node, FOAF_NS.name, Literal(person["person_name"])))

    place_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}place")
    )
    for place in places:
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
            g.add((place_node, rdfs.seeAlso, nepalica_reg[place_ref_value]))


    term_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}term")
    )
    for term in terms:
        term_node = URIRef(f"{term_uri}#{term['prefLabel'].replace(' ', '_')}")
        # ref_num = term.get(
        #     "ref_num"
        # )  # Extract the reference number from the term metadata
        g.add((term_node, RDF.type, SKOS_NS.Concept))
        g.add((term_node, SKOS_NS.prefLabel, Literal(term["prefLabel"])))
        g.add((term_node, SKOS_NS.comment, Literal(term["meaning"])))
        # Add alternative labels as skos:altLabel
        alt_labels = term.get("altLabel", [])
        for alt_label in alt_labels:
            g.add((term_node, SKOS_NS.altLabel, Literal(alt_label)))
        # Add the value for nepalica-gloss:{{ term['term_ref'] }}
        term_ref_value = term.get("term_ref")
        if term_ref_value:
            g.add((term_node, rdfs.seeAlso, nepalica_reg[term_ref_value]))
        # Use the identifiers from the metadata dictionary
        if "geonames" in term:
            g.add((term_node, geonames.geonames, Literal(term["geonames"])))
        if "dbr" in term:
            g.add((term_node, dbr.dbr, Literal(term["dbr"])))
        if "wiki" in term:
            g.add((term_node, wiki.wiki, Literal(term["wiki"])))
        if "wikidata" in term:
            g.add((term_node, wikidata.wikidata, Literal(term["wikidata"])))
        if "viaf" in term:
            g.add((term_node, viaf.viaf, Literal(term["viaf"])))
        if "gnd" in term:
            g.add((term_node, gnd.gnd, Literal(term["gnd"])))

        # if ref_num:
        #     ref_num = ref_num.split("/")[
        #         -1
        #     ]  # Extract the number value from the full URI
        #     g.add(
        #         (term_node, SKOS_NS.related, URIRef(ref_num))
        #     )  # Use prefix in the related gloss term

    return g
