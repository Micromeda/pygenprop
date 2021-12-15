#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the functional_element module.
"""

import unittest

from pygenprop.database_file_parser import parse_functional_elements


class TestFunctionalElement(unittest.TestCase):
    """A unit testing class for testing the functional_element.py module. To be called by nosetests."""

    def test_parse_functional_element(self):
        """Test that functional element rows can be parsed."""
        functional_element = [
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins (EC 3.5.1.26)'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571; GO:0043579;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)

        self.assertEqual(len(parsed_functional_element), 1)
        first_functional_element = parsed_functional_element[0]
        self.assertEqual(first_functional_element.id, 'Aferr subtype specific proteins')
        self.assertEqual(first_functional_element.name, 'Crispy Proteins (EC 3.5.1.26)')
        self.assertEqual(first_functional_element.required, False)
        self.assertEqual(len(first_functional_element.evidence), 1)
        self.assertIn('3.5.1.26', first_functional_element.expasy_enzyme_numbers)

    def test_parse_missing_rows(self):
        """Test that functional elements can be parsed if they are missing non-essential rows."""
        functional_element = [
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Apern subtype specific proteins')
        ]

        parsed_functional_elements = parse_functional_elements(functional_element)

        second_functional_element = parsed_functional_elements[0]
        self.assertEqual(second_functional_element.required, False)
        self.assertEqual(second_functional_element.evidence, [])

    def test_parse_multiple_functional_elements(self):
        """Test that functional elements rows consisting of multiple functional elements can be parsed."""

        functional_elements = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;'),
            ('ID', 'Yolo subtype specific proteins'),
            ('RQ', '1'),
            ('EV', 'IPR017546; TIGR03115;'),
            ('TG', 'GO:0043571;')
        ]

        parsed_functional_elements = parse_functional_elements(functional_elements)
        functional_element_one = parsed_functional_elements[0]
        functional_element_two = parsed_functional_elements[1]

        self.assertEqual(len(parsed_functional_elements), 2)

        evidence_one = functional_element_one.evidence[0]
        evidence_two = functional_element_two.evidence[0]

        self.assertEqual(evidence_one.evidence_identifiers, ['IPR017545', 'TIGR03114'])
        self.assertEqual(evidence_two.evidence_identifiers, ['IPR017546', 'TIGR03115'])
