#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the results module.
"""

import unittest

from pygenprop.assign import AssignmentCache
from pygenprop.assignment_file_parser import parse_genome_property_longform_file
from pygenprop.database_file_parser import parse_genome_properties_flat_file
from pygenprop.results import GenomePropertiesResults


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
            genome_properties_tree = parse_genome_properties_flat_file(test_genome_properties_file)

        cls.test_genome_property_results = [properties_one, properties_two]
        cls.test_tree = genome_properties_tree

    def test_results(self):
        """Test parsing longform genome properties assignment files into assignment results."""

        first_property_assignment_cache = self.test_genome_property_results[0]

        results = GenomePropertiesResults(first_property_assignment_cache, properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, ['C_chlorochromatii_CaD3'])
        self.assertEqual(results.get_property_result('GenProp0232'), ['PARTIAL'])
        self.assertEqual(results.get_property_result('GenProp0000'), ['NO'])
        self.assertEqual(results.get_step_result('GenProp0232', 1), ['YES'])
        self.assertEqual(results.get_step_result('GenProp0000', 2), ['NO'])

        self.assertEquals(len(results.tree), len(results.property_results.index))

    def test_multiple_results(self):
        """Test parsing multiple longform genome properties assignment files into assignment results."""

        results = GenomePropertiesResults(*self.test_genome_property_results, properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, ['C_chlorochromatii_CaD3', 'C_luteolum_DSM_273'])
        self.assertEqual(results.get_property_result('GenProp0232'), ['PARTIAL', 'NO'])
        self.assertEqual(results.get_property_result('GenProp0000'), ['NO', 'NO'])
        self.assertEqual(results.get_step_result('GenProp0232', 1), ['YES', 'NO'])
        self.assertEqual(results.get_step_result('GenProp0000', 2), ['NO', 'NO'])

    def test_simplified_results(self):
        """Test parsing multiple longform genome properties assignment files into assignment results."""

        results = GenomePropertiesResults(*self.test_genome_property_results, properties_tree=self.test_tree)

        self.assertEqual(len(results.differing_property_results), 3)
        self.assertEqual(len(results.supported_property_results), 4)
        self.assertEqual(len(results.differing_step_results), 16)
        self.assertEqual(len(results.supported_step_results), 19)

    def test_get_results(self):
        """Test that we can get a results dataframe."""

        results = GenomePropertiesResults(*self.test_genome_property_results, properties_tree=self.test_tree)

        filtered_results = results.get_results('GenProp0877', 'GenProp0902')
        results_list = filtered_results['C_chlorochromatii_CaD3'].tolist()

        self.assertEqual(len(filtered_results), 2)
        self.assertEqual(results_list[0], 'YES')
        self.assertEqual(results_list[1], 'NO')

        filtered_step_results = results.get_results('GenProp0877', 'GenProp0902', steps=True)
        step_results_list = filtered_step_results['C_chlorochromatii_CaD3'].tolist()

        self.assertEqual(len(filtered_step_results), 6)
        self.assertEqual(step_results_list[1], 'YES')
        self.assertEqual(step_results_list[5], 'NO')

        filtered_results_names = results.get_results('GenProp0877', 'GenProp0902', names=True)
        results_names = filtered_results_names.index.levels[1].tolist()

        self.assertEqual(len(filtered_results_names.index.levels), 2)
        self.assertEqual(results_names[0], 'Flagellar motor stator complex')
        self.assertEqual(results_names[1], 'Quinohemoprotein amine dehydrogenase')

        filtered_step_results_names = results.get_results('GenProp0877', 'GenProp0902', steps=True, names=True)
        step_results_names = filtered_step_results_names.index.levels[3].tolist()

        self.assertEqual(len(filtered_step_results_names.index.levels), 4)
        self.assertEqual(step_results_names[1], 'Flagellar motor stator protein MotB')
        self.assertEqual(step_results_names[5], 'Quinohemoprotein amine dehydrogenase, gamma subunit')

    def test_results_summary(self):
        results = GenomePropertiesResults(*self.test_genome_property_results, properties_tree=self.test_tree)

        filtered_summary = results.get_results_summary('GenProp0877', 'GenProp0902')
        summary_list = filtered_summary['C_chlorochromatii_CaD3'].tolist()

        self.assertEqual(len(filtered_summary), 2)
        self.assertEqual(summary_list[0], 1)  # NO
        self.assertEqual(summary_list[1], 1)  # YES

        filtered_step_summary = results.get_results_summary('GenProp0877', 'GenProp0902', steps=True)
        step_summary_list = filtered_step_summary['C_chlorochromatii_CaD3'].tolist()

        self.assertEqual(len(filtered_step_summary), 2)
        self.assertEqual(step_summary_list[0], 4)  # NO
        self.assertEqual(step_summary_list[1], 2)  # YES

        filtered_normalized_step_summary = results.get_results_summary('GenProp0877', 'GenProp0902',
                                                                       steps=True, normalize=True)
        normalized_step_summary_list = filtered_normalized_step_summary['C_chlorochromatii_CaD3'].tolist()

        self.assertEqual(len(filtered_normalized_step_summary), 2)

        self.assertEqual(normalized_step_summary_list[0], 2 / 3 * 100)  # NO
        self.assertEqual(normalized_step_summary_list[1], 1 / 3 * 100)  # YES

        filtered_normalized_summary = results.get_results_summary('GenProp0877', 'GenProp0902', normalize=True)
        normalized_summary_list = filtered_normalized_summary['C_chlorochromatii_CaD3'].tolist()

        self.assertEqual(len(filtered_normalized_summary), 2)
        self.assertEqual(normalized_summary_list[0], 50.0)  # NO
        self.assertEqual(normalized_summary_list[1], 50.0)  # YES

    def test_assignment_cache_synchronization(self):
        """Test that the assignment file can be properly synchronized."""

        test_cache = AssignmentCache()
        test_tree = self.test_tree

        test_cache.cache_property_assignment('GenProp0456', 'YES')
        test_cache.cache_property_assignment('GenProp0710', 'YES')

        test_cache.synchronize_with_tree(test_tree)

        self.assertEqual(len(test_cache.property_assignments), 1)
        self.assertEqual(test_cache.get_property_assignment('GenProp0710'), 'YES')
