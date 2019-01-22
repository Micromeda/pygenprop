#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the results module.
"""

import unittest

from pygenprop.assignment_parsers import parse_genome_property_longform_file
from pygenprop.flat_file_parser import parse_genome_property_file
from pygenprop.results import GenomePropertiesResults
from pygenprop.assign import calculate_property_assignment_from_required_steps, calculate_property_assignment_from_all_steps


class TestResults(unittest.TestCase):
    """A unit testing class for testing the results.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """Set up testing data for testing."""

        with open('pygenprop/testing/test_constants/C_chlorochromatii_CaD3.txt') as assignment_file_one:
            properties_one = parse_genome_property_longform_file(assignment_file_one)

        with open('pygenprop/testing/test_constants/C_luteolum_DSM_273.txt') as assignment_file_two:
            properties_two = parse_genome_property_longform_file(assignment_file_two)

        with open('pygenprop/testing/test_constants/test_genome_properties_two.txt') as test_genome_properties_file:
            genome_properties_tree = parse_genome_property_file(test_genome_properties_file)

        cls.test_genome_property_results = [properties_one, properties_two]
        cls.test_tree = genome_properties_tree

    def test_assign_property_result_from_required_steps_all_yes(self):
        """Test that we can assign the genome property a correct result when all required steps are present."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'YES'])
        self.assertEqual(property_result, 'YES')

    def test_assign_property_result_from_required_steps_yes_above_threshold(self):
        """
        Test that we can assign the genome property a correct result when required steps present above the threshold.
        """

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'NO'], threshold=1)
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_property_result_from_required_steps_all_no(self):
        """Test that we can assign the genome property a correct result when no required steps are present."""

        property_result = calculate_property_assignment_from_required_steps(['NO', 'NO', 'NO'])
        self.assertEqual(property_result, 'NO')

    def test_assign_property_result_from_required_steps_yes_at_threshold(self):
        """
        Test that we can assign the genome property a correct result
        when required steps present is at the threshold.
        """

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'NO'], threshold=2)
        self.assertEqual(property_result, 'NO')

    def test_assign_property_result_from_required_steps_with_partial(self):
        """Test that we can assign the genome property a correct result when some steps are partial."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_property_result_from_required_steps_with_partial_at_threshold(self):
        """
        Test that we can assign the genome property a correct result
        when partial steps cause us to be at threshold.
        """

        property_result = calculate_property_assignment_from_required_steps(['YES', 'PARTIAL', 'PARTIAL'], threshold=1)
        self.assertEqual(property_result, 'NO')

    def test_assign_result_from_child_assignment_results_all_yes(self):
        """Test that we can assign the parent a correct result when all children are present."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'YES'])
        self.assertEqual(property_result, 'YES')

    def test_assign_result_from_child_assignment_results_all_no(self):
        """Test that we can assign the parent a correct result when all children are absent."""

        property_result = calculate_property_assignment_from_all_steps(['NO', 'NO', 'NO'])
        self.assertEqual(property_result, 'NO')

    def test_assign_result_from_child_assignment_results_has_no(self):
        """Test that we can assign the parent a correct result when some children are present."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'NO'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_result_from_child_assignment_results_has_partial(self):
        """Test that we can assign the parent a correct result when some children are partial."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_result_from_child_assignment_results_has_partial_and_no(self):
        """Test that we can assign the parent a correct result when some children are partial and some absent."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'NO', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    @unittest.skip('Last assertion fails. Investigating.')
    def test_results(self):
        """Test parsing longform genome properties assignment files into assignment results."""

        first_results_dict = self.test_genome_property_results[0]

        results = GenomePropertiesResults(first_results_dict, genome_properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, ['C_chlorochromatii_CaD3'])
        self.assertEqual(results.get_property_result('GenProp0232'), ['PARTIAL'])
        self.assertEqual(results.get_step_result('GenProp0232', 1), ['YES'])
        self.assertEquals(len(results.tree), len(results.property_results.index))

    def test_multiple_results(self):
        """Test parsing multiple longform genome properties assignment files into assignment results."""

        results = GenomePropertiesResults(*self.test_genome_property_results, genome_properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, ['C_chlorochromatii_CaD3', 'C_luteolum_DSM_273'])
        self.assertEqual(results.get_property_result('GenProp0232'), ['PARTIAL', 'NO'])
        self.assertEqual(results.get_step_result('GenProp0232', 1), ['YES', 'NO'])
