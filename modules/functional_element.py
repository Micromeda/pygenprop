#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The functional element class.
"""


class FunctionalElement(object):
    """A functional element (enzyme, structural component or sub-genome property) that can carry out a step."""

    def __init__(self, identifier, name, evidence=None, required=False):
        """
        Creates a new FunctionalElement object.
        :param identifier: The identifier of the FunctionalElement.
        :param name: The name of the FunctionalElement.
        :param evidence: A list of Evidence objects supporting this FunctionalElement.
        :param required: Is this a required FunctionalElement for this functional_element?
        """

        if evidence is None:
            evidence = []
        if required is None:
            required = False

        self.id = identifier
        self.name = name
        self.evidence = evidence
        self.required = required

    def __repr__(self):
        repr_data = ['ID: ' + str(self.id),
                     'Name: ' + str(self.name),
                     'Evidences: ' + str(self.evidence),
                     'Required: ' + str(self.required)]
        return '(' + ', '.join(repr_data) + ')'
