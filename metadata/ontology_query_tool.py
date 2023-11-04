import os
import rdflib
from rdflib import Namespace
from rdflib.plugins.sparql.processor import prepareQuery  

def process_query_by_id(individual_id):
    try:
        # Create a Graph object to parse the RDF data
        g = rdflib.Graph()
        ontology_file_path = os.path.join("data", "nepalpeople.ttl")
        g.parse(ontology_file_path, format="turtle")

        # Define the namespaces
        gnd = Namespace("http://d-nb.info/gnd/")
        agrelon = Namespace("https://d-nb.info/standards/elementset/agrelon#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        # Define the query with a parameter
        query_str = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX gnd: <http://d-nb.info/gnd/>
        PREFIX agrelon: <https://d-nb.info/standards/elementset/agrelon#>

        SELECT ?individual ?personalName ?forename ?lastname ?hasParent ?hasBiologicalChild
        WHERE {
        ?individual rdfs:seeAlso ?individual_url .
        ?individual gnd:personalName ?personalName .
        ?individual gnd:forename ?forename .
        ?individual gnd:lastname ?lastname .
        OPTIONAL { ?individual agrelon:hasParent ?hasParent . }
        OPTIONAL { ?individual agrelon:hasBiologicalChild ?hasBiologicalChild . }
        }
        """

        # Prepare the query
        query = prepareQuery(query_str, initNs={'rdfs': rdfs, 'gnd': gnd, 'agrelon': agrelon})

        # Execute the query with the provided individual_id
        results = g.query(query, initBindings={'individual_url': rdflib.URIRef(f"https://nepalica.hadw-bw.de/nepal/ontologies/viewitem/{individual_id}")})

        query_results = {
            "personal_name": None,
            "forename": None,
            "lastname": None,
            "has_parent": None
        }

        # Store the results in the dictionary
        for row in results:
            query_results["personal_name"] = row["personalName"].toPython() # type: ignore
            query_results["forename"] = row["forename"].toPython() # type: ignore
            query_results["lastname"] = row["lastname"].toPython() # type: ignore
            query_results["has_parent"] = row["hasParent"].toPython() # type: ignore

        return query_results

    except Exception as e:
        print("Error processing the query:", e)
        return None
    

