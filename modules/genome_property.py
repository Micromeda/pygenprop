#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The genome property class.
"""
from modules.database_reference import parse_database_references
from modules.literature_reference import parse_literature_references
from modules.step import parse_steps


class GenomeProperty(object):
    """
    Represents a EBI Interpro genome property. Each represents specific capabilities of an
    organism as proven by the presence of genes found in its genome.
    """

    def __init__(self, accession_id, name, property_type, threshold=0,
                 parent=None, references=None, databases=None, steps=None,
                 public=False, description=None, private_notes=None):
        """
        Creates a new GenomeProperty object.
        :param accession_id: The genome property accession (i.e. "GenProp00286").
        :param name: The name of the genome property.
        :param property_type: The type of genome property (ex. "METAPATH").
        :param threshold: Is a threshold that the number of required steps must exceed.
        :param parent: The parent genome property of the current genome property (parent accession or direct link).
        :param references: A list of reference objects which help support the existence of the property.
        :param databases: A list of database objects which represent database entries related to the property.
        :param steps: A list of step objects that are part of the property.
        :param public: Boolean detailing if the genome property should be public.
        :param description: A detailed description of the genome property.
        :param private_notes: Private notes about the property a potential problems with it.
        """
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
        self.parent = parent
        self.steps = steps
        self.public = public
        self.description = description
        self.private_notes = private_notes

    def __repr__(self):
        has_references = False
        has_steps = False
        has_databases = False

        if self.references:
            has_references = True

        if self.steps:
            has_steps = True

        if self.databases:
            has_databases = True

        repr_data = [str(self.id),
                     'Type: ' + str(self.type),
                     'Name: ' + str(self.name),
                     'Thresh: ' + str(self.threshold),
                     'References: ' + str(has_references),
                     'Databases: ' + str(self.type),
                     'Steps: ' + str(has_steps),
                     'Parent: ' + str(has_databases),
                     'Public: ' + str(self.public)]

        return ', '.join(repr_data)


def parse_genome_property(genome_property_record):
    """
    Parses a single genome property from a genome property record.
    :param genome_property_record:  A list of marker, content tuples representing genome property flat file lines.
    :return: A single genome property object.
    """
    # A list of record markers related to the genome property.
    core_genome_property_markers = ['AC', 'DE', 'TP', 'TH', 'PN', 'CC', '**']
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
        elif marker == 'SN':
            if not step_index:
                step_index = current_index
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
                                         parent=gathered_core_genome_property_markers.get('PN'),
                                         description=gathered_core_genome_property_markers.get('CC'),
                                         private_notes=gathered_core_genome_property_markers.get('**'),
                                         references=references,
                                         databases=databases,
                                         steps=steps)
    return new_genome_property
