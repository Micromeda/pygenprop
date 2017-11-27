#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the genome property module.
"""

import unittest
from modules.genome_property import parse_genome_property, build_genome_property_connections


class TestGenomeProperty(unittest.TestCase):
    """A unit testing class for testing the genome_properties.py module. To be called by nosetests."""

    def test_parse_genome_property(self):
        """Test that we can parse genome property rows."""

        property_rows = [
            ('AC', 'GenProp0002'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('AU', 'Haft DH'),
            ('TH', '0'),
            ('RN', '[1]'),
            ('RM', '11726492'),
            ('RT', 'Structures of F420H2:NADP+ oxidoreductase with and without its'),
            ('RA', 'Warkentin E, Mamat B, Sordel-Klippert M, Wicke M, Thauer RK, Iwata M,'),
            ('RL', 'EMBO J. 2001;20:6561-6569.'),
            ('DC', 'Methane Biosynthesis'),
            ('DR', 'IUBMB; misc; methane;'),
            ('CC', 'Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin)'),
            ('**', 'Yo_Dog_its_Yolo'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03564; sufficient;'),
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Methylene-5,6,7,8-tetrahydromethanopterin dehydrogenase'),
            ('RQ', '0'),
            ('EV', 'IPR002844; PF01993; sufficient;'),
            ('--', ''),
            ('SN', '3'),
            ('ID', 'PPOX-class probable F420-dependent enzyme'),
            ('RQ', '0'),
            ('EV', 'IPR019920; TIGR03618; sufficient;')
        ]

        new_property = parse_genome_property(property_rows)

        self.assertEqual(new_property.id, 'GenProp0002')
        self.assertEqual(new_property.name, 'Coenzyme F420 utilization')
        self.assertEqual(new_property.type, 'GUILD')
        self.assertEqual(new_property.threshold, 0)
        self.assertEqual(new_property.parents, [])
        self.assertEqual(new_property.description, 'Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin)')
        self.assertEqual(new_property.private_notes, 'Yo_Dog_its_Yolo')
        self.assertEqual(new_property.public, False)
        self.assertEqual(len(new_property.databases), 1)
        self.assertEqual(len(new_property.references), 1)
        self.assertEqual(len(new_property.steps), 3)

    def test_child_genome_property_identifiers(self):
        """Test that we can get child genome property identifiers."""

        property_rows = [
            ('AC', 'GenProp0002'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03564; sufficient;'),
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0066; GenProp0067;'),
            ('--', ''),
            ('SN', '3'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0068; GenProp0069;')
        ]

        new_property = parse_genome_property(property_rows)
        child_genome_property_identifiers = new_property.child_genome_property_identifiers

        self.assertEqual(child_genome_property_identifiers, ['GenProp0066', 'GenProp0067',
                                                             'GenProp0068', 'GenProp0069'])

    def test_add_child_connections(self):
        """Test that we can add child and parent genome properties."""

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
            ('AC', 'GenProp0066'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0066;')
        ]

        property_one = parse_genome_property(property_rows_one)
        property_two = parse_genome_property(property_rows_two)

        genome_properties_dict = {property_one.id: property_one, property_two.id: property_two}

        property_one.add_child_connections(genome_properties_dict)

        self.assertEqual(property_one.children[0], property_two)
        self.assertEqual(property_two.parents[0], property_one)

    def test_build_genome_property_connections(self):
        """Test that we can add child and parent genome properties."""

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

        genome_properties_dict = {property_one.id: property_one,
                                  property_two.id: property_two,
                                  property_three.id: property_three,
                                  property_four.id: property_four,
                                  property_five.id: property_five}

        build_genome_property_connections(genome_properties_dict)

        self.assertEqual(property_one.children[0], property_three)
        self.assertEqual(property_two.children[0], property_three)
        self.assertEqual(property_three.parents, [property_one, property_two])
        self.assertEqual(property_three.children, [property_four, property_five])
        self.assertEqual(property_four.parents[0], property_three)
        self.assertEqual(property_five.parents[0], property_three)
