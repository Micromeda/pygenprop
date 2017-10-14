#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The literature reference class.
"""


class LiteratureReference(object):
    """A class representing a literature reference supporting the existence of a genome property."""

    def __init__(self, number, pubmed_id, title, authors, citation):
        """
        Creates a Reference object.
        :param number: The position of the reference.
        :param pubmed_id: The PubMed identify of the literature reference.
        :param title: The title of the literature reference.
        :param authors: The author list of the literature reference.
        :param citation: A citation for the literature reference.
        """
        self.number = int(number)
        self.pubmed_id = int(pubmed_id)
        self.title = title
        self.authors = authors
        self.citation = citation

    def __repr__(self):
        repr_data = ['Ref ' + str(self.number),
                     'Pubmed ID: ' + str(self.pubmed_id),
                     'Title: ' + str(self.title),
                     'Authors: ' + str(self.authors),
                     'Citation: ' + str(self.citation)]
        return ', '.join(repr_data)


def parse_literature_references(genome_property_record):
    """
    Parses literature references from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of LiteratureReference objects.
    """
    # A list of record markers related to literature references.
    literature_reference_markers = ('RN', 'RM', 'RT', 'RA', 'RL')

    literature_references = []
    current_literature_reference = {}
    for marker, content in genome_property_record:
        if marker in literature_reference_markers:
            if marker in current_literature_reference:
                literature_references.append(LiteratureReference(number=current_literature_reference.get('RN'),
                                                                 pubmed_id=current_literature_reference.get('RM'),
                                                                 title=current_literature_reference.get('RT'),
                                                                 authors=current_literature_reference.get('RA'),
                                                                 citation=current_literature_reference.get('RL')))
                if marker == 'RN':
                    content = int(content.strip('[]'))

                current_literature_reference = {marker: content}
            else:
                if marker == 'RN':
                    content = int(content.strip('[]'))

                current_literature_reference[marker] = content

    literature_references.append(LiteratureReference(number=current_literature_reference.get('RN'),
                                                     pubmed_id=current_literature_reference.get('RM'),
                                                     title=current_literature_reference.get('RT'),
                                                     authors=current_literature_reference.get('RA'),
                                                     citation=current_literature_reference.get('RL')))
    return literature_references
