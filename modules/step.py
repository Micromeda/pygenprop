#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The step class.
"""


class Step(object):
    """A class representing a step that supports the existence of a genome property."""

    def __init__(self, number, functional_elements=None):
        """
        Creates a new Step object.
        :param number: The position of the step in the step list.
        :param functional_elements: A list of FunctionalElements supporting this step.
        """

        if functional_elements is None:
            functional_elements = []

        self.number = int(number)
        self.functional_elements = functional_elements

    def __repr__(self):
        repr_data = ['Step ' + str(self.number),
                     'Functional_Elements: ' + str(self.functional_elements)]
        return ', '.join(repr_data)

    @property
    def required(self):
        """
        Checks if the step is required by checking if any of the functional elements are required.
        :return: True if the step is required.
        """
        required_step = False

        for element in self.functional_elements:
            if element.required:
                required_step = True
                break

        return required_step

    @property
    def genome_property_identifiers(self):
        """
        Collects all the genome properties identifiers supporting a step.
        :return:
        """
        genome_properties_identifiers = []
        for element in self.functional_elements:
            for evidence in element.evidence:
                if evidence.has_genome_property:
                    genome_properties_identifiers.extend(evidence.genome_property_identifiers)

        return genome_properties_identifiers
