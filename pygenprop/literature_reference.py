#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The literature reference class.
"""


class LiteratureReference(object):
    """A class representing a literature reference supporting the existence of a genome property."""

    def __init__(self, number, pubmed_id, title, authors, journal):
        """
        Creates a Reference object.

        :param number: The position of the reference.
        :param pubmed_id: The PubMed identify of the literature reference.
        :param title: The title of the literature reference.
        :param authors: The author list of the literature reference.
        :param journal: A journal for the literature reference.
        """
        self.number = int(number)
        self.pubmed_id = int(pubmed_id)
        self.title = title
        self.authors = authors
        self.journal = journal

    @property
    def citation(self):
        """
        Creates a bibliographic style citation for the reference.
        :return: A formatted text citation.
        """
        return "{0} {1} {2} PMID: {3}".format(self.authors, self.title, self.journal, self.pubmed_id)

    def __repr__(self):
        repr_data = ['Ref ' + str(self.number),
                     'Pubmed ID: ' + str(self.pubmed_id),
                     'Title: ' + str(self.title),
                     'Authors: ' + str(self.authors),
                     'Journal: ' + str(self.journal)]
        return ', '.join(repr_data)
