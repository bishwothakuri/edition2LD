import jinja2
from jinja2 import Environment, FileSystemLoader

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF, SKOS

def generate_rdfa_from_graph(g: Graph, file_name: str) -> bytes:
    # Define SPARQL queries
    person_query = """
    SELECT ?person ?name WHERE {
      ?person a foaf:Person .
      ?person foaf:name ?name .
    }
    """
    place_query = """
    SELECT ?place ?name WHERE {
      ?place a <http://www.geonames.org/ontology#Feature> .
      ?place <http://www.geonames.org/ontology#name> ?name .
    }
    """
    term_query = """
    SELECT ?term ?term_label ?meaning ?ref_num WHERE {
      ?term a skos:Concept .
      ?term skos:prefLabel ?term_label .
      OPTIONAL { ?term skos:definition ?meaning . }
      OPTIONAL { ?term skos:related ?ref_term . ?ref_term <https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/ref_num> ?ref_num . }
    }
    """

    # Execute SPARQL queries and store results in dictionaries
    persons = {}
    for row in g.query(person_query, initBindings={"foaf": FOAF}):
        person_uri = row["person"].toPython()
        persons[person_uri] = {
            "name": row["name"].toPython(),
        }
    places = {}
    for row in g.query(place_query):
        place_uri = row["place"].toPython()
        places[place_uri] = {
            "name": row["name"].toPython(),
            "alternative_names": [],
        }
        alt_name = row.get("alt_name", None)
        if alt_name is not None:
            places[place_uri]["alternative_names"].append(alt_name.toPython())

                                                          
    terms = {}
    for row in g.query(term_query, initBindings={"skos": SKOS}):
        term_uri = row["term"].toPython()
        ref_num = row.get("ref_num", "")  # Assign an empty string if ref_num is None
        terms[term_uri] = {
            "term": row["term_label"].toPython(),
            "meaning": row.get("meaning", None),
            "ref_num": ref_num,
        }

    # Load the Jinja2 template file
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates"))
    template = env.get_template("rdfa.html")

    # Pass the data to the template context
    template_context = {
        "file_name": file_name,
        "persons": persons,
        "places": places,
        "terms": terms,
    }

    # Render the template using the context variables
    html = template.render(template_context)

    # Return the resulting HTML string as bytes
    return html.encode("utf-8")
