import logging
import os
import json
from pathlib import Path

#import xml.etree.ElementTree as ET
from lxml import etree as ET
from rdflib import RDF, Graph, Literal, Namespace, URIRef, BNode
from serialization.turtle import save_turtle_serialization
from metadata.xml_tei_parser import extract_metadata_from_xml
from metadata.ont_item_mapper import extract_item_entity_id
from conversion.rdf_graph_builder import bind_namespaces

def judge_repetition(word, word_list):
    if not word_list:
        return None
    
    for i, item in enumerate(word_list):
        if item == word:
            return i
    
    return None



NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}
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


def create_rdf_from_nepaltokens(xml_file_path:str, json_file_path: str, metadata):
    #xml_file_path = os.path.join("data", "K_0440_0007.xml")
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    #get physDesc_id
    physDesc_id = root.find(".//tei:physDesc", NS)
    tei_id = root.attrib[f"{{{NS['xml']}}}id"]
    ref_element = physDesc_id.find(".//tei:ref", NS)
    if ref_element is not None and "target" in ref_element.attrib:
        target = ref_element.attrib["target"]
        ref_num = target.rsplit("/", 1)[-1]
        physDesc_id = ref_num

    # Find all the <w> elements
    w_elements = root.findall(".//tei:w", NS)

    g = Graph()

    #nepaltokens = Namespace("http://example.com/nepaltokens")
    ontolex = Namespace("http://www.w3.org/ns/lemon/ontolex#")
    example = Namespace("http://example.org/")

    bind_namespaces(g)
    g.bind('ontolex', ontolex)
    g.bind('', example)

    w_dict = {
        "w": [],
        "persName": [],
        "placeName": [],
        "term": []
    }

    # Add an id attribute to each <w> element
    for i, w_element in enumerate(w_elements, start=1):
        w = w_element.text
        index = judge_repetition(w, w_dict["w"])#w_list)
        if index == None:
            #w_list.append(w)
            w_dict["w"].append(w)
            w_parent = w_element.getparent() 
            if w_parent.tag == "{http://www.tei-c.org/ns/1.0}persName":
                w_dict["persName"].append(w_parent.get('n'))
            else:
                w_dict["persName"].append('')

            if w_parent.tag == "{http://www.tei-c.org/ns/1.0}placeName":
                w_dict["placeName"].append(w_parent.get('n'))
            else:
                w_dict["placeName"].append('')


    #xml_file_path = os.path.join("data", "K_0440_0007.xml")
    #json_file_path = os.path.join("data", "ont_item_occurrences.json")
    #metadata = extract_metadata_from_xml(xml_file_path, json_file_path)
    ont_item_occurrences = extract_item_entity_id(tei_id, json_file_path)

    persons = metadata.get("persons", [])    
    places = metadata.get("places", [])


    for i, word in enumerate(w_dict["w"]):
        format_id = "{:06}".format(i+1)
        format_next_id = "{:06}".format(i+2)
        nepaltokens_node = URIRef(f"nepalica:{physDesc_id}#ne{format_id}")
        nepaltokens_node_form = URIRef(f"nepalica:{physDesc_id}#ne{format_id}_form")
        #g.add((nepaltokens_node, ontolex.Form, Literal(word, lang = "ne")))
        
        # Add information of persname and placename into graph
        if w_dict['persName'][i]:
            g.add((nepaltokens_node, RDF.type, FOAF_NS.Person))
            ont_item_ids = ont_item_occurrences.get(w_dict['persName'][i], [])
            if ont_item_ids:
                ont_item_id = ont_item_ids[0]
                person = next((item for item in persons if item['n'] == ont_item_id), None)
                
                g.add(
                    (nepaltokens_node, FOAF_NS.name, Literal(person["anglicized_name"], lang="ne"))
                )
                g.add((nepaltokens_node, rdfs.label, Literal(person["anglicized_name"], lang="ne")))

                # Add devanagari_name as a custom property
                if "devanagari_name" in person:
                    g.add(
                        (
                            nepaltokens_node,
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
                    g.add((nepaltokens_node, SKOS_NS.altLabel, Literal(alt_name)))

                # Add the value for nepalica-reg:{{ person['n'] }}
                person_ref_value = person.get("n")
                if person_ref_value:
                    rdfs_see_also_parent = nepalica_reg[person_ref_value]
                    g.add((nepaltokens_node, rdfs.seeAlso, rdfs_see_also_parent))

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
                                g.add((nepaltokens_node, rdfs.seeAlso, lod_uri))

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

                    g.add((nepaltokens_node, schema.gender, gender_uri))
                # Add surname if available
                if "surname" in person:
                    g.add((nepaltokens_node, gndo.surname, Literal(person["surname"], lang="ne")))

                # Add the note_text to the graph
                note_text = person["note_text"]
                if note_text:
                    g.add((nepaltokens_node, rdfs.comment, Literal(note_text, lang="ne")))


        if w_dict['placeName'][i]:
            g.add((nepaltokens_node, RDF.type, GN_NS.Feature))
            ont_item_ids = ont_item_occurrences.get(w_dict['placeName'][i], [])
            if ont_item_ids:
                ont_item_id = ont_item_ids[0]
                place = next((item for item in places if item['n'] == ont_item_id), None)
                
                g.add((nepaltokens_node, RDF.type, GN_NS.Feature))
                g.add((nepaltokens_node, GN_NS.name, Literal(place["place_name"], lang="ne")))
                # Extract alternative names and exclude the main place name from the list
                alternative_names = [
                    alt_name
                    for alt_name in place.get("alternative_names", [])
                    if alt_name != place["place_name"]
                ]
                for alt_name in alternative_names:
                    g.add((nepaltokens_node, SKOS_NS.altLabel, Literal(alt_name, lang="ne")))
                # Add the value for nepalica-reg:{{ place['n'] }}
                place_ref_value = place.get("n")
                if place_ref_value:
                    rdfs_see_also_parent = nepalica_reg[place_ref_value]
                    g.add((nepaltokens_node, rdfs.seeAlso, rdfs_see_also_parent))

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
                                    g.add((nepaltokens_node, rdfs.seeAlso, lod_uri))

                # Add the note_text to the graph
                note_text = place["note_text"]
                if note_text:
                    g.add((nepaltokens_node, rdfs.comment, Literal(note_text, lang="en")))
        
        if word is None:
            g.add((nepaltokens_node, RDF.type, ontolex.LexicalEntry))
            g.add((nepaltokens_node, RDF.type, ontolex.Word)) 
        elif word.isnumeric():
            g.add((nepaltokens_node, RDF.type, dbr.Number))
            #g.add((nepaltokens_node, ontolex.writtenRep, Literal(word, lang="en")))
        else:
            #g.add((nepaltokens_node, ontolex.LexicalEntry, ontolex.Word))
            g.add((nepaltokens_node, RDF.type, ontolex.LexicalEntry))
            g.add((nepaltokens_node, RDF.type, ontolex.Word))

        g.add((nepaltokens_node, ontolex.canonicalForm, nepaltokens_node_form))
        g.add((nepaltokens_node, example.followedBy, URIRef(f"nepalica:{physDesc_id}#ne{format_next_id}")))
        
        #g.add((nepaltokens_node_form, ontolex.Form, Literal(word, lang = "ne")))
        g.add((nepaltokens_node_form, RDF.type, ontolex.Form))
        g.add((nepaltokens_node_form, ontolex.writtenRep, Literal(word, lang = "ne")))

    return g



