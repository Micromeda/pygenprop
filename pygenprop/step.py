#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The step class.
"""

from pygenprop.genome_property import GenomeProperty


class Step(object):
    """A class representing a step that supports the existence of a genome property."""

    def __init__(self, number, functional_elements: list=None, parent: GenomeProperty=None):
        """
        Creates a new Step object.

        :param number: The position of the step in the step list.
        :param functional_elements: A list of FunctionalElements supporting this step.
        """

        if functional_elements is None:
            functional_elements = []
        else:
            # Double link functional_elements back to the parent step.
            for element in functional_elements:
                element.parent = self

        self.number = int(number)
        self.functional_elements = functional_elements
        self.parent = parent

    def __repr__(self):
        repr_data = ['Step ' + str(self.number),
                     'Functional_Elements: ' + str(self.functional_elements)]
        return ', '.join(repr_data)

    @property
    def name(self):
        """
        Get the name for a step based on combine the names of its functional elements.

        :return: The name of the step.
        """
        return " ".join(element.name for element in self.functional_elements)

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

        :return: A list of the steps child genome property identifiers.
        """
        genome_properties_identifiers = []
        for element in self.functional_elements:
            for evidence in element.evidence:
                if evidence.has_genome_property:
                    genome_properties_identifiers.extend(evidence.genome_property_identifiers)

        return genome_properties_identifiers

    @property
    def genome_properties(self):
        """
        Collects all the child genome properties supporting a step.

        :return: A list of child genome properties for a step.
        """
        child_identifiers = self.genome_property_identifiers
        return [child_property for child_property in self.parent.children if child_property.id in child_identifiers]
