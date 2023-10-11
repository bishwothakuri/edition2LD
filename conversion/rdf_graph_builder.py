from typing import Dict
from rdflib import RDF, Graph, Literal, Namespace, URIRef


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


geonames = Namespace("https://sws.geonames.org/")
dbr = Namespace("https://dbpedia.org/resource/")
wiki = Namespace("https://de.wikipedia.org/wiki/")
viaf = Namespace("https://viaf.org/viaf/")
gnd = Namespace("https://d-nb.info/gnd/")
wikidata = Namespace("https://www.wikidata.org/wiki/")
gndo = Namespace("https://d-nb.info/standards/elementset/gnd#")


def bind_namespaces(g):
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


def add_document_metadata(g, document_metadata, physDesc_ref_target):
    # Check if "document_metadata" key exists in the metadata dictionary
    if "document_metadata" in document_metadata:
        document_node = URIRef(f"{nepalica}{physDesc_ref_target}")
        g.add((document_node, RDF.type, DC_NS.Document))

        # Iterate over the key-value pairs in "document_metadata" and add RDF triples
        for key, value in document_metadata.items():
            if value:
                # Mapping between document metadata keys and RDF predicates
                predicates = {
                    "Identifier:": DC_NS.identifier,
                    "Title:": DC_NS.title,
                    "Type, original:": DC_NS.type,
                    "Abstract:": DC_NS.abstract,
                    "Issued by and to:": DC_NS.issued_by,
                    "Place:": DC_NS.place,
                    "Donor, king:": DC_NS.donor,
                    "Type of endowment:": DC_NS.type_of_endowment,
                    "Region of endowment:": DC_NS.region_of_endowment,
                    "Purpose of endowment:": DC_NS.purpose_of_endowment,
                    "Amount of endowment:": DC_NS.amount_of_endowment,
                    "Date:": DC_NS.date,
                    "Language, script:": DC_NS.language,
                    "Width, height, and unit:": DC_NS.format,
                    "Material, binding, and color:": schema.material,
                    "Condition:": DC_NS.extent,
                    "Institution and reg. no.:": DC_NS.publisher,
                    "Source and details:": DC_NS.source,
                    "Running no., exposures:": DC_NS.hasPart,
                    "Created, modified, ID:": schema.created,
                    "Notes:": DC_NS.description,
                    "Technical terms:": DC_NS.subject
                }

                if key in predicates:
                    g.add((document_node, predicates[key], Literal(value, lang='en')))


def add_persons(g, persons, physDesc_ref_target):
    person_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}person")
    )
    for person in persons:
        person_node = URIRef(
            f"{person_uri}#{person['anglicized_name'].replace(' ', '_')}"
        )
        g.add((person_node, RDF.type, FOAF_NS.Person))
        g.add(
            (person_node, FOAF_NS.name, Literal(person["anglicized_name"], lang="ne"))
        )
        g.add((person_node, rdfs.label, Literal(person["anglicized_name"], lang="ne")))

        # Add devanagari_name as a custom property
        if "devanagari_name" in person:
            g.add(
                (
                    person_node,
                    rdfs.devanagariLabel,
                    Literal(person["devanagari_name"], lang="ne"),
                )
            )

        # Extract alternative names and add them to the RDF graph
        alternative_names = [
            alt_name
            for alt_name in person.get("alternative_names", [])
            if alt_name != person["anglicized_name"]
        ]
        for alt_name in alternative_names:
            g.add((person_node, SKOS_NS.altLabel, Literal(alt_name)))

        # Add the value for nepalica-reg:{{ person['n'] }}
        person_ref_value = person.get("n")
        if person_ref_value:
            rdfs_see_also_parent = nepalica_reg[person_ref_value]
            g.add((person_node, rdfs.seeAlso, rdfs_see_also_parent))

        # Add the LOD identifiers extracted from the metadata dictionary
        for lod_identifier_key, lod_identifier_values in person.items():
            if lod_identifier_key in [
                "gnd",
                "viaf",
                "wiki",
                "dbr",
                "geonames",
                "wikidata",
            ]:
                for lod_identifier_value in lod_identifier_values:
                    if lod_identifier_value:
                        lod_uri = URIRef(f"{lod_identifier_key}:{lod_identifier_value}")
                        g.add((person_node, rdfs.seeAlso, lod_uri))

        # Add the gender and its value to the RDF graph as a single value
        gender_value = person.get("gender")
        if gender_value:
            if gender_value[0].lower() == "female":
                gender_uri = schema.Female
            elif gender_value[0].lower() == "male":
                gender_uri = schema.Male
            else:
                # Handle other cases or use a default URI if necessary
                gender_uri = schema.OtherGender  # Replace with your desired default URI

            g.add((person_node, schema.gender, gender_uri))
        # Add surname if available
        if "surname" in person:
            g.add((person_node, gndo.surname, Literal(person["surname"], lang="ne")))

        # Add the note_text to the graph
        note_text = person["note_text"]
        if note_text:
            g.add((person_node, rdfs.comment, Literal(note_text, lang="ne")))


def add_places(g, places, physDesc_ref_target):
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
        g.add((place_node, GN_NS.name, Literal(place["place_name"], lang="ne")))
        # Extract alternative names and exclude the main place name from the list
        alternative_names = [
            alt_name
            for alt_name in place.get("alternative_names", [])
            if alt_name != place["place_name"]
        ]
        for alt_name in alternative_names:
            g.add((place_node, SKOS_NS.altLabel, Literal(alt_name, lang="ne")))
        # Add the value for nepalica-reg:{{ place['n'] }}
        place_ref_value = place.get("n")
        if place_ref_value:
            rdfs_see_also_parent = nepalica_reg[place_ref_value]
            g.add((place_node, rdfs.seeAlso, rdfs_see_also_parent))

            # Add the LOD identifiers extracted from the metadata dictionary
            for lod_identifier_key, lod_identifier_values in place.items():
                if lod_identifier_key in [
                    "gnd",
                    "viaf",
                    "wiki",
                    "dbr",
                    "geonames",
                    "wikidata",
                ]:
                    for lod_identifier_value in lod_identifier_values:
                        if lod_identifier_value:
                            lod_uri = URIRef(
                                f"{lod_identifier_key}:{lod_identifier_value}"
                            )
                            g.add((place_node, rdfs.seeAlso, lod_uri))

            # # Sort the LOD identifiers to ensure nepalica-reg comes first
            # sorted_lod_identifiers = sorted(lod_identifiers, key=lambda x: str(x) != str(nepalica_reg[place_ref_value]))

            # # Add the sorted LOD identifiers to the RDF graph
            # for lod_uri in sorted_lod_identifiers:
            #     g.add((place_node, rdfs.seeAlso, lod_uri))

        # Add the note_text to the graph
        note_text = place["note_text"]
        if note_text:
            g.add((place_node, rdfs.comment, Literal(note_text, lang="en")))


def add_terms(g, terms, physDesc_ref_target):
    # Loop through term entries and add them to the RDF graph
    term_uri = (
        URIRef(f"{nepalica}{physDesc_ref_target}")
        if physDesc_ref_target
        else URIRef(f"{nepalica}term")
    )
    for term in terms:
        term_node = URIRef(f"{term_uri}#{term['prefLabel'].replace(' ', '_')}")
        g.add((term_node, RDF.type, SKOS_NS.Concept))
        g.add((term_node, SKOS_NS.prefLabel, Literal(term["prefLabel"], lang="ne")))
        g.add((term_node, rdfs.comment, Literal(term["meaning"], lang="en")))

        # Add alternative labels as skos:altLabel
        alt_labels = term.get("altLabel", [])
        for alt_label in alt_labels:
            g.add((term_node, SKOS_NS.altLabel, Literal(alt_label, lang="ne")))

        # # Add the value for nepalica-gloss
        # term_ref_value = term.get("term_ref")
        # if term_ref_value:
        #     g.add((term_node, SKOS_NS.seeAlso, nepalica_gloss[term_ref_value]))  # Use SKOS_NS.seeAlso

        # Add the value for nepalica-gloss
        term_ref_value = term.get("term_ref")
        if term_ref_value:
            rdfs_see_also_parent = nepalica_gloss[term_ref_value]
            g.add((term_node, SKOS_NS.related, rdfs_see_also_parent))

        # Add the LOD identifiers extracted from the metadata dictionary
        for lod_identifier_key, lod_identifier_values in term.items():
            if lod_identifier_key in [
                "gnd",
                "viaf",
                "wiki",
                "dbr",
                "geonames",
                "wikidata",
            ]:
                for lod_identifier_value in lod_identifier_values:
                    if lod_identifier_value:
                        lod_uri = URIRef(f"{lod_identifier_key}:{lod_identifier_value}")
                        g.add((term_node, SKOS_NS.related, lod_uri))


def create_rdf_graph(metadata: Dict[str, list]) -> Graph:
    document_metadata = metadata.get("document_metadata", {})
    persons = metadata.get("persons", [])
    places = metadata.get("places", [])
    terms = metadata.get("terms", [])
    physDesc_ref_target = metadata.get("physDesc_id")

    # Initialize an RDF graph
    g = Graph()

    bind_namespaces(g)


     # Check if "document_metadata" key exists in the metadata dictionary
    if "document_metadata" in metadata:
        document_metadata = metadata["document_metadata"]
        document_node = URIRef(f"{nepalica}{physDesc_ref_target}")
        g.add((document_node, RDF.type, DC_NS.Document))

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
                    g.add((document_node, DC_NS.language, Literal(value, lang='en')))
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
                       

    add_persons(g, persons, physDesc_ref_target)
    add_places(g, places, physDesc_ref_target)
    add_terms(g, terms, physDesc_ref_target)

    return g
