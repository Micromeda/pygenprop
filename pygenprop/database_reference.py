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
