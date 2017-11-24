#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the genome property module.
"""

import unittest
from modules.genome_property import parse_genome_property


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
        self.assertEqual(new_property.parent, None)
        self.assertEqual(new_property.description, 'Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin)')
        self.assertEqual(new_property.private_notes, 'Yo_Dog_its_Yolo')
        self.assertEqual(new_property.public, False)
        self.assertEqual(len(new_property.databases), 1)
        self.assertEqual(len(new_property.references), 1)
        self.assertEqual(len(new_property.steps), 3)
