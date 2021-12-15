#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A simple unittest for testing the literature reference module.
"""

import unittest
from pygenprop.database_file_parser import parse_literature_references


class TestLiteratureReference(unittest.TestCase):
    """A unit testing class for testing the literature_reference.py module. To be called by nosetests."""

    def test_parse_literature_reference(self):
        """Test that literature reference rows can be parsed."""
        literature_reference = [
            ('TH', '1'),
            ('RN', '[1]'),
            ('RM', '11952905'),
            ('RT', 'Identification of genes that are associated with DNA repeats.'),
            ('RA', 'Jansen R, Embden JD, Gaastra W, Schouls LM;'),
            ('RL', 'Mol Microbiol. 2002;43:1565-1575.'),
            ('CC', 'CRISPR repeats are by definition Clustered Regularly')
        ]

        reference = parse_literature_references(literature_reference)

        self.assertEqual(len(reference), 1)
        first_reference = reference[0]
        self.assertEqual(first_reference.number, 1)
        self.assertEqual(first_reference.pubmed_id, 11952905)
        self.assertEqual(first_reference.title, 'Identification of genes that are associated with DNA repeats.')
        self.assertEqual(first_reference.authors, 'Jansen R, Embden JD, Gaastra W, Schouls LM;')
        self.assertEqual(first_reference.journal, 'Mol Microbiol. 2002;43:1565-1575.')

    def test_parse_multiple_database_references(self):
        """Test that literature reference rows consisting of multiple references can be parsed."""
        literature_references = [
            ('TH', '1'),
            ('RN', '[1]'),
            ('RM', '11952905'),
            ('RT', 'Identification of genes that are associated with DNA repeats in prokaryotes.'),
            ('RA', 'Jansen R, Embden JD, Gaastra W, Schouls LM;'),
            ('RL', 'Mol Microbiol. 2002;43:1565-1575.'),
            ('RN', '[2]'),
            ('RM', '16292354'),
            ('RT', 'A guild of 45 CRISPR-associated (Cas) protein families.'),
            ('RA', 'Haft DH, Selengut J, Mongodin EF, Nelson KE;'),
            ('RL', 'PLoS Comput Biol. 2005;1:e60.'),
            ('CC', 'CRISPR repeats are by definition Clustered Regularly Interspaced Short')
        ]

        references = parse_literature_references(literature_references)

        self.assertEqual(len(references), 2)
