#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the assign module.
"""

import unittest

from pygenprop.assign import calculate_property_assignment_from_required_steps, \
    calculate_property_assignment_from_all_steps, AssignmentCache, calculate_step_or_functional_element_assignment, \
    assign_evidence, assign_functional_element, assign_step, assign_genome_property
from pygenprop.database_file_parser import parse_evidences, parse_functional_elements, parse_steps, \
    parse_genome_property
from pygenprop.genome_property import GenomeProperty
from pygenprop.tree import GenomePropertiesTree


class TestAssign(unittest.TestCase):
    """Tests the assign.py module. To be called by nosetests."""

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

        """
        Test Properties Rooted DAG Structure:

                    --> GenProp0089
        GenProp0066
                    --> GenProp0092
        """

        property_rows_one = [
            ('AC', 'GenProp0066'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0089;'),
            ('--', ''),
            ('SN', '2'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0092;')
        ]

        property_rows_two = [
            ('AC', 'GenProp0089'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03564; sufficient;')
        ]

        property_rows_three = [
            ('AC', 'GenProp0092'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03565; sufficient;')
        ]

        property_one = parse_genome_property(property_rows_one)
        property_two = parse_genome_property(property_rows_two)
        property_three = parse_genome_property(property_rows_three)

        raw_properties = [property_one, property_two, property_three]

        cls.tree = GenomePropertiesTree(*raw_properties)

    def test_calculate_assignment_from_required_steps_all_yes(self):
        """Test that we can calculate the property assignment correctly when all required steps are present."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'YES'])
        self.assertEqual(property_result, 'YES')

    def test_calculate_assignment_from_required_steps_yes_above_threshold(self):
        """Test that we can calculate the property assignment correctly when required steps above the threshold."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'NO'], threshold=1)
        self.assertEqual(property_result, 'PARTIAL')

    def test_calculate_assignment_from_required_steps_all_no(self):
        """Test that we can calculate the property assignment correctly when no required steps are present."""

        property_result = calculate_property_assignment_from_required_steps(['NO', 'NO', 'NO'])
        self.assertEqual(property_result, 'NO')

    def test_calculate_assignment_from_required_steps_yes_at_threshold(self):
        """Test that we can calculate the property assignment correctly when required steps at the threshold."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'NO'], threshold=2)
        self.assertEqual(property_result, 'NO')

    def test_calculate_assignment_from_required_steps_with_partial(self):
        """Test that we can calculate the property assignment correctly when some steps are partial."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'YES', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_calculate_assignment_from_required_steps_with_partial_at_threshold(self):
        """Test that we can calculate the property assignment correctly when partial required steps at threshold."""

        property_result = calculate_property_assignment_from_required_steps(['YES', 'PARTIAL', 'PARTIAL'], threshold=1)
        self.assertEqual(property_result, 'NO')

    def test_calculate_assignment_from_all_all_yes(self):
        """Test that we can calculate the property assignment correctly when all steps are present."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'YES'])
        self.assertEqual(property_result, 'YES')

    def test_calculate_assignment_from_all_all_no(self):
        """Test that we can calculate the property assignment correctly when all steps are absent."""

        property_result = calculate_property_assignment_from_all_steps(['NO', 'NO', 'NO'])
        self.assertEqual(property_result, 'NO')

    def test_calculate_assignment_from_all_has_no(self):
        """Test that we can calculate the property assignment correctly when some steps are present."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'NO'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_calculate_assignment_from_all_has_partial(self):
        """Test that we can calculate the property assignment correctly when some steps are partial."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'YES', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_calculate_assignment_from_all_has_partial_and_no(self):
        """Test that we can calculate the property assignment correctly when some steps are partial and some absent."""

        property_result = calculate_property_assignment_from_all_steps(['YES', 'NO', 'PARTIAL'])
        self.assertEqual(property_result, 'PARTIAL')

    def test_calculate_step_assignment_all_yes(self):
        """Test that we can calculate the step assignment correctly when all yes."""

        step_result = calculate_step_or_functional_element_assignment(['YES', 'YES', 'YES'])
        self.assertEqual(step_result, 'YES')

    def test_calculate_step_assignment_all_partial(self):
        """Test that we can calculate the step assignment correctly all partial."""

        step_result = calculate_step_or_functional_element_assignment(['PARTIAL', 'PARTIAL', 'PARTIAL'])
        self.assertEqual(step_result, 'YES')

    def test_calculate_step_assignment_all_no(self):
        """Test that we can calculate the step assignment correctly all no."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'NO', 'NO'])
        self.assertEqual(step_result, 'NO')

    def test_calculate_step_assignment_mixed_yes_no_partial(self):
        """Test that we can calculate the step assignment correctly mixed yes, no, and partial."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'YES', 'PARTIAL'])
        self.assertEqual(step_result, 'NO')

    def test_calculate_step_assignment_mixed_no_partial(self):
        """Test that we can calculate the step assignment correctly mixed no and partial."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'PARTIAL', 'PARTIAL'])
        self.assertEqual(step_result, 'NO')

    def test_calculate_step_assignment_mixed_yes_partial(self):
        """Test that we can calculate the step assignment correctly mixed."""

        step_result = calculate_step_or_functional_element_assignment(['YES', 'PARTIAL', 'PARTIAL'])
        self.assertEqual(step_result, 'YES')

    def test_calculate_functional_element_assignment_sufficient_mixed_no_partial(self):
        """Test that we can calculate the element assignment correctly with mixed (NO,PARTIAL) sufficient steps."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['NO', 'PARTIAL', 'PARTIAL'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'YES')

    def test_calculate_functional_element_assignment_sufficient_multiple_no(self):
        """Test that we can calculate the element assignment correctly with sufficient steps (multiple NO)."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['NO', 'NO', 'NO'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'NO')

    def test_calculate_functional_element_assignment_sufficient_single_no(self):
        """Test that we can calculate the element assignment correctly with sufficient steps (single NO)."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['NO'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'NO')

    def test_calculate_functional_element_assignment_sufficient_single_yes(self):
        """Test that we can calculate the element assignment correctly with sufficient steps (single YES)."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['YES'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'YES')

    def test_calculate_functional_element_assignment_sufficient_single_partial(self):
        """Test that we can calculate the element assignment correctly with sufficient steps (single PARTIAL)."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['PARTIAL'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'YES')

    def test_add_property_assignment_to_cache(self):
        """Test that a property assignment can be cached."""

        test_cache = self.cache
        test_cache.cache_property_assignment('GenProp0065', 'YES')
        self.assertEqual(test_cache.get_property_assignment('GenProp0065'), 'YES')
        self.assertEqual(len(test_cache.property_assignments), 4)

    def test_get_property_assignment_from_cache(self):
        """Test that a cached property assignment can be retrieved from the cache."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_property_assignment('GenProp0052'), 'NO')

    def test_get_property_assignment_when_property_not_in_cache(self):
        """Test if a non-cached property assignment can be retrieved."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_property_assignment('GenProp0100'), None)

    def test_add_step_assignment_to_cache(self):
        """Test that a step assignment can be cached."""

        test_cache = self.cache
        test_cache.cache_step_assignment('GenProp0065', 1, 'YES')
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1), 'YES')
        self.assertEqual(len(test_cache.step_assignments), 2)

    def test_get_step_assignment(self):
        """Test that a cached step assignment can be retrieved from the cache."""

        test_cache = self.cache
        self.assertEqual(test_cache.get_step_assignment('GenProp0053', 3), 'YES')

    def test_get_step_assignment_when_step_not_in_cache(self):
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
        """Test that we can get the correct assignment identifiers from the cache."""

        test_cache = AssignmentCache()
        test_cache.cache_property_assignment('GenProp0067', 'YES')
        test_cache.cache_property_assignment('GenProp0092', 'NO')
        identifiers = test_cache.genome_property_identifiers
        identifiers.sort()

        self.assertEqual(identifiers, ['GenProp0067', 'GenProp0092'])

    def test_assign_evidence_from_no_interpro_identifiers(self):
        """Test we can assign evidence when no InterPro identifiers are in the assignment cache."""

        test_cache = AssignmentCache()

        evidence = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;')
        ]

        evidence = parse_evidences(evidence)[0]

        assignment = assign_evidence(test_cache, evidence)

        self.assertEqual(assignment, 'NO')

    def test_assign_evidence_from_interpro_identifiers(self):
        """Test that we can assign evidence based on InterPro identifiers in the assignment cache."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03114', 'TIGR03115', 'TIGR03113'])

        evidence = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;')
        ]

        evidence = parse_evidences(evidence)[0]

        assignment = assign_evidence(test_cache, evidence)

        self.assertEqual(assignment, 'YES')

    def test_assign_evidence_when_missing_interpro_identifiers(self):
        """Test assign evidence based on InterPro identifiers that are missing from the assignment cache."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03192', 'TIGR03193', 'TIGR03194'])

        evidence = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;')
        ]

        evidence = parse_evidences(evidence)[0]

        assignment = assign_evidence(test_cache, evidence)

        self.assertEqual(assignment, 'NO')

    def test_assign_functional_element_all_identifiers(self):
        """Test assignment of a functional element when all evidence markers are present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03114', 'TIGR03117', 'TIGR03120'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),  # Yes
            ('EV', 'IPR017547; TIGR03117;'),  # Yes
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # Yes
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'YES')

    def test_assign_functional_element_one_non_sufficient_identifier(self):
        """Test assignment of a functional element when there is one non-sufficient identifier present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03115', 'TIGR03118', 'TIGR03120'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),  # NO
            ('EV', 'IPR017547; TIGR03117; sufficient;'),  # NO
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # YES
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'NO')

    def test_assign_functional_element_when_two_sufficient_identifiers(self):
        """Test assignment of a functional element when there are two sufficient identifiers and one is present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03115', 'TIGR03117', 'TIGR03121'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),  # NO
            ('EV', 'IPR017547; TIGR03117; sufficient;'),  # YES
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # NO
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'YES')

    def test_assign_functional_element_when_two_sufficient_identifiers_both_not_present(self):
        """Test assignment of a functional element when two sufficient identifiers and both are not present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03115', 'TIGR03118', 'TIGR03121'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),  # NO
            ('EV', 'IPR017547; TIGR03117; sufficient;'),  # NO
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # NO
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'NO')

    def test_assign_functional_element_no_sufficient_one_present(self):
        """Test assignment of a functional element when no sufficient identifiers and one is present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03115', 'TIGR03117', 'TIGR03120'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114'),  # NO
            ('EV', 'IPR017547; TIGR03117'),  # NO
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # YES
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'NO')

    def test_assign_functional_element_no_sufficient_all_present(self):
        """Test assignment of a functional element when no sufficient identifiers and all present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03114', 'TIGR03117', 'TIGR03120'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114;'),  # YES
            ('EV', 'IPR017547; TIGR03117;'),  # YES
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # YES
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'YES')

    def test_assign_functional_element_none_sufficient_all_not_present(self):
        """Test assignment of a functional element when no sufficient identifiers and none present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03115', 'TIGR03118', 'TIGR03121'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114;'),  # NO
            ('EV', 'IPR017547; TIGR03117;'),  # NO
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # NO
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'NO')

    def test_assign_step_multiple_functional_elements_one_present(self):
        """Test assignment of multiple elements and one present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03114'])
        parent_genome_property = GenomeProperty(accession_id='GenProp0065', name='YOLO', property_type="TEMP")

        step = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03114;'),  # Yes
            ('TG', 'GO:0043571;'),
            ('ID', 'Yolo subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03115;'),  # NO
            ('TG', 'GO:0043571;')
        ]

        parsed_step = parse_steps(step)[0]
        parsed_step.parent = parent_genome_property

        step_assignment = assign_step(test_cache, parsed_step)

        self.assertEqual(step_assignment, 'YES')
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1), 'YES')

    def test_assign_step_multiple_functional_elements_all_none_present(self):
        """Test assignment of multiple elements when all are not present."""

        test_cache = AssignmentCache()
        parent_genome_property = GenomeProperty(accession_id='GenProp0065', name='YOLO', property_type="TEMP")

        step = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03114;'),  # NO
            ('TG', 'GO:0043571;'),
            ('ID', 'Yolo subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03115;'),  # NO
            ('TG', 'GO:0043571;')
        ]

        parsed_step = parse_steps(step)[0]
        parsed_step.parent = parent_genome_property

        step_assignment = assign_step(test_cache, parsed_step)

        self.assertEqual(step_assignment, 'NO')
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1), 'NO')

    def test_genome_property_assignment_non_required_all_identifiers_present(self):
        """Test assignment of a genome property when all marker are present but none are required."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03564', 'TIGR03565'])
        test_property = self.tree.root

        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'YES')

    def test_genome_property_assignment_non_required_one_present(self):
        """Test assignment of a genome property when one marker is present but none are required."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03565'])
        test_property = self.tree.root

        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'PARTIAL')

    def test_genome_property_assignment_non_required_none_present(self):
        """Test assignment of genome properties when no markers are present and none are required."""

        test_cache = AssignmentCache()
        test_property = self.tree.root

        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'NO')

    def test_genome_property_assignment_one_required_one_present(self):
        """Test assignment of genome properties when one marker is required and one is present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03564'])

        property_rows = [
            ('AC', 'GenProp0089'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03564; sufficient;'),  # YES
            ('--', ''),
            ('SN', '2'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03567; sufficient;'),  # NO
            ('--', ''),
            ('SN', '3'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03568; sufficient;')  # NO
        ]

        test_property = parse_genome_property(property_rows)

        test_property.threshold = 0
        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'YES')

    def test_genome_property_assignment_two_required_two_present(self):
        """Test assignment of genome properties when two markers are required and two are present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03564', 'TIGR03567'])

        property_rows = [
            ('AC', 'GenProp0089'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03564; sufficient;'),  # YES
            ('--', ''),
            ('SN', '2'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03567; sufficient;'),  # YES
            ('--', ''),
            ('SN', '3'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03568; sufficient;')  # NO
        ]

        test_property = parse_genome_property(property_rows)

        test_property.threshold = 0
        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'PARTIAL')

    def test_genome_property_assignment_two_required_three_absent(self):
        """Test assignment of genome properties when two markers are required and none are present."""

        test_cache = AssignmentCache()

        property_rows = [
            ('AC', 'GenProp0089'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03564; sufficient;'),  # NO
            ('--', ''),
            ('SN', '2'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03567; sufficient;'),  # NO
            ('--', ''),
            ('SN', '3'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03568; sufficient;')  # NO
        ]

        test_property = parse_genome_property(property_rows)

        test_property.threshold = 0
        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'NO')

    def test_genome_property_assignment_two_required_all_present(self):
        """Test assignment of genome properties when two markers are required and all are present."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03564', 'TIGR03567', 'TIGR03568'])

        property_rows = [
            ('AC', 'GenProp0089'),
            ('DE', 'Coenzyme F420 utilization'),
            ('TP', 'GUILD'),
            ('--', ''),
            ('SN', '1'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03564; sufficient;'),  # YES
            ('--', ''),
            ('SN', '2'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '1'),
            ('EV', 'IPR019910; TIGR03567; sufficient;'),  # YES
            ('--', ''),
            ('SN', '3'),
            ('ID', 'LLM-family F420-associated subfamilies'),
            ('RQ', '0'),
            ('EV', 'IPR019910; TIGR03568; sufficient;')  # YES
        ]

        test_property = parse_genome_property(property_rows)

        test_property.threshold = 0
        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'YES')
