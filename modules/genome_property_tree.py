#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""
import json

# TODO: Root Property, Type cast to dict, Type cast to str, Length, Iterable, Dictionary Type Syntax.

class GenomePropertyTree(object):
    """
    This class contains a representation of the EBI InterPro Genome Properties database. Internally, the instantiated
    object contains a polytree of all genome properties connected from root to leaf (parent to child). A dictionary is
    also included which points to each tree node for fast lookups by genome property identifier.
    """

    def __init__(self, *genome_properties):
        self.genome_properties_dictionary = {}
        for new_property in genome_properties:
            self.genome_properties_dictionary[new_property.id] = new_property

        self.build_genome_property_connections()

    def build_genome_property_connections(self):
        """
        Build connections between parent-child genome properties in the dictionary. This creates the polytree.
        """
        for genome_property in self.genome_properties_dictionary.values():
            genome_property.add_child_connections(self.genome_properties_dictionary)

    def print_human_readable_genome_properties_list(self):
        """
        Prints a human readable summery for all properties in a genome properties dictionary.
        """
        for genome_property in self.genome_properties_dictionary.values():
            parent_ids = [parent.id for parent in genome_property.parents]
            child_ids = [child.id for child in genome_property.children]

            if not parent_ids:
                parent_ids = "[ No Parent Genome Properties ]"

            if not child_ids:
                child_ids = "[ No Child Properties ]"

            print(
                "\n" + genome_property.id + " (" + genome_property.name + ")" + " Type: [" +
                genome_property.type + "]" + " Parents: " + str(parent_ids) + " Children: " + str(child_ids))
            print(
                '=====================================================================================================')
            for step in genome_property.steps:
                print(str(step) + "\n")

    def create_graph_node_json(self, to_list=False):
        """
        Creates a JSON representation of a genome property dictionary.
        :param to_list: Return as a list instead of a JSON formatted string.
        :return: A JSON formatted string of a list of each properties JSON representation.
        """
        nodes = []
        for genome_property in self.genome_properties_dictionary.values():
            genome_property_dict = genome_property.to_json(as_dict=True)
            nodes.append(genome_property_dict)

        if to_list:
            output = nodes
        else:
            output = json.dumps(nodes)

        return output

    def create_graph_links_json(self, to_list=False):
        """
        Creates a JSON representation of a genome property links.
        :param to_list: Return as a list instead of a JSON formatted string.
        :return: A JSON formatted string of a list of each properties JSON representation.
        """
        links = []
        for genome_property in self.genome_properties_dictionary.values():
            if genome_property.parents:
                for parent in genome_property.parents:
                    link = {'source': parent.id, 'target': genome_property.id}
                    links.append(link)

        if to_list:
            output = links
        else:
            output = json.dumps(links)

        return output
