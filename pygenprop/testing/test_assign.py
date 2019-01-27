#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the assign module.
"""

import unittest

from pygenprop.assign import calculate_property_assignment_from_required_steps, \
    calculate_property_assignment_from_all_steps, AssignmentCache, calculate_step_or_functional_element_assignment


class TestAssign(unittest.TestCase):
    """A unit testing class for testing the assign.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """Set up testing data for testing."""

        prebuilt_cache = AssignmentCache()

        prebuilt_cache.cache_property_assignment('GenProp0053', 'YES')
        prebuilt_cache.cache_property_assignment('GenProp0052', 'NO')
        prebuilt_cache.cache_property_assignment('GenProp0051', 'PARTIAL')

        prebuilt_cache.cache_step_assignment('GenProp0053', 1, 'YES')
        prebuilt_cache.cache_step_assignment('GenProp0053', 2, 'NO')
        prebuilt_cache.cache_step_assignment('GenProp0053', 3, 'YES')

        cls.cache = prebuilt_cache

    def test_assign_property_from_required_steps_all_yes(self):
        """Test that we can assign the genome property a correct result when all required steps are present."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'YES'])
        self.assertEqual(property_result, 'YES')

    def test_assign_property_from_required_steps_yes_above_threshold(self):
        """
        Test that we can assign the genome property a correct result when required steps present above the threshold.
        """

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'NO'], threshold=1)
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_property_from_required_steps_all_no(self):
        """Test that we can assign the genome property a correct result when no required steps are present."""

        property_result = calculate_property_assignment_from_required_steps(['NO', 'NO', 'NO'])
        self.assertEqual(property_result, 'NO')

    def test_assign_property_from_required_steps_yes_at_threshold(self):
        """
        Test that we can assign the genome property a correct result
        when required steps present is at the threshold.
        """

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'NO'], threshold=2)
        self.assertEqual(property_result, 'NO')

    def test_assign_property_from_required_steps_with_partial(self):
        """Test that we can assign the genome property a correct result when some steps are partial."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_property_from_required_steps_with_partial_at_threshold(self):
        """
        Test that we can assign the genome property a correct result
        when partial steps cause us to be at threshold.
        """

        property_result = calculate_property_assignment_from_required_steps(['YES', 'PARTIAL', 'PARTIAL'], threshold=1)
        self.assertEqual(property_result, 'NO')

    def test_assign_result_from_all_all_yes(self):
        """Test that we can assign the parent a correct result when all children are present."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'YES'])
        self.assertEqual(property_result, 'YES')

    def test_assign_result_from_all_all_no(self):
        """Test that we can assign the parent a correct result when all children are absent."""

        property_result = calculate_property_assignment_from_all_steps(['NO', 'NO', 'NO'])
        self.assertEqual(property_result, 'NO')

    def test_assign_result_from_all_has_no(self):
        """Test that we can assign the parent a correct result when some children are present."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'NO'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_result_from_all_has_partial(self):
        """Test that we can assign the parent a correct result when some children are partial."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_assign_result_from_all_has_partial_and_no(self):
        """Test that we can assign the parent a correct result when some children are partial and some absent."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'NO', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_step_assignment_all_yes(self):
        """Test that we can assign the step a correctly when all yes."""

        step_result = calculate_step_or_functional_element_assignment(['YES', 'YES', 'YES'])
        self.assertEqual(step_result, 'YES')

    def test_step_assignment_all_partial(self):
        """Test that we can assign the step a correctly when all partial."""

        step_result = calculate_step_or_functional_element_assignment(['PARTIAL', 'PARTIAL', 'PARTIAL'])
        self.assertEqual(step_result, 'YES')

    def test_step_assignment_all_no(self):
        """Test that we can assign the step a correctly when all no."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'NO', 'NO'])
        self.assertEqual(step_result, 'NO')

    def test_step_assignment_mixed(self):
        """Test that we can assign the step a correctly when mixed."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'YES', 'PARTIAL'])
        self.assertEqual(step_result, 'YES')

    def test_step_assignment_mixed_two(self):
        """Test that we can assign the step a correctly when mixed."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'NO', 'PARTIAL'])
        self.assertEqual(step_result, 'YES')

    def test_add_property_assignment(self):
        """Test that a property assignment can be cached."""

        test_cache = self.cache
        test_cache.cache_property_assignment('GenProp0065', 'YES')
        self.assertEqual(test_cache.get_property_assignment('GenProp0065'), 'YES')
        self.assertEqual(len(test_cache.property_assignments), 4)

    def test_get_property_assignment(self):
        """Test that a cached property assignment can be retrieved."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_property_assignment('GenProp0052'), 'NO')

    def test_get_property_assignment_no_cache(self):
        """Test that a non-cached property assignment can be retrieved."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_property_assignment('GenProp0100'), None)

    def test_add_step_assignment(self):
        """Test that a step assignment can be cached."""

        test_cache = self.cache
        test_cache.cache_step_assignment('GenProp0065', 1, 'YES')
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1,), 'YES')
        self.assertEqual(len(test_cache.step_assignments), 2)

    def test_get_step_assignment(self):
        """Test that a cached step assignment can be retrieved."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_step_assignment('GenProp0053', 3), 'YES')

    def test_get_step_assignment_no_cache(self):
        """Test that a non-cached step assignment can be retrieved."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_step_assignment('GenProp0100', 1), None)

    def test_cache_flush(self):
        """Test that the cache can be properly flushed."""

        test_cache = AssignmentCache()
        test_cache.cache_property_assignment('GenProp0067', 'YES')
        test_cache.cache_property_assignment('GenProp0092', 'NO')
        test_cache.cache_step_assignment('GenProp0067', 1, 'YES')
        test_cache.cache_step_assignment('GenProp0092', 1, 'NO')

        test_cache.flush_property_from_cache('GenProp0067')

        self.assertEqual(test_cache.get_property_assignment("GenProp0067"), None)
        self.assertEqual(test_cache.get_step_assignment("GenProp0067", 1), None)
        self.assertEqual(len(test_cache.property_assignments), 1)
        self.assertEqual(len(test_cache.step_assignments), 1)

    def test_get_identifiers(self):
        """Test that we can get the correct assignment identifiers."""

        test_cache = AssignmentCache()
        test_cache.cache_property_assignment('GenProp0067', 'YES')
        test_cache.cache_property_assignment('GenProp0092', 'NO')
        self.assertEqual(test_cache.genome_property_identifiers, ['GenProp0067', 'GenProp0092'])
