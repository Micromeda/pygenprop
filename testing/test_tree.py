#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the genome_property_tree module.
"""

import json
import unittest

from copy import deepcopy

from modules.tree import GenomePropertiesTree
from modules.flat_file_parser import parse_genome_property
from modules.flat_file_parser import parse_genome_property_file


class TestGenomePropertyTree(unittest.TestCase):
    """A unit testing class for testing the tree.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """
        Test Properties Polytree Structure:

        GenProp0002 -->             --> GenProp0089
                        GenProp0066
        GenProp0003 -->             --> GenProp0092

        Note 1: The structure of the property tree used above is not the common case.
        Commonly there should be only a single root node.
        """

        property_rows_one = [
            ('AC', 'GenProp0002'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0066;')
        ]

        property_rows_two = [
            ('AC', 'GenProp0003'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0066;')
        ]

        property_rows_three = [
            ('AC', 'GenProp0066'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0089;'),
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0092;'),
        ]

        property_rows_four = [
            ('AC', 'GenProp0089'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03564; sufficient;')
        ]

        property_rows_five = [
            ('AC', 'GenProp0092'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03564; sufficient;')
        ]

        property_one = parse_genome_property(property_rows_one)
        property_two = parse_genome_property(property_rows_two)
        property_three = parse_genome_property(property_rows_three)
        property_four = parse_genome_property(property_rows_four)
        property_five = parse_genome_property(property_rows_five)

        cls.raw_properties = [property_one, property_two, property_three, property_four, property_five]

    @property
    def properties(self):
        """
        Returns a copy of the properties created during the setUpClass.
        :return: A deep copy of the test genome properties.
        """
        return deepcopy(self.raw_properties)

    def test_build_genome_property_connections(self):
        """Test that we can add child and parent genome properties."""

        test_properties = self.properties

        property_one = test_properties[0]
        property_two = test_properties[1]
        property_three = test_properties[2]
        property_four = test_properties[3]
        property_five = test_properties[4]

        property_tree = GenomePropertiesTree(*test_properties)

        self.assertEqual(property_tree[property_one.id].children[0], property_three)
        self.assertEqual(property_tree[property_two.id].children[0], property_three)
        self.assertCountEqual(property_tree[property_three.id].parents, [property_one, property_two])
        self.assertCountEqual(property_tree[property_three.id].children, [property_four, property_five])
        self.assertEqual(property_tree[property_four.id].parents[0], property_three)
        self.assertEqual(property_tree[property_five.id].parents[0], property_three)

    def test_find_leaf_nodes(self):
        """Test we can find the right leaf nodes."""

        property_tree = GenomePropertiesTree(*self.properties)
        leaf_ids = [leaf.id for leaf in property_tree.leafs]

        self.assertCountEqual(leaf_ids, ['GenProp0089', 'GenProp0092'])

    def test_find_root_node(self):
        """Test that we can find the correct genome property root."""

        property_tree = GenomePropertiesTree(*self.properties)
        root = property_tree.root

        """
        Note 2: The root could be GenProp0002 or GenProp0003 depending on which one is stored first in the property 
        tree. Since we are using a dict not an OrderedDict inside of GenomePropertyTree we cannot guarantee that 
        GenProp0002 will always be returned as root. Thus we check if the root node is either property.
        """
        self.assertIn(root.id, ['GenProp0002', 'GenProp0003'])

    def test_create_json_graph_links(self):
        """Test that we can create parent child link json."""

        property_tree = GenomePropertiesTree(*self.properties)
        json_links = property_tree.create_graph_links_json(as_list=True)

        predicted_links = [{'parent': 'GenProp0002', 'child': 'GenProp0066'},
                           {'parent': 'GenProp0003', 'child': 'GenProp0066'},
                           {'parent': 'GenProp0066', 'child': 'GenProp0089'},
                           {'parent': 'GenProp0066', 'child': 'GenProp0092'}]

        self.assertCountEqual(json_links, predicted_links)

    def test_create_json_graph_nodes(self):
        """Test that we can create nodes json."""

        property_tree = GenomePropertiesTree(*self.properties)
        json_nodes = property_tree.create_graph_nodes_json(as_list=True)

        ids = {node['id'] for node in json_nodes}
        names = {node['name'] for node in json_nodes}
        types = {node['type'] for node in json_nodes}
        descriptions = {node['description'] for node in json_nodes}
        notes = {node['notes'] for node in json_nodes}

        self.assertCountEqual(ids, {'GenProp0002', 'GenProp0003', 'GenProp0066', 'GenProp0089', 'GenProp0092'})
        self.assertEqual(names, {'Coenzyme F420 utilization'})
        self.assertEqual(types, {'GUILD'})
        self.assertEqual(descriptions, {None})
        self.assertEqual(notes, {None})

    def test_create_nested_json(self):
        """Test that we can create nested json."""

        property_tree = GenomePropertiesTree(*self.properties)
        json = property_tree.create_nested_json(as_dict=True)

        root_id = json['id']

        """Root could be either GenProp0002 or GenProp0003. See Note 1 in test_find_root_node()."""
        self.assertIn(root_id, ['GenProp0002', 'GenProp0003'])

        tree_level_one_children = json['children']
        self.assertEqual(len(tree_level_one_children), 1)

        level_one_child = tree_level_one_children[0]
        self.assertEqual(level_one_child['id'], 'GenProp0066')

        tree_level_two_children = level_one_child['children']
        self.assertEqual(len(tree_level_two_children), 2)

        level_two_child_one = tree_level_two_children[0]
        level_two_child_two = tree_level_two_children[1]

        self.assertIn(level_two_child_one['id'], ['GenProp0089', 'GenProp0092'])
        self.assertIn(level_two_child_two['id'], ['GenProp0089', 'GenProp0092'])
        self.assertNotEqual(level_two_child_one['id'], level_two_child_two['id'])

        self.assertEqual(level_two_child_one['children'], [])
        self.assertEqual(level_two_child_two['children'], [])

    def test_json_string_creation(self):
        property_tree = GenomePropertiesTree(*self.properties)

        test_json = property_tree.to_json()

        expected_json_one = '''{"id": "GenProp0002", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null, "notes": null,
         "children": [{"id": "GenProp0066", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                       "notes": null, "children": [
                 {"id": "GenProp0089", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                  "notes": null, "children": []},
                 {"id": "GenProp0092", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                  "notes": null, "children": []}]}]}'''

        test_json_parsed = json.loads(test_json)
        expected_json_parsed_one = json.loads(expected_json_one)

        """Root could be either GenProp0002 or GenProp0003. See Note 1 in test_find_root_node()."""
        expected_json_parsed_two = deepcopy(expected_json_parsed_one)
        expected_json_parsed_two['id'] = 'GenProp0003'

        self.assertIn(test_json_parsed, [expected_json_parsed_one, expected_json_parsed_two])

    def test_json_string_creation_nodes_and_links(self):
        property_tree = GenomePropertiesTree(*self.properties)

        test_json = property_tree.to_json(nodes_and_links=True)

        expected_json = '''{
        "nodes": [{"id": "GenProp0002", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                    "notes": null},
                   {"id": "GenProp0003", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                    "notes": null},
                   {"id": "GenProp0066", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                    "notes": null},
                   {"id": "GenProp0089", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                    "notes": null},
                   {"id": "GenProp0092", "name": "Coenzyme F420 utilization", "type": "GUILD", "description": null,
                    "notes": null}],
        "links": [{"parent": "GenProp0002", "child": "GenProp0066"}, {"parent": "GenProp0003", "child": "GenProp0066"},
                   {"parent": "GenProp0066", "child": "GenProp0089"},
                   {"parent": "GenProp0066", "child": "GenProp0092"}]}'''

        test_json_parsed = json.loads(test_json)
        expected_json_parsed = json.loads(expected_json)

        test_json_nodes = test_json_parsed['nodes']
        expected_json_nodes = expected_json_parsed['nodes']

        test_json_links = test_json_parsed['links']
        expected_json_links = expected_json_parsed['links']

        self.assertCountEqual(test_json_nodes, expected_json_nodes)
        self.assertCountEqual(test_json_links, expected_json_links)

    def test_parse_genome_property_file(self):
        """Test if a physical genome properties file can be parsed."""
        genome_property_flat_file_path = './testing/test_constants/test_genome_properties.txt'

        with open(genome_property_flat_file_path) as genome_property_file:
            properties = parse_genome_property_file(genome_property_file)

        self.assertEqual(len(properties), 4)
