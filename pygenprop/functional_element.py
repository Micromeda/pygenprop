#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The functional element class.
"""
from pygenprop.step import Step

import re

EC_REGEX = re.compile('[0-9]+[.][0-9-]+[.][0-9-]+[.][0-9-]+')


class FunctionalElement(object):
    """A functional element (enzyme, structural component or sub-genome property) that can carry out a step."""

    def __init__(self, identifier, name, evidence: list = None, required=False, parent: Step = None):
        """
        Creates a new FunctionalElement object.

        :param identifier: The identifier of the FunctionalElement.
        :param name: The name of the FunctionalElement.
        :param evidence: A list of Evidence objects supporting this FunctionalElement.
        :param required: Is this a required FunctionalElement for this functional_element?
        """

        if evidence is None:
            evidence = []
        else:
            # Double link evidences back to the parent functional element.
            for current_evidence in evidence:
                current_evidence.parent = self

        if required is None:
            required = False
        if name is None:
            name = identifier

        self.id = identifier
        self.name = name
        self.evidence = evidence
        self.required = required
        self.parent = parent

    def __repr__(self):
        repr_data = ['ID: ' + str(self.id),
                     'Name: ' + str(self.name),
                     'Evidences: ' + str(self.evidence),
                     'Required: ' + str(self.required)]
        return '(' + ', '.join(repr_data) + ')'

    @property
    def expasy_enzyme_numbers(self):
        """
        Extracts the expasy enzyme numbers from the elements name.
        :return: A list of EC numbers
        """
        ec_numbers = EC_REGEX.findall(self.name)

        return ec_numbers
