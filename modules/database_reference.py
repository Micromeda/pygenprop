#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The database reference class.
"""


class DatabaseReference(object):
    """A class representing an external database reference for a genome property."""

    def __init__(self, database_name, record_title, record_ids):
        """
        Creates a new DatabaseReference object.
        :param database_name: The name of the database in question.
        :param record_title: The title of the record of the genome property in the database.
        :param record_ids: One or more database identifiers of the record of the genome property in the database.
        """
        self.database_name = database_name
        self.record_title = record_title
        self.record_ids = record_ids

    def __repr__(self):
        repr_data = ['Title: ' + str(self.record_title),
                     'DB_Name: ' + str(self.database_name),
                     'DB_Records: ' + str(self.record_ids)]
        return ', '.join(repr_data)


def parse_database_references(genome_property_record):
    """
    Parses database reference from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of DatabaseReference objects.
    """
    database_reference_markers = ['DC', 'DR']

    database_references = []
    current_database_reference = {}
    for marker, content in genome_property_record:
        if marker in database_reference_markers:
            if marker in current_database_reference:
                database_references.append(DatabaseReference(record_title=current_database_reference.get('DC'),
                                                             database_name=current_database_reference.get('DN'),
                                                             record_ids=current_database_reference.get('DI')))

                current_database_reference = {marker: content}
            else:
                if marker == 'DR':
                    split_content = filter(None, content.split(';'))
                    cleaned_content = list(map(lambda evidence: evidence.strip(), split_content))
                    database_name = cleaned_content[0]
                    database_records = cleaned_content[1:]
                    current_database_reference['DN'] = database_name
                    current_database_reference['DI'] = database_records

                current_database_reference[marker] = content

    database_references.append(DatabaseReference(record_title=current_database_reference.get('DC'),
                                                 database_name=current_database_reference.get('DN'),
                                                 record_ids=current_database_reference.get('DI')))
    return database_references
