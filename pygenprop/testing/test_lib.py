#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing functions from the lib module.
"""

import unittest
from pygenprop.database_file_parser import parse_genome_property, create_marker_and_content, \
    collapse_genome_property_record


class TestLib(unittest.TestCase):
    """A unit test class for lib functions which clean and parse genome properties files."""

    def test_create_marker_and_content(self):
        """Test that we can split genome property rows by marker and content."""
        genome_property_row = 'RL  EMBO J. 2001;20:6561-6569.'
        marker, content = create_marker_and_content(genome_property_row)

        self.assertEqual(marker, 'RL')
        self.assertEqual(content, 'EMBO J. 2001;20:6561-6569.')

    def test_collapse_genome_property_record(self):
        """Test that we can clean up the overall genome property file."""
        property_rows = [
            ('AC', 'GenProp0002'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('AU', 'Haft DH'),
            ('TH', '0'),
            ('RN', '[1]'),
            ('RM', '11726492'),
            ('RT', 'Structures of F420H2:NADP+ oxidoreductase with and without its'),
            ('RT', 'janky structure!'),
            ('RT', 'I surprised that worked!'),
            ('RA', 'Warkentin E, Mamat B, Sordel-Klippert M, Wicke M, Thauer RK, Iwata M,'),
            ('RL', 'EMBO J. 2001;20:6561-6569.'),
            ('DC', 'Methane Biosynthesis'),
            ('DR', 'IUBMB; misc; methane;'),
            ('CC', 'Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin)'),
            ('CC', 'is a very important enzyme!'),
            ('**', 'Yo_Dog_its_Yolo'),
            ('**', 'a new film by the cool dudes!'),
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
            ('EV', 'IPR019920; TIGR03618; sufficient;'),
            ('SN', '10'),
            ('ID', 'F420-dependent oxidoreductase families'),
            ('RQ', '0'),
            ('EV', 'IPR019944; TIGR03554; sufficient;'),
            ('EV', 'IPR019946; TIGR03555; sufficient;'),
            ('EV', 'IPR019945; TIGR03557; sufficient;'),
            ('EV', 'IPR019951; TIGR03559; sufficient;'),
            ('EV', 'IPR019952; TIGR03560; sufficient;'),
            ('EV', 'IPR031017; TIGR04465; sufficient;'),
        ]

        clean_genome_property_record = collapse_genome_property_record(property_rows)

        first_genome_property = parse_genome_property(clean_genome_property_record)
        first_reference = first_genome_property.references[0]

        self.assertEqual(first_genome_property.description, 'Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin) '
                                                            'is a very important enzyme!')
        self.assertEqual(first_genome_property.private_notes, 'Yo_Dog_its_Yolo a new film by the cool dudes!')
        self.assertEqual(first_reference.title, 'Structures of F420H2:NADP+ oxidoreductase with and without its janky '
                                                'structure! I surprised that worked!')

        final_step = first_genome_property.steps[-1]
        functional_elements = final_step.functional_elements

        self.assertEqual(len(functional_elements), 1)
        self.assertEqual(len(functional_elements[0].evidence), 6)
