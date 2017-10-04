#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The step class.
"""


class Step(object):
    """A class representing a step that supports the existence of a genome property."""
    def __init__(self, number, identifier, name, gene_ontology_id=None, evidence=None, required=False,
                 sufficient=False):
        """
        Creates a new Step object.
        :param number: The position of the step in the step list.
        :param identifier: The identifier of the step.
        :param name: The name of the step.
        :param evidence: A list of identifiers of proteins or processes supporting this step
                        (i.e a list of Intro Consortium IDs or GenProp Accessions).
        :param gene_ontology_id: The id for gene ontology (GO) term of the protein supporting this step.
        :param required: Is this a required step for this genome property?
        :param sufficient: IS this step sufficient? (TODO: figure out what this means?)
        """
        if evidence is None:
            evidence = []

        self.number = int(number)
        self.id = identifier
        self.name = name
        self.evidence = evidence
        self.gene_ontology_id = gene_ontology_id
        self.required = required
        self.sufficient = sufficient

    def __repr__(self):
        repr_data = ['Step ' + str(self.number),
                     'ID: ' + str(self.id),
                     'Name: ' + str(self.name),
                     'Evidences: ' + str(self.evidence),
                     'Gene Ontology IDs: ' + str(self.gene_ontology_id),
                     'Required: ' + str(self.required),
                     'Sufficient: ' + str(self.sufficient)]
        return ', '.join(repr_data)
