#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the database reference module.
"""

import unittest
from modules.database_reference import parse_database_references


class TestDatabaseReference(unittest.TestCase):
    """A unit testing class for testing the database_reference.py module. To be called by nosetests."""

    def test_parse_database_references(self):
        """Test that database reference rows can be parsed."""
        database_reference = [
            ('RL', 'EMBO J. 2001;20:6561-6569.'),
            ('DC', 'Methane Biosynthesis'),
            ('DR', 'IUBMB; misc; methane;'),
            ('CC', ' Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin) is found in')
        ]
        reference = parse_database_references(database_reference)

        self.assertEqual(len(reference), 1)
        first_reference = reference[0]
        self.assertEqual(first_reference.database_name, 'IUBMB')
        self.assertEqual(first_reference.record_title, 'Methane Biosynthesis')
        self.assertEqual(first_reference.record_ids, ['misc', 'methane'])

    def test_parse_multiple_database_references(self):
        """Test that database reference rows consisting of multiple references can be parsed."""
        database_references = [
            ('RL', 'EMBO J. 2001;20:6561-6569.'),
            ('DC', 'Methane Biosynthesis'),
            ('DR', 'IUBMB; misc; methane;'),
            ('DC', 'Coenzyme F420 hydrogenase'),
            ('DR', 'IUBMB; single; 112981;'),
            ('CC', ' Coenzyme F420 (a 7,8-didemethyl-8-hydroxy 5-deazaflavin) is found in')
        ]

        references = parse_database_references(database_references)

        self.assertEqual(len(references), 2)



