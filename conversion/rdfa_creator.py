import jinja2
from jinja2 import Environment, FileSystemLoader
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import FOAF, SKOS

def generate_rdfa_from_graph(g: Graph, file_name: str) -> bytes:

     # Define the namespace bindings
    FOAF_NS = FOAF
    GN_NS = Namespace("http://www.geonames.org/ontology#")
    SKOS_NS = SKOS
    nepalica_reg = Namespace("https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/")

    # Define SPARQL queries
    # person_query = """
    # SELECT ?person ?name WHERE {
    #   ?person a foaf:Person .
    #   ?person foaf:name ?name .
    # }
    # """

    place_query = """
    SELECT ?place ?name ?alt_name ?place_ref WHERE {
        ?place a gn:Feature .
        ?place gn:name ?name .
        OPTIONAL { ?place skos:altLabel ?alt_name . }
        OPTIONAL { ?place rdfs:seeAlso ?place_ref . }
     }
    """

    term_query = """
    SELECT ?term ?term_label ?meaning ?ref_num ?alt_label ?term_ref WHERE {
      ?term a skos:Concept .
      ?term skos:prefLabel ?term_label .
      OPTIONAL { ?term skos:comment ?meaning . }
      OPTIONAL { ?term skos:related ?ref_term . ?ref_term nepalica-reg:ref_num ?ref_num . }
      OPTIONAL { ?term skos:altLabel ?alt_label . }
      OPTIONAL { ?term rdfs:seeAlso ?term_ref . }
    }
    """

    # Execute SPARQL queries and store results in dictionaries
    # persons = {}
    # for row in g.query(person_query, initBindings={"foaf": FOAF}):
        # person_uri = row["person"].toPython()
        # persons[person_uri] = {
            # "name": row["name"].toPython(),
        # }
     
    places = {}
    for row in g.query(place_query, initBindings={"gn": GN_NS, "skos": SKOS_NS, "nepalica-reg": nepalica_reg}):
        place_uri = row["place"].toPython()
        ref_num_uri = row.get("place_ref", "")
        ref_num = ref_num_uri.split("/")[-1] if ref_num_uri else ""  # Extract the number part
        alt_name = row.get("alt_name", None)
        if place_uri not in places:
            places[place_uri] = {
                "name": row["name"].toPython(),
                "alternative_names": [],
                "place_ref": row.get("place_ref", "").toPython(),
                "ref_num": ref_num,
                "lod_identifiers": [],  # Initialize a list for LOD identifiers
            }
        if alt_name is not None:
            places[place_uri]["alternative_names"].append(alt_name.toPython())
        
        # Add LOD identifiers to the list
        lod_identifier = row.get("place_ref", None)
        if lod_identifier is not None:
            places[place_uri]["lod_identifiers"].append(lod_identifier.toPython())

    terms = {}
    for row in g.query(term_query, initBindings={"skos": SKOS_NS, "nepalica-reg": nepalica_reg}):
        term_uri = row["term"].toPython()
        ref_num_uri = row.get("term_ref", "") 
        ref_num = ref_num_uri.split("/")[-1] if ref_num_uri else ""  # Extract the number part
        pref_label = row["term_label"].toPython()
        alt_label = row.get("alt_label", None)
        meaning = row.get("meaning", None)

        terms[term_uri] = {
            "term": pref_label,
            "meaning": meaning,
            "ref_num": ref_num,
            "alt_labels": [],
        }

        if alt_label is not None:
            terms[term_uri]["alt_labels"].append(alt_label.toPython())

        
    # Load the Jinja2 template file
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates"))
    template = env.get_template("rdfa.xhtml")

    # Pass the data to the template context
    template_context = {
        "file_name": file_name,
        # "persons": persons,
        "places": places,
        "terms": terms,
    }

    # Render the template using the context variables
    html = template.render(template_context)

    # Return the resulting HTML string as bytes
    return html.encode("utf-8")
