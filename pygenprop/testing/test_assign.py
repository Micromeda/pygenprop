#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the assign module.
"""

import unittest

from pygenprop.assign import calculate_property_assignment_from_required_steps, \
    calculate_property_assignment_from_all_steps, AssignmentCache, calculate_step_or_functional_element_assignment, \
    assign_evidence, assign_functional_element, assign_step, assign_genome_property
from pygenprop.database_file_parser import parse_evidences, parse_functional_elements, parse_steps, parse_genome_property
from pygenprop.genome_property import GenomeProperty
from pygenprop.tree import GenomePropertiesTree


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

        """
        Test Properties Polytree Structure:

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
        self.assertEqual(step_result, 'NO')

    def test_step_assignment_mixed_two(self):
        """Test that we can assign the step a correctly when mixed."""

        step_result = calculate_step_or_functional_element_assignment(['NO', 'PARTIAL', 'PARTIAL'])
        self.assertEqual(step_result, 'NO')

    def test_step_assignment_mixed_three(self):
        """Test that we can assign the step a correctly when mixed."""

        step_result = calculate_step_or_functional_element_assignment(['YES', 'PARTIAL', 'PARTIAL'])
        self.assertEqual(step_result, 'YES')

    def test_functional_element_assignment_sufficient(self):
        """Test that we can assign the functional evidence with sufficient steps correctly."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['NO', 'PARTIAL', 'PARTIAL'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'YES')

    def test_functional_element_assignment_sufficient_two(self):
        """Test that we can assign the functional evidence with sufficient steps correctly."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['NO', 'NO', 'NO'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'NO')

    def test_functional_element_assignment_sufficient_three(self):
        """Test that we can assign the functional evidence with sufficient steps correctly."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['NO'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'NO')

    def test_functional_element_assignment_sufficient_four(self):
        """Test that we can assign the functional evidence with sufficient steps correctly."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['YES'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'YES')

    def test_functional_element_assignment_sufficient_five(self):
        """Test that we can assign the functional evidence with sufficient steps correctly."""

        functional_element_evidence = calculate_step_or_functional_element_assignment(['PARTIAL'],
                                                                                      sufficient_scheme=True)
        self.assertEqual(functional_element_evidence, 'YES')

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
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1), 'YES')
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
        identifiers = test_cache.genome_property_identifiers
        identifiers.sort()

        self.assertEqual(identifiers, ['GenProp0067', 'GenProp0092'])

    def test_assign_evidence_from_no_interpro_identifiers(self):
        """Assigns evidence based if no InterPro identifiers are in the assignment cache."""

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
        """Assigns evidence based on InterPro identifiers in the assignment cache."""

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

    def test_assign_evidence_missing_interpro_identifiers(self):
        """Assigns evidence based on InterPro identifiers missing from the assignment cache."""

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

    def test_assign_functional_element(self):
        """Test assignment of functional element."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03114', 'TIGR03117', 'TIGR03120'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('EV', 'IPR017547; TIGR03117;'),
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'YES')

    def test_assign_functional_element_two(self):
        """Test assignment of functional element."""

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

    def test_assign_functional_element_three(self):
        """Test assignment of functional element."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03115', 'TIGR03117', 'TIGR03120'])

        functional_element = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),  # NO
            ('EV', 'IPR017547; TIGR03117; sufficient;'),  # YES
            ('TG', 'GO:0043571;'),
            ('EV', 'IPR017552; TIGR03120;'),  # YES
            ('TG', 'GO:0043573;')
        ]

        parsed_functional_element = parse_functional_elements(functional_element)[0]

        assignment = assign_functional_element(test_cache, parsed_functional_element)

        self.assertEqual(assignment, 'YES')

    def test_assign_functional_element_four(self):
        """Test assignment of functional element."""

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

    def test_assign_functional_element_five(self):
        """Test assignment of functional element."""

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

    def test_assign_step_multiple_functional_elements(self):
        """Test assignment of step."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03114'])
        parent_genome_property = GenomeProperty(accession_id='GenProp0065', name='YOLO', property_type="TEMP")

        step = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03114;'),
            ('TG', 'GO:0043571;'),
            ('ID', 'Yolo subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03115;'),
            ('TG', 'GO:0043571;')
        ]

        parsed_step = parse_steps(step)[0]
        parsed_step.parent = parent_genome_property

        step_assignment = assign_step(test_cache, parsed_step)

        self.assertEqual(step_assignment, 'YES')
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1), 'YES')

    def test_assign_step_multiple_functional_elements_two(self):
        """Test assignment of step."""

        test_cache = AssignmentCache()
        parent_genome_property = GenomeProperty(accession_id='GenProp0065', name='YOLO', property_type="TEMP")

        step = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03114;'),
            ('TG', 'GO:0043571;'),
            ('ID', 'Yolo subtype specific proteins'),
            ('EV', 'IPR017545; TIGR03115;'),
            ('TG', 'GO:0043571;')
        ]

        parsed_step = parse_steps(step)[0]
        parsed_step.parent = parent_genome_property

        step_assignment = assign_step(test_cache, parsed_step)

        self.assertEqual(step_assignment, 'NO')
        self.assertEqual(test_cache.get_step_assignment('GenProp0065', 1), 'NO')

    def test_genome_property_assignment_non_required(self):
        """Test assignment of genome properties."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03564', 'TIGR03565'])
        test_property = self.tree.root

        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'YES')

    def test_genome_property_assignment_non_required_two(self):
        """Test assignment of genome properties."""

        test_cache = AssignmentCache(interpro_member_database_identifiers=['TIGR03565'])
        test_property = self.tree.root

        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'PARTIAL')

    def test_genome_property_assignment_non_required_three(self):
        """Test assignment of genome properties."""

        test_cache = AssignmentCache()
        test_property = self.tree.root

        assignment = assign_genome_property(test_cache, test_property)

        self.assertEqual(assignment, 'NO')

    def test_genome_property_assignment_required(self):
        """Test assignment of genome properties when some are required."""

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

    def test_genome_property_assignment_required_two(self):
        """Test assignment of genome properties when some are required."""

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

    def test_genome_property_assignment_required_three(self):
        """Test assignment of genome properties when some are required."""

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

    def test_genome_property_assignment_required_four(self):
        """Test assignment of genome properties when some are required."""

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
