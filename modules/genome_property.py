#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The genome property class.
"""

from modules.database_reference import parse_database_references
from modules.literature_reference import parse_literature_references
from modules.step import parse_steps
import json


class GenomeProperty(object):
    """
    Represents a EBI Interpro genome property. Each represents specific capabilities of an
    organism as proven by the presence of genes found in its genome.
    """

    def __init__(self, accession_id, name, property_type, threshold=0,
                 parents=None, children=None, references=None, databases=None,
                 steps=None, public=False, description=None, private_notes=None):
        """
        Creates a new GenomeProperty object.
        :param accession_id: The genome property accession (i.e. "GenProp00286").
        :param name: The name of the genome property.
        :param property_type: The type of genome property (ex. "METAPATH").
        :param threshold: Is a threshold that the number of required steps must exceed.
        :param parents: The parent genome property of the current genome property (parent accession or direct link).
        :param references: A list of reference objects which help support the existence of the property.
        :param databases: A list of database objects which represent database entries related to the property.
        :param steps: A list of step objects that are part of the property.
        :param public: Boolean detailing if the genome property should be public.
        :param description: A detailed description of the genome property.
        :param private_notes: Private notes about the property a potential problems with it.
        """
        if children is None:
            children = []
        if parents is None:
            parents = []
        if steps is None:
            steps = []
        if databases is None:
            databases = []
        if references is None:
            references = []

        self.id = accession_id
        self.name = name
        self.type = property_type
        self.threshold = threshold
        self.references = references
        self.databases = databases
        self.parents = parents
        self.children = children
        self.steps = steps
        self.public = public
        self.description = description
        self.private_notes = private_notes

    def __repr__(self):
        has_references = False
        has_steps = False
        has_databases = False
        has_parents = False
        has_children = False

        if self.references:
            has_references = True

        if self.steps:
            has_steps = True

        if self.databases:
            has_databases = True

        if self.parents:
            has_parents = True

        if self.children:
            has_children = True

        repr_data = [str(self.id),
                     'Type: ' + str(self.type),
                     'Name: ' + str(self.name),
                     'Thresh: ' + str(self.threshold),
                     'References: ' + str(has_references),
                     'Databases: ' + str(has_databases),
                     'Steps: ' + str(has_steps),
                     'Parents: ' + str(has_parents),
                     'Children: ' + str(has_children),
                     'Public: ' + str(self.public)]

        return ', '.join(repr_data)

    @property
    def child_genome_property_identifiers(self):
        """
        Collects the genome property identifiers of child genome properties.
        :return: A list of genome property identifiers.
        """
        child_genome_properties_identifiers = []

        for step in self.steps:
            for element in step.functional_elements:
                for evidence in element.evidence:
                    if evidence.has_genome_property:
                        child_genome_properties_identifiers.extend(evidence.genome_property_identifiers)

        return child_genome_properties_identifiers

    def add_child_connections(self, genome_properties_dict):
        """
        Adds child genome properties.
        :param genome_properties_dict: A dictionary of genome property ids / genome property object pairs.
        """
        child_identifiers = self.child_genome_property_identifiers

        for identifier in child_identifiers:
            child_genome_property = genome_properties_dict.get(identifier)

            if child_genome_property:
                self.children.append(child_genome_property)
                child_genome_property.parents.append(self)

    def to_json(self, as_dict=False):
        """
        Converts the object to a JSON representation.
        :param as_dict: Return a dictionary for incorporation into other json objects.
        :return: A JSON formatted string or dictionary representing the object.
        """
        json_dict = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'notes': self.private_notes
        }

        if as_dict:
            output = json_dict
        else:
            output = json.dumps(json_dict)

        return output


def parse_genome_property(genome_property_record):
    """
    Parses a single genome property from a genome property record.
    :param genome_property_record:  A list of marker, content tuples representing genome property flat file lines.
    :return: A single genome property object.
    """
    # A list of record markers related to the genome property.
    core_genome_property_markers = ('AC', 'DE', 'TP', 'TH', 'PN', 'CC', '**')
    gathered_core_genome_property_markers = {}

    reference_index = False
    database_index = False
    step_index = False

    current_index = 0
    for marker, content in genome_property_record:
        if marker == 'RN':
            if not reference_index:
                reference_index = current_index
        elif marker == 'DC':
            if not database_index:
                database_index = current_index
        elif marker == '--':
            step_index = current_index + 1
            break  # If we have reach steps we have covered all core_genome_property_markers and can leave the loop.
        elif marker in core_genome_property_markers:
            if marker == 'TH':
                content = int(content)
            gathered_core_genome_property_markers[marker] = content

        current_index = current_index + 1

    if reference_index:
        if database_index:
            reference_rows = genome_property_record[reference_index:database_index]
        else:
            reference_rows = genome_property_record[reference_index:]

        references = parse_literature_references(reference_rows)
    else:
        references = []

    if database_index:
        if step_index:
            database_rows = genome_property_record[database_index:step_index - 1]
        else:
            database_rows = genome_property_record[database_index:]

        databases = parse_database_references(database_rows)
    else:
        databases = []

    if step_index:
        step_rows = genome_property_record[step_index:]
        steps = parse_steps(step_rows)
    else:
        steps = []

    new_genome_property = GenomeProperty(accession_id=gathered_core_genome_property_markers.get('AC'),
                                         name=gathered_core_genome_property_markers.get('DE'),
                                         property_type=gathered_core_genome_property_markers.get('TP'),
                                         threshold=gathered_core_genome_property_markers.get('TH'),
                                         parents=gathered_core_genome_property_markers.get('PN'),
                                         description=gathered_core_genome_property_markers.get('CC'),
                                         private_notes=gathered_core_genome_property_markers.get('**'),
                                         references=references,
                                         databases=databases,
                                         steps=steps)
    return new_genome_property


def build_genome_property_connections(genome_properties_dict):
    """
    Creates connections between genome properties.
    :param genome_properties_dict: A dictionary of genome property ids / genome property object pairs.
    """
    for genome_property in genome_properties_dict.values():
        genome_property.add_child_connections(genome_properties_dict)
