#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The functional element class.
"""

from modules.evidence import parse_evidence

class FunctionalElement(object):
    """A functional element (enzyme, structural component or sub-genome property) that can carry out a functional_element."""

    def __init__(self, identifier, name, evidence=None, required=False):
        """
        Creates a new FunctionalElement object.
        :param identifier: The identifier of the FunctionalElement.
        :param name: The name of the FunctionalElement.
        :param evidence: A list of Evidence objects supporting this FunctionalElement.
        :param required: Is this a required FunctionalElement for this functional_element?
        """

        if evidence is None:
            evidence = set
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
        return ', '.join(repr_data)


def parse_functional_element(genome_property_record):
    """
    Parses functional_elements from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of functional_element objects.
    """
    functional_element_markers = ('ID', 'DN', 'RQ')
    functional_elements = []
    current_functional_element = {}

    evidence_markers = ('EV', 'TG')
    current_evidence = []

    for marker, content in genome_property_record:
        if marker in functional_element_markers:
            if marker in current_functional_element:
                evidence = parse_evidence(current_evidence)
                evidence_markers = []

                functional_elements.append(FunctionalElement(identifier=current_functional_element.get('ID'),
                                                             name=current_functional_element.get('DN'),
                                                             evidence=evidence))
                if marker == 'ID':
                    content = int(content)
                current_functional_element = {marker, content}
            else:
                if marker == 'ID':
                    content = int(content)
                elif marker == 'RQ':  # Required should true marker is 1.
                    if int(content) == 1:
                        content = True
                    else:
                        content = False

                current_functional_element[marker] = content

        elif marker in evidence_markers:
            current_evidence.append((marker, content))
        else:
            continue  # Move on if marker is not a functional element marker or evidence marker.

    evidence = parse_evidence(current_evidence)
    functional_elements.append(FunctionalElement(identifier=current_functional_element.get('ID'),
                                                 name=current_functional_element.get('DN'),
                                                 evidence=evidence))

    return functional_elements
