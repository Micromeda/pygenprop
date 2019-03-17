#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the evidence module.
"""

import unittest

from pygenprop.database_file_parser import parse_evidences, parse_genome_property
from pygenprop.tree import GenomePropertiesTree


class TestEvidence(unittest.TestCase):
    """A unit testing class for testing the evidence.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """Set up testing data for testing."""

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
            ('EV', 'GenProp0089;')
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

        property_one = parse_genome_property(property_rows_one)
        property_two = parse_genome_property(property_rows_two)

        cls.tree = GenomePropertiesTree(property_one, property_two)

    def test_parse_evidence(self):
        """Test that evidence rows can be parsed."""
        evidence = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '0'),
            ('EV', 'IPR017545; TIGR03114; sufficient;'),
            ('TG', 'GO:0043571;')
        ]

        parsed_evidence = parse_evidences(evidence)

        self.assertEqual(len(parsed_evidence), 1)
        first_evidence = parsed_evidence[0]

        self.assertEqual(first_evidence.evidence_identifiers, ['IPR017545', 'TIGR03114'])
        self.assertEqual(first_evidence.gene_ontology_terms, ['GO:0043571'])
        self.assertEqual(first_evidence.sufficient, True)

    def test_parse_evidence_insufficient(self):
        """Test that the evidence rows can be properly parsed if the evidence is insufficient."""
        evidence = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '1'),
            ('EV', 'IPR017545; TIGR03114;'),
            ('TG', 'GO:0043571;')
        ]

        parsed_evidence = parse_evidences(evidence)
        first_evidence = parsed_evidence[0]
        self.assertEqual(first_evidence.sufficient, False)

    def test_parse_evidence_no_go_terms(self):
        """Test that the evidence rows can be properly parsed if the evidence has no go terms."""
        evidence = [
            ('--', ''),
            ('SN', '1'),
            ('ID', 'Aferr subtype specific proteins'),
            ('DN', 'Crispy Proteins'),
            ('RQ', '1'),
            ('EV', 'IPR017545; TIGR03114;'),
        ]

        parsed_evidence = parse_evidences(evidence)
        first_evidence = parsed_evidence[0]
        self.assertEqual(first_evidence.gene_ontology_terms, [])

    def test_parse_multiple_evidences(self):
        """Test that literature reference rows consisting of multiple references can be parsed."""

        evidences = [
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

        parsed_evidences = parse_evidences(evidences)
        first_evidence = parsed_evidences[0]
        second_evidence = parsed_evidences[1]
        third_evidence = parsed_evidences[2]

        self.assertEqual(len(parsed_evidences), 3)
        self.assertEqual(first_evidence.evidence_identifiers, ['IPR017545', 'TIGR03114'])
        self.assertEqual(first_evidence.gene_ontology_terms, [])
        self.assertEqual(second_evidence.evidence_identifiers, ['IPR017547', 'TIGR03117'])
        self.assertEqual(third_evidence.gene_ontology_terms, ['GO:0043573'])

    def test_has_genome_property(self):
        """Test that we can determine that an evidence is a genome property."""

        evidences = [
            ('--', ''),
            ('SN',  '3'),
            ('ID',  'Selfish genetic elements'),
            ('RQ',  '0'),
            ('EV', 'GenProp0066;')
        ]

        evidence = parse_evidences(evidences)[0]
        self.assertEqual(evidence.has_genome_property, True)

    def test_get_genome_property_identifiers(self):
        """Test that we can determine that an evidence is a genome property."""

        evidences = [
            ('--', ''),
            ('SN', '3'),
            ('ID', 'Selfish genetic elements'),
            ('RQ', '0'),
            ('EV', 'GenProp0066; GenProp0067;')
        ]

        evidence = parse_evidences(evidences)[0]
        self.assertEqual(evidence.genome_property_identifiers, ['GenProp0066', 'GenProp0067'])

    def test_get_genome_properties(self):
        """Test that we can get genome properties of an evidence."""

        test_evidence = self.tree.root.steps[0].functional_elements[0].evidence[0]

        self.assertEqual(test_evidence.has_genome_property, True)
        self.assertEqual(test_evidence.genome_property_identifiers, ['GenProp0089'])

        test_child_genome_property = test_evidence.genome_properties[0]

        self.assertEqual(test_child_genome_property.id, 'GenProp0089')
