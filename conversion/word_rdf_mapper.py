from typing import Dict
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from itertools import count

# Define RDF namespaces for the ontology
FOAF_NS = Namespace("http://xmlns.com/foaf/0.1/")
GN_NS = Namespace("http://www.geonames.org/ontology#")
SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC_NS = Namespace("http://purl.org/dc/terms/")

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
dbpedia = Namespace("https://dief.tools.dbpedia.org/server/ontology/classes/Place")
geonames = Namespace("https://sws.geonames.org/")
dbr = Namespace("https://dbpedia.org/resource/")
wiki = Namespace("https://de.wikipedia.org/wiki/")
viaf = Namespace("https://viaf.org/viaf/")
gnd = Namespace("https://d-nb.info/gnd/")
wikidata = Namespace("https://www.wikidata.org/wiki/")
gndo = Namespace("https://d-nb.info/standards/elementset/gnd#")
agrelon = Namespace("https://d-nb.info/standards/elementset/agrelon#")
ontolex = Namespace("http://www.w3.org/ns/lemon/ontolex#")
lime = Namespace("http://www.w3.org/ns/lemon/lime#")
lexvo = Namespace("http://lexvo.org/id/iso639-3/")
ex = Namespace("http://example.org/")

project_description = "This is a text edition of the project “Documents on the History of Religion and Law of Pre-modern Nepal”, Heidelberg Academy of Sciences and Humanities, https://www.hadw-bw.de/nepal."

def bind_namespaces(g):
    # Bind RDF namespaces for use in the graph
    g.bind("foaf", FOAF_NS)
    g.bind("gn", GN_NS)
    g.bind("skos", SKOS_NS)
    g.bind("dct", DC_NS)
    g.bind("dbr", dbr)
    g.bind("wiki", wiki)
    g.bind("geonames", geonames)
    g.bind("viaf", viaf)
    g.bind("gnd", gnd)
    g.bind("wikidata", wikidata)
    g.bind("gndo", gndo)
    g.bind("schema", schema)
    g.bind("agrelon", agrelon)
    g.bind("ontolex", ontolex)
    g.bind("", ex)

    # Bind custom namespaces using the NamespaceManager
    g.namespace_manager.bind("nepalica", nepalica, override=False)
    g.namespace_manager.bind("nepalica_reg", nepalica_reg)

def copy_rdf_section_by_text(rdf_graph, text):
    # Iterate over all RDF triples in the graph
    for s, p, o in rdf_graph:
        # Check if the object is a Literal with the specified text
        if isinstance(o, Literal) and o.value == text:
            # Retrieve the subject URI
            subject_uri = s
            # Retrieve all triples with the subject URI
            section_triples = list(rdf_graph.triples((subject_uri, None, None)))
            return section_triples
    return None

id_counter = count(start=0)
document_description = "This is a text edition of the project “Documents on the History of Religion and Law of Pre-modern Nepal”, Heidelberg Academy of Sciences and Humanities, https://www.hadw-bw.de/nepal.”@en"
def add_tokenize_text(g, words, physDesc_ref_target, rdf_graph):
    token_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}word")
    )
    for i, word in enumerate(words):
        current_id = next(id_counter)
        token_node = URIRef(f"{token_uri}#en_{current_id:06}")
        g.add((token_node, RDF.type, ontolex.LexicalEntry))
        g.add((token_node, RDF.type, ontolex.Word))
        g.add((token_node, DC_NS.language, lexvo.ne))
        g.add((token_node, DC_NS.language, lexvo.en))
        g.add((token_node, DC_NS.description, Literal(document_description)))


        # Check if the word has a tag_name
        if "tag_name" in word:
            # Retrieve the corresponding section from the RDF graph
            tag_name = word["tag_name"]
            section_triples = copy_rdf_section_by_text(rdf_graph, word["text"])

            # Add the triples from the section to the current graph
            if section_triples:
                for triple in section_triples:
                    subject_uri = URIRef(token_node)
                    g.add((subject_uri, triple[1], triple[2]))
        else:
            # Add triples for the word without a tag_name
            g.add((token_node, ontolex.writtenRep, Literal(word["text"], lang="en")))

        if i < len(words) - 1:
            next_id = current_id + 1
            next_token_node = URIRef(f"{token_uri}#en_{next_id:06}")
            g.add((token_node, ex.followedBy, next_token_node))

def create_rdf_graph_from_tokenized_word(metadata: Dict[str, list], token_dict: Dict[str, list], rdf_graph: Graph) -> Graph:
    physDesc_ref_target = metadata.get("physDesc_id")
    words = token_dict.get("words", [])

    # Initialize an RDF graph
    g = Graph()

    bind_namespaces(g)

    add_tokenize_text(g, words, physDesc_ref_target, rdf_graph)

    return g
