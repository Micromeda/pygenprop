#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The evidence class.
"""


class Evidence(object):
    """A piece of evidence (ex. InterPro HMM hit or GenProp) that supports the existence of a functional element."""

    def __init__(self, evidence_identifiers=None, gene_ontology_terms=None, sufficient=False):
        """
        Creates a new Evidence object.
        :param evidence_identifiers: A list of identifiers of proteins or processes supporting the existence of a
                                     FunctionalElement (i.e a list of Intro Consortium IDs or GenProp Accessions).
        :param gene_ontology_terms: The ids for gene ontology (GO) terms defining the protein or process supporting
                                    the existence of a FunctionalElement.
        :param sufficient: Can this evidence alone prove the existence of FunctionalElement?
        """

        if evidence_identifiers is None:
            evidence_identifiers = []
        if gene_ontology_terms is None:
            gene_ontology_terms = []
        if sufficient is None:
            sufficient = False

        self.evidence_identifiers = evidence_identifiers
        self.gene_ontology_terms = gene_ontology_terms
        self.sufficient = sufficient

    def __repr__(self):
        repr_data = ['Evidence_IDs: ' + str(self.evidence_identifiers),
                     'GO Terms: ' + str(self.gene_ontology_terms),
                     'Sufficient: ' + str(self.sufficient)]
        return '(' + ', '.join(repr_data) + ')'

    @property
    def has_genome_property(self):
        """
        Is the evidence a genome property?
        :return: Return True if evidence is a genome property.
        """
        genome_property = False
        for identifier in self.evidence_identifiers:
            if "genprop" in identifier.lower():
                genome_property = True
                break
        return genome_property

    @property
    def genome_property_identifiers(self):
        """
        Gets genome properties identifiers for representing a piece of evidence.
        :return: A list of genome properties.
        """
        genome_property_identifiers = []
        for identifier in self.evidence_identifiers:
            if "genprop" in identifier.lower():
                genome_property_identifiers.append(identifier)

        return genome_property_identifiers
