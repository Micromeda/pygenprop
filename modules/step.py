#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The step class.
"""

from modules.functional_element import parse_functional_elements


class Step(object):
    """A class representing a step that supports the existence of a genome property."""

    def __init__(self, number, functional_elements=None):
        """
        Creates a new Step object.
        :param number: The position of the step in the step list.
        :param functional_elements: A list of FunctionalElements supporting this step.
        """

        if functional_elements is None:
            functional_elements = set

        self.number = int(number)
        self.functional_elements = functional_elements

    def __repr__(self):
        repr_data = ['Step ' + str(self.number),
                     'Evidences: ' + str(self.functional_elements)]
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


def parse_steps(genome_property_record):
    """
    Parses steps from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of Step objects.
    """
    step_markers = ('SN', 'ID', 'DN', 'RQ', 'EV', 'TG')
    steps = []
    current_step_markers = []
    step_number = 0
    for marker, content in genome_property_record:
        if marker in step_markers:
            if not marker == 'SN':
                current_step_markers.append((marker, content))
            else:
                if current_step_markers:
                    functional_elements = parse_functional_elements(current_step_markers)
                    steps.append(Step(number=step_number, functional_elements=functional_elements))
                    current_step_markers = []
                    step_number = int(content)
                else:
                    step_number = int(content)

    functional_elements = parse_functional_elements(current_step_markers)
    steps.append(Step(number=step_number, functional_elements=functional_elements))

    return steps
