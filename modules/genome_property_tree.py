#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json


class GenomePropertyTree(object):
    """
    This class contains a representation of a set of nested genome properties. Internally, the instantiated
    object contains a polytree of genome properties connected from root to leaf (parent to child). A dictionary is
    also included which points to each tree node for fast lookups by genome property identifier.
    """

    def __init__(self, *genome_properties):
        """
        When the object is created create a dictionary and connect the nodes to each other to form the polytree.
        :param genome_properties: One or more genome property objects.
        """
        self.genome_properties_dictionary = {}
        for new_property in genome_properties:
            self.genome_properties_dictionary[new_property.id] = new_property

        self.build_genome_property_connections()

    @property
    def root(self):
        """
        Gets the top level genome properties object in a genome properties tree.
        :return: The root genome property of the genome properties tree.
        """
        genome_property = next(iter(self.genome_properties_dictionary.values()))

        while True:
            if genome_property.parents:
                genome_property = genome_property.parents[0]
            else:
                break

        return genome_property

    @property
    def leafs(self):
        """
        Returns the leaf nodes of the polytree.
        :return: A list of all genome property objects with no children.
        """
        for genome_property in self:
            if not genome_property.children:
                yield genome_property

    def build_genome_property_connections(self):
        """
        Build connections between parent-child genome properties in the dictionary. This creates the polytree.
        """
        for genome_property in self:
            child_identifiers = genome_property.child_genome_property_identifiers

            for identifier in child_identifiers:
                child_genome_property = self[identifier]

                if child_genome_property:
                    genome_property.children.append(child_genome_property)
                    child_genome_property.parents.append(genome_property)

    def to_json(self, nodes_and_links=False):
        """
        Converts the object to a JSON representation.
        :param nodes_and_links: If True, returns the JSON in node and link format.
        :return: A JSON formatted string representing the genome property tree.
        """
        if nodes_and_links:
            nodes = self.create_graph_node_json(as_list=True)
            links = self.create_graph_links_json(as_list=True)
            final_json = json.dumps({'nodes': nodes, 'links': links})
        else:
            final_json = self.create_nested_json()

        return final_json

    def create_nested_json(self, current_property=None, as_dict=False):
        """
        Converts the object to a nested JSON representation.
        :param current_property: The current root genome property (for recursion)
        :param as_dict: Returns Return a dictionary for incorporation into other json objects.
        :return: A JSON formatted string or dictionary representing the object.
        """
        if current_property:
            root_genome_property = current_property
        else:
            root_genome_property = self.root

        root_json = root_genome_property.to_json(as_dict=True)

        child_jsons = []
        for child in root_genome_property.children:
            child_json = self.create_nested_json(child, as_dict=True)
            child_jsons.append(child_json)

        root_json['children'] = child_jsons

        if as_dict:
            output = root_json
        else:
            output = json.dumps(root_json)

        return output

    def create_graph_node_json(self, as_list=False):
        """
        Creates a JSON representation of a genome property dictionary.
        :param as_list: Return as a list instead of a JSON formatted string.
        :return: A JSON formatted string of a list of each properties JSON representation.
        """
        nodes = []
        for genome_property in self:
            genome_property_dict = genome_property.to_json(as_dict=True)
            nodes.append(genome_property_dict)

        if as_list:
            output = nodes
        else:
            output = json.dumps(nodes)

        return output

    def create_graph_links_json(self, as_list=False):
        """
        Creates a JSON representation of a genome property links.
        :param as_list: Return as a list instead of a JSON formatted string.
        :return: A JSON formatted string of a list of each properties JSON representation.
        """
        links = []
        for genome_property in self:
            if genome_property.parents:
                for parent in genome_property.parents:
                    link = {'source': parent.id, 'target': genome_property.id}
                    links.append(link)

        if as_list:
            output = links
        else:
            output = json.dumps(links)

        return output

    def __getitem__(self, item):
        return self.genome_properties_dictionary.get(item)

    def __len__(self):
        return len(self.genome_properties_dictionary)

    def __iter__(self):
        for genome_property in self.genome_properties_dictionary.values():
            yield genome_property

    def __contains__(self, item):
        return True if item in self.genome_properties_dictionary else False

    def __repr__(self):
        repr_data = []
        for genome_property in self:
            repr_data.append(str(genome_property))

        return '\n'.join(repr_data)

    def __str__(self):
        """
        Prints a human readable summary for all properties in a genome properties dictionary.
        """
        for genome_property in self:
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
