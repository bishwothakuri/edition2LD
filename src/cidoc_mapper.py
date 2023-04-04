from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS

CIDOC = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


def map_to_cidoc(metadata):
    cidoc_graph = Graph()
    cidoc_graph.parse("cidoc_crm.rdf", format="xml")
    cidoc_ns = dict(cidoc_graph.namespaces())
    mapped_metadata = []
    for s, p, o in metadata:
        if p in cidoc_graph.predicates():
            cidoc_p = cidoc_graph.preferredLabel(p, lang="en")[0][0]
            if o.datatype:
                cidoc_o = Literal(o.value, datatype=o.datatype)
            elif o.language:
                cidoc_o = Literal(o.value, lang=o.language)
            else:
                cidoc_o = Literal(o.value)
            mapped_metadata.append((s, CIDOC[cidoc_p], cidoc_o))
    return mapped_metadata
