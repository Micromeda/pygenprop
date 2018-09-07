#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The genome property class.
"""

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
            child_genome_properties_identifiers.extend(step.genome_property_identifiers)

        return child_genome_properties_identifiers

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
