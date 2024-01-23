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

project_description = "This is a text edition of the project 'Documents on the History of Religion and Law of Pre-modern Nepal', Heidelberg Academy of Sciences and Humanities, https://www.hadw-bw.de/nepal."

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
    g.bind("lime", lime)
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

document_description = "This is a text edition of the project 'Documents on the History of Religion and Law of Pre-modern Nepal', Heidelberg Academy of Sciences and Humanities, https://www.hadw-bw.de/nepal."
id_counter = count(start=1)

def add_lexical_entry_information(g, token_node, word, rdf_graph):
    if word["text"].isnumeric():
        g.add((token_node, RDF.type, dbr.Number))
        g.add((token_node, ontolex.writtenRep, Literal(word["text"], lang="en")))
    elif "tag_name" in word:
        section_triples = copy_rdf_section_by_text(rdf_graph, word["text"])
        if section_triples:
            for triple in section_triples:
                subject_uri = URIRef(token_node)
                g.add((subject_uri, triple[1], triple[2]))
    else:
        g.add((token_node, RDF.type, ontolex.LexicalEntry))
        g.add((token_node, RDF.type, ontolex.Word))
        g.add((token_node, ontolex.canonicalForm, URIRef(f"{token_node}_form")))
        
        canonical_form_node = URIRef(f"{token_node}_form")
        g.add((canonical_form_node, RDF.type, ontolex.Form))
        g.add((canonical_form_node, ontolex.writtenRep, Literal(word["text"], lang="en")))
        # g.add((token_node, ex.followedBy, URIRef(f"{token_node[:-7]}{int(token_node[-6:])+1:06}")))

def add_tokenize_text(g, words, physDesc_ref_target, rdf_graph):
    token_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}word")
    )
    for i, word in enumerate(words):
        current_id = next(id_counter)
        token_node = URIRef(f"{token_uri}#en{current_id:06}")
        add_lexical_entry_information(g, token_node, word, rdf_graph)
        
        if i < len(words) - 1:
            next_id = current_id + 1
            next_token_node = URIRef(f"{token_uri}#en{next_id:06}")
            g.add((token_node, ex.followedBy, next_token_node))


def create_rdf_graph_from_tokenized_word(metadata: Dict[str, list], token_dict: Dict[str, list], rdf_graph: Graph) -> Graph:
    physDesc_ref_target = metadata.get("physDesc_id")
    words = token_dict.get("words", [])

    # Initialize an RDF graph
    g = Graph()

    bind_namespaces(g)
    document_metadata = metadata.get("document_metadata", {})
    add_tokenize_text(g, words, physDesc_ref_target, rdf_graph)

            
    # Check if "document_metadata" key exists in the metadata dictionary
    if "document_metadata" in metadata:
        document_metadata = metadata["document_metadata"]
        document_node = URIRef(f"{nepalica}{physDesc_ref_target}")
        g.add((document_node, RDF.type, DC_NS.Document))
        g.add((document_node, RDF.type, lime.Lexicon))
        g.add((document_node, DC_NS.description, Literal(document_description, lang='en')))
        g.add((document_node, DC_NS.language, lexvo.ne))
        g.add((document_node, DC_NS.language, lexvo.en))

        # Iterate over the key-value pairs in "document_metadata" and add RDF triples
        for key, value in document_metadata.items(): # type: ignore
            # Check if the value is present for the current key
            if value:
                if key == "Identifier:":
                    g.add((document_node, DC_NS.identifier, Literal(value, lang='en')))
                elif key == "Title:":
                    g.add((document_node, DC_NS.title, Literal(value, lang='en')))
                elif key == "Type, original:":
                    g.add((document_node, DC_NS.type, Literal(value, lang='en')))
                elif key == "Abstract:":
                    g.add((document_node, DC_NS.abstract, Literal(value, lang='en')))
                elif key == "Issued by and to:":
                    g.add((document_node, DC_NS.issued_by, Literal(value, lang='en')))
                elif key == "Place:":
                   g.add((document_node, DC_NS.place, Literal(value, lang='en')))
                elif key == "Donor, king:":
                    g.add((document_node, DC_NS.donor, Literal(value, lang='en')))
                elif key == "Type of endowment:":
                    g.add((document_node, DC_NS.type_of_endowment, Literal(value, lang='en')))
                elif key == "Region of endowment:":
                    g.add((document_node, DC_NS.region_of_endowment, Literal(value, lang='en')))
                elif key == "Purpose of endowment:":
                    g.add((document_node, DC_NS.purpose_of_endowment, Literal(value, lang='en')))
                elif key == "Amount of endowment:":
                    g.add((document_node, DC_NS.amount_of_endowment, Literal(value, lang='en')))
                elif key == "Date:":
                    g.add((document_node, DC_NS.date, Literal(value, lang='en')))
                elif key == "Language, script:":
                    g.add((document_node, lime.language, Literal(value, lang='en')))
                elif key == "Width, height, and unit:":
                    g.add((document_node, DC_NS["format"], Literal(value, lang='en')))
                elif key == "Material, binding, and color:":
                    g.add((document_node, schema.material, Literal(value, lang='en')))
                elif key == "Condition:":
                    g.add((document_node, DC_NS.extent, Literal(value, lang='en')))
                elif key == "Institution and reg. no.:":
                    g.add((document_node, DC_NS.publisher, Literal(value, lang='en')))
                elif key == "Source and details:":
                    g.add((document_node, DC_NS.source, Literal(value, lang='en')))
                elif key == "Running no., exposures:":
                    g.add((document_node, DC_NS.hasPart, Literal(value, lang='en')))
                elif key == "Created, modified, ID:":
                    g.add((document_node, schema.created, Literal(value, lang='en')))
                elif key == "Notes:":
                    g.add((document_node, DC_NS.description, Literal(value, lang='en')))
                elif key == "Technical terms:":
                    g.add((document_node, DC_NS.subject, Literal(value, lang='en')))
            
    return g



