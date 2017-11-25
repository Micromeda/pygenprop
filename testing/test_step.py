#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the step module.
"""

import unittest

from modules.step import parse_steps


class TestStep(unittest.TestCase):
    """A unit testing class for testing the step.py module. To be called by nosetests."""

    def test_parse_step(self):
        """Test that step rows can be parsed."""
        step = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;GO:0043579;')
        ]

        parsed_step = parse_steps(step)

        self.assertEqual(len(parsed_step), 1)
        first_step = parsed_step[0]
        self.assertEqual(first_step.number, 1)
        self.assertEqual(first_step.required, False)

    def test_parse_step_required(self):
        """Test that the step rows can be properly parsed if the step is required."""
        step = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '1'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571; GO:0043579;')
        ]

        parsed_step = parse_steps(step)
        first_step = parsed_step[0]
        self.assertEqual(first_step.required, True)

    def test_parse_missing_rows(self):
        """Test that steps can be parsed if they are missing non essential rows."""
        step = [
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Apern subtype specific proteins')
        ]

        parsed_steps = parse_steps(step)

        second_step = parsed_steps[0]
        self.assertEqual(second_step.required, False)
        self.assertEqual(len(second_step.functional_elements), 1)

    def test_parse_multiple_steps(self):
        """Test that steps rows consisting of multiple references can be parsed."""

        steps = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;'),
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Yolo subtype specific proteins'),
            ('RQ', '1'),
            ('EV', 'IPR017545; TIGR03114;'),
            ('TG', 'GO:0043571;')
        ]

        parsed_steps = parse_steps(steps)
        step_one = parsed_steps[0]
        step_two = parsed_steps[1]

        self.assertEqual(len(parsed_steps), 2)
        self.assertEqual(step_one.number, 1)
        self.assertEqual(step_two.number, 2)
        self.assertEqual(len(step_two.functional_elements), 1)
        self.assertEqual(len(step_two.functional_elements[0].evidence), 1)
