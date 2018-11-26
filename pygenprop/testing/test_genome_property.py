#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the genome property module.
"""

import unittest
from pygenprop.flat_file_parser import parse_genome_property


class TestGenomeProperty(unittest.TestCase):
    """A unit testing class for testing the genome_properties.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """Setup property rows for later parsing."""

        property_rows_one = [
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

        property_rows_two = [
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
            ('ID', 'Selfish genetic elements One'),
            ('RQ', '1'),
            ('EV', 'GenProp0066; GenProp0067;'),
            ('--', ''),
            ('SN', '3'),
            ('ID', 'Selfish genetic elements two'),
            ('RQ', '0'),
            ('EV', 'GenProp0068; GenProp0069;')
        ]

        cls.property_rows = [property_rows_one, property_rows_two]

    def test_parse_genome_property(self):
        """Test that we can parse genome property rows."""

        new_property = parse_genome_property(self.property_rows[0])

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

        new_property = parse_genome_property(self.property_rows[1])
        child_genome_property_identifiers = new_property.child_genome_property_identifiers

        self.assertEqual(child_genome_property_identifiers, ['GenProp0066', 'GenProp0067',
                                                             'GenProp0068', 'GenProp0069'])

    def test_json_creation(self):
        """Test that json can be created properly."""

        new_property = parse_genome_property(self.property_rows[0])

        json_dict = new_property.to_json(as_dict=True)

        self.assertEqual(json_dict['id'], 'GenProp0002')
        self.assertEqual(json_dict['name'], 'Coenzyme F420 utilization')
        self.assertEqual(json_dict['type'], 'GUILD')
        self.assertEqual(json_dict['description'], 'Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin)')
        self.assertEqual(json_dict['notes'], 'Yo_Dog_its_Yolo')

    def test_required_steps(self):
        """Test that a genome property can return its required steps."""

        new_property = parse_genome_property(self.property_rows[1])

        required_steps = new_property.required_steps

        self.assertEquals(len(required_steps), 1)
        self.assertEquals(required_steps[0].name, 'Selfish genetic elements One')
