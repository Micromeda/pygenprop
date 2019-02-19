#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the results module.
"""

import unittest

from pygenprop.assign import AssignmentCache
from pygenprop.assignment_file_parser import parse_genome_property_longform_file
from pygenprop.database_file_parser import parse_genome_property_file
from pygenprop.results import GenomePropertiesResults, create_synchronized_assignment_cache


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

    def test_results(self):
        """Test parsing longform genome properties assignment files into assignment results."""

        first_property_assignment_cache = self.test_genome_property_results[0]

        results = GenomePropertiesResults(first_property_assignment_cache, genome_properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, ['C_chlorochromatii_CaD3'])
        self.assertEqual(results.get_property_result('GenProp0232'), ['PARTIAL'])
        self.assertEqual(results.get_property_result('GenProp0000'), ['NO'])
        self.assertEqual(results.get_step_result('GenProp0232', 1), ['YES'])
        self.assertEqual(results.get_step_result('GenProp0000', 2), ['NO'])

        self.assertEquals(len(results.tree), len(results.property_results.index))

    def test_multiple_results(self):
        """Test parsing multiple longform genome properties assignment files into assignment results."""

        results = GenomePropertiesResults(*self.test_genome_property_results, genome_properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, ['C_chlorochromatii_CaD3', 'C_luteolum_DSM_273'])
        self.assertEqual(results.get_property_result('GenProp0232'), ['PARTIAL', 'NO'])
        self.assertEqual(results.get_property_result('GenProp0000'), ['NO', 'NO'])
        self.assertEqual(results.get_step_result('GenProp0232', 1), ['YES', 'NO'])
        self.assertEqual(results.get_step_result('GenProp0000', 2), ['NO', 'NO'])

    def test_assignment_cache_synchronization(self):
        """Test that the assignment file can be properly synchronized."""

        test_cache = AssignmentCache()
        test_tree = self.test_tree

        test_cache.cache_property_assignment('GenProp0456', 'YES')
        test_cache.cache_property_assignment('GenProp0710', 'YES')

        sanitized_cache = create_synchronized_assignment_cache(test_cache, test_tree)

        self.assertEqual(len(sanitized_cache.property_assignments), 1)
        self.assertEqual(sanitized_cache.get_property_assignment('GenProp0710'), 'YES')
