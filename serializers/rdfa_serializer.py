from rdflib import plugin
from rdflib.serializer import Serializer

plugin.register("rdfa", Serializer, "rdflib.plugins.serializers.rdfa", "RdfaSerializer")


def serialize_graph_to_rdfa(graph):
    serializer = Serializer("rdfa")
    rdfa = graph.serialize(format="rdfa", destination=None, serializer=serializer)
    return rdfa
