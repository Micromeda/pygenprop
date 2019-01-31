#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the literature reference module.
"""

import unittest
from io import StringIO

from pygenprop.assignment_parsers import parse_genome_property_longform_file


class TestParseLongform(unittest.TestCase):
    """A unit testing class for testing the assignment_parsers.py module.
    To be called by nosetests."""

    def test_parse_longform(self):
        """Test parsing longform genome properties assignment files."""
        simulated_property_file = '''PROPERTY: GenProp0001
                    Chorismate biosynthesis via shikimate
                    .	STEP NUMBER: 1
                    .	STEP NAME: Phospho-2-dehydro-3-deoxyheptonate aldolase
                    .	.	required
                    .	STEP RESULT: yes
                    .	STEP NUMBER: 2
                    .	STEP NAME: 3-dehydroquinate synthase
                    .	.	required
                    .	STEP RESULT: yes
                    RESULT: YES
                    PROPERTY: GenProp0053
                    Type II secretion
                    .	STEP NUMBER: 1
                    .	STEP NAME: Type II secretion system protein C
                    .	STEP RESULT: yes
                    .	STEP NUMBER: 10
                    .	STEP NAME: Type II secretion system protein L
                    .	.	required
                    .	STEP RESULT: yes
                    .	STEP NUMBER: 12
                    .	STEP NAME: Type II secretion system protein N
                    .	STEP RESULT: no
                    RESULT: PARTIAL
                    PROPERTY: GenProp0046
                    IPP biosynthesis
                    .	STEP NUMBER: 1
                    .	STEP NAME: IPP biosynthesis
                    .	.	required
                    .	STEP RESULT: no
                    .	STEP NUMBER: 2
                    .	STEP NAME: IPP storage
                    .	.	required
                    .	STEP RESULT: yes
                    RESULT: NO'''

        rows = StringIO(simulated_property_file)
        rows.name = './testing/test1'

        assignment_cache = parse_genome_property_longform_file(rows)

        self.assertEqual(len(assignment_cache.property_assignments), 3)
        self.assertEqual(len(assignment_cache.step_assignments), 3)

        self.assertEqual(assignment_cache.get_property_assignment('GenProp0001'), 'YES')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0001', 1), 'YES')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0001', 2), 'YES')

        self.assertEqual(assignment_cache.get_property_assignment('GenProp0053'), 'PARTIAL')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0053', 1), 'YES')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0053', 10), 'YES')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0053', 12), 'NO')

        self.assertEqual(assignment_cache.get_property_assignment('GenProp0046'), 'NO')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0046', 1), 'NO')
        self.assertEqual(assignment_cache.get_step_assignment('GenProp0046', 2), 'YES')

        self.assertEqual(assignment_cache.sample_name, 'test1')
