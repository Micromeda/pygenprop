#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: A simple unittest for testing the results module.
"""

import unittest
from sqlalchemy import create_engine

from io import StringIO
from pygenprop.assignment_file_parser import parse_interproscan_file_and_fasta_file
from pygenprop.database_file_parser import parse_genome_properties_flat_file
from pygenprop.results import GenomePropertiesResultsWithMatches, load_assignment_caches_from_database_with_matches, \
    load_results_from_serialization


class TestResults(unittest.TestCase):
    """A unit testing class for testing the results.py module. To be called by nosetests."""

    @classmethod
    def setUpClass(cls):
        """Set up testing data for testing."""

        with open('pygenprop/testing/test_constants/C_chlorochromatii_CaD3.faa') as fasta_one:
            with open('pygenprop/testing/test_constants/C_chlorochromatii_CaD3.tsv') as assignment_file_one:
                properties_one = parse_interproscan_file_and_fasta_file(assignment_file_one, fasta_file=fasta_one)

        with open('pygenprop/testing/test_constants/C_luteolum_DSM_273.faa') as fasta_two:
            with open('pygenprop/testing/test_constants/C_luteolum_DSM_273.tsv') as assignment_file_two:
                properties_two = parse_interproscan_file_and_fasta_file(assignment_file_two, fasta_file=fasta_two)

        with open('pygenprop/testing/test_constants/test_genome_properties_two.txt') as test_genome_properties_file:
            genome_properties_tree = parse_genome_properties_flat_file(test_genome_properties_file)

        cls.test_genome_property_results = [properties_one, properties_two]
        cls.test_tree = genome_properties_tree

        cls.engine = create_engine('sqlite://')

    def test_get_matches(self):
        """Test that we can get matches that support the existence of steps."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results, properties_tree=self.test_tree)

        self.assertEqual(len(
            results.step_matches.reset_index()[['Property_Identifier', 'Step_Number']].drop_duplicates()), 1)
        self.assertEqual(len(results.get_sample_matches('C_chlorochromatii_CaD3')), 5)
        self.assertEqual(len(results.get_sample_matches('C_luteolum_DSM_273')), 4)

        self.assertEqual(results.get_sample_matches('Your moms house'), None)

    def test_get_top_step_matches(self):
        """Test that we can get top matches that support the existence of steps."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results, properties_tree=self.test_tree)

        self.assertEqual(len(results._top_step_matches), 2)

        cad3_top_matches = results.get_sample_matches('C_chlorochromatii_CaD3', top=True)
        dsm_273_top_matches = results.get_sample_matches('C_luteolum_DSM_273', top=True)

        self.assertEqual(len(cad3_top_matches), 1)
        self.assertEqual(len(dsm_273_top_matches), 1)

        self.assertEqual(cad3_top_matches['Protein_Accession'].tolist()[0], 'NC_007514.1_940')
        self.assertEqual(dsm_273_top_matches['Protein_Accession'].tolist()[0], 'NC_007512.1_1088')

    def test_get_property_matches(self):
        """Test that we can get matches that support the existence of a property."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results, properties_tree=self.test_tree)

        self.assertEqual(results.get_property_matches('GenProp0236'), None)
        self.assertEqual(len(results.get_property_matches('GenProp0232')), 9)
        self.assertEqual(len(results.get_property_matches('GenProp0232', top=True)), 2)
        self.assertEqual(len(results.get_property_matches('GenProp0232', sample='C_luteolum_DSM_273')), 4)

    def test_get_step_matches(self):
        """Test that we can get matches that support the existence of specific steps."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results, properties_tree=self.test_tree)

        self.assertEqual(results.get_step_matches('None', 1), None)
        self.assertEqual(results.get_step_matches('GenProp0232', 1), None)
        self.assertEqual(len(results.get_step_matches('GenProp0232', 4)), 9)

    def test_write_fasta(self):
        """Test writing a FASTA file."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results, properties_tree=self.test_tree)

        test_one = StringIO()
        results.write_supporting_proteins_for_step_fasta(test_one, 'GenProp0232', 4)
        first_identifiers = self.get_fasta_identifiers(test_one)
        self.assertEqual(len(results.get_step_matches('GenProp0232', 4)), len(first_identifiers))

        test_two = StringIO()
        results.write_supporting_proteins_for_step_fasta(test_two, 'GenProp0232', 4, top=True)
        first_identifiers = self.get_fasta_identifiers(test_two)
        self.assertEqual(len(results.get_step_matches('GenProp0232', 4, top=True)), len(first_identifiers))

        with self.assertRaises(KeyError):
            results.write_supporting_proteins_for_step_fasta(test_two, 'NO', 'NO')

        with self.assertRaises(KeyError):
            results.write_supporting_proteins_for_step_fasta(test_two, 'GenProp0232', 5)

    @staticmethod
    def get_fasta_identifiers(fasta_handle):
        """
        Gets the identifiers from each sequence of a FASTA file.

        :param fasta_handle: A FASTA file handle.
        :return: A list of FASTA file sequence identifiers.
        """
        fasta_handle.seek(0)
        current_identifiers = []
        for line in fasta_handle:
            if '>' in line:
                current_id = line.split('>')[1].strip()
                current_identifiers.append(current_id)
        return current_identifiers

    def test_save_assignment_file(self):
        """Test that we can save an SQLite assignment file."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results, properties_tree=self.test_tree)

        engine = self.engine
        results.to_assignment_database(engine)

        assignment_caches = load_assignment_caches_from_database_with_matches(engine)
        new_results = GenomePropertiesResultsWithMatches(*assignment_caches, properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, new_results.sample_names)
        self.assertEqual(results.property_results.equals(new_results.property_results), True)
        self.assertEqual(results.step_results.equals(new_results.step_results), True)
        self.assertEqual(results.step_matches.equals(new_results.step_matches), True)

    def test_save_serialization(self):
        """Test that we can serialize."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results,
                                                     properties_tree=self.test_tree)

        serialization = results.to_serialization()

        new_results = load_results_from_serialization(serialized_results=serialization, properties_tree=self.test_tree)

        self.assertEqual(results.sample_names, new_results.sample_names)
        self.assertEqual(results.property_results.equals(new_results.property_results), True)
        self.assertEqual(results.step_results.equals(new_results.step_results), True)
        self.assertEqual(results.step_matches.equals(new_results.step_matches), True)
        self.assertIsInstance(new_results, GenomePropertiesResultsWithMatches)

    def test_generate_json_tree(self):
        """Test that a JSON tree can be built."""

        results = GenomePropertiesResultsWithMatches(*self.test_genome_property_results,
                                                     properties_tree=self.test_tree)
        json = results.to_json()

        self.assertIsNotNone(json)
