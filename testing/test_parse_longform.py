#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the literature reference module.
"""

import unittest
from io import StringIO

from modules.assignment_file_parser import parse_genome_property_longform_file


class TestParseLongform(unittest.TestCase):
    """A unit testing class for testing the assignment_file_parser.py module.
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
                    RESULT: NO
                '''

        rows = StringIO(simulated_property_file)
        rows.name = './testing/test1'

        properties = parse_genome_property_longform_file(rows)

        self.assertEqual(len(properties.keys()), 4)
        self.assertEqual(properties['GenProp0001']['supported_steps'], [1, 2])
        self.assertEqual(properties['GenProp0001']['result'], 'YES')
        self.assertEqual(properties['GenProp0053']['supported_steps'], [1, 10])
        self.assertEqual(properties['GenProp0053']['result'], 'PARTIAL')
        self.assertEqual(properties['GenProp0046']['result'], 'NO')
        self.assertEqual(properties['GenProp0046']['supported_steps'], [2])
        self.assertEqual(properties['name'], 'test1')
