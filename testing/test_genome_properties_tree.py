#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the genome_property_tree module.
"""

import unittest

from modules.genome_property_tree import GenomePropertyTree
from modules.genome_properties_flat_file_parser import parse_genome_property


class TestGenomePropertyTree(unittest.TestCase):
    """A unit testing class for testing the genome_properties_tree.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """
        Test Properties Polytree Structure:

        GenProp0002 -->             --> GenProp0089
                        GenProp0066
        GenProp0003 -->             --> GenProp0092
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

        cls.properties = [property_one, property_two, property_three, property_four, property_five]

    def test_build_genome_property_connections(self):
        """Test that we can add child and parent genome properties."""

        property_one = self.properties[0]
        property_two = self.properties[1]
        property_three = self.properties[2]
        property_four = self.properties[3]
        property_five = self.properties[4]

        property_tree = GenomePropertyTree(*self.properties)

        self.assertEqual(property_tree[property_one.id].children[0], property_three)
        self.assertEqual(property_tree[property_two.id].children[0], property_three)
        self.assertCountEqual(property_tree[property_three.id].parents, [property_one, property_two])
        self.assertCountEqual(property_tree[property_three.id].children, [property_four, property_five])
        self.assertEqual(property_tree[property_four.id].parents[0], property_three)
        self.assertEqual(property_tree[property_five.id].parents[0], property_three)

    def test_find_leaf_nodes(self):
        """Test we can find the right leaf nodes."""

        property_tree = GenomePropertyTree(*self.properties)
        leaf_ids = [leaf.id for leaf in property_tree.leafs]

        self.assertCountEqual(leaf_ids, ['GenProp0089', 'GenProp0092'])

    def test_find_root_node(self):
        """Test that we can find the correct genome property root."""

        property_tree = GenomePropertyTree(*self.properties)
        root = property_tree.root

        # The structure of the property tree used above is not the common case.
        # Commonly there should be a single root node. The root could be GenProp0002
        # or GenProp0003 depending on which one is stored first in the property tree.
        # Since we are using a dict not an OrderedDict inside of GenomePropertyTree
        # we cannot guarantee that GenProp0002 will always be returned as root.
        # Thus we check if the root node is either property.
        self.assertIn(root.id, ['GenProp0002', 'GenProp0003'])
